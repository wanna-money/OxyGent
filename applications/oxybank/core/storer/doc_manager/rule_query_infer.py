"""
Dynamic endpoint generator.

Dynamically generates retrieval endpoints based on match_rules in KBSchema.

Rule constraints:
1. Each retrieval rule can only have one advanced search strategy (es_text or vearch_vector) as the main query
2. Precise search strategies (precise) can appear multiple times for filtering conditions

Query template design:
- Pre-build query template structure when strategy is determined
- Only fill parameter values at runtime, avoiding repeated DSL construction
- Unified query interface supporting multiple search engines (ES, Vearch, etc.)
"""
import datetime
import uuid
from abc import ABC, abstractmethod
from typing import Annotated
from typing import Optional, List, Dict, Any, Type, Union

import pandas as pd
from fastapi import APIRouter, HTTPException, Body, Path
from fastapi.routing import APIRoute
from loguru import logger
from pydantic import Field, create_model, BaseModel, BeforeValidator, ConfigDict
from pydantic.fields import FieldInfo

from core.config import settings
from core.interface.endpoint_show import get_field_type
from core.storer.doc_manager.es_kb_base_manager import ElasticsearchKbBaseManager
from core.storer.doc_manager.es_kb_file_manager import ElasticsearchKbFileManager
from core.storer.doc_manager.knowledge_index import (
    KBSchema, MatchRule, MatchPolicy,
    PreciseMatchPolicy, check_kb_schema, VearchVectorMatchPolicy
)
from core.storer.doc_manager.schema_utils import convert_dataframe_types_by_schema
from core.storer.vector_manager.vearch_manager import VearchManager


class SearchResult(BaseModel):
    """Generic search result with pagination"""
    items: List[dict]
    total: int
    took_ms: float
    page_number: int = Field(..., description="Current page number (starting from 1)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")


# ============================================================================
# Helper Functions
# ============================================================================

def optional_int_with_empty_string(v: Any) -> Optional[int]:
    """Validator to convert empty string to None for Optional[int] fields

    Args:
        v: Input value (could be int, str, or None)

    Returns:
        Integer value or None

    Raises:
        ValueError: If the value is a non-empty string that cannot be converted to int
    """
    if v == "" or v is None:
        return None
    if isinstance(v, str):
        try:
            return int(v)
        except ValueError:
            raise ValueError(f"Must be an integer or empty string, got '{v}'")
    return v


# Create a reusable type alias for Optional[int] that accepts empty strings
OptionalInt = Annotated[Optional[int], BeforeValidator(optional_int_with_empty_string)]


def create_request_model_with_validators(model_name: str, **field_definitions):
    """Create a Pydantic model with empty-string-to-None validators

    This helper function creates a dynamic model and automatically converts
    empty strings to None for Optional[int] fields.

    Args:
        model_name: Name of the model to create
        **field_definitions: Field definitions (name: (type, FieldInfo))

    Returns:
        Dynamically created model class with validators
    """
    # Create modified field definitions
    modified_fields = {}
    for field_name, (field_type, field_info) in field_definitions.items():
        # Check if this is an Optional[int] field
        if (hasattr(field_type, "__origin__") and
            field_type.__origin__ is Union and
            type(None) in field_type.__args__ and
            int in field_type.__args__):
            # Replace with OptionalInt type that handles empty strings
            modified_fields[field_name] = (OptionalInt, field_info)
        else:
            # Keep original field definition
            modified_fields[field_name] = (field_type, field_info)

    # Create and return the model
    return create_model(model_name, **modified_fields)


# ============================================================================
# Query Template Abstract Base Class
# ============================================================================

class BaseQueryTemplate(ABC):
    """Query template abstract base class

    Provides a unified query interface supporting multiple search engines (ES, Vearch, etc.)
    Subclasses must implement the execute method
    """

    def __init__(
        self,
        advanced_search_fields: List[str],
        precise_filter_fields: List[str],
        output_fields: List[str]
    ):
        """
        Initialize query template

        Args:
            advanced_search_fields: List of advanced search fields
            precise_filter_fields: List of precise filter fields
            output_fields: List of output fields
        """
        self.advanced_search_fields = advanced_search_fields
        self.precise_filter_fields = precise_filter_fields
        self.output_fields = output_fields

    @abstractmethod
    async def execute(
        self,
        request_data: Dict[str, Any],
        page_size: int,
        page_number: int,
        **kwargs
    ) -> SearchResult:
        """
        Execute query (abstract method, must be implemented by subclasses)

        Args:
            request_data: Request parameter dictionary
            page_size: Number of items per page
            page_number: Page number (0-indexed)
            **kwargs: Other parameters (e.g., kb_name, etc.)

        Returns:
            SearchResult: Search results with pagination
        """
        pass


class ESQueryTemplate(BaseQueryTemplate):
    """ES query template

    Encapsulates Elasticsearch full-text search logic
    """

    def __init__(
        self,
        advanced_search_fields: List[str],
        precise_filter_fields: List[str],
        output_fields: List[str],
        es_client
    ):
        """
        Initialize ES query template

        Args:
            advanced_search_fields: List of advanced search fields
            precise_filter_fields: List of precise filter fields
            output_fields: List of output fields
            es_client: Elasticsearch client instance
        """
        super().__init__(
            advanced_search_fields=advanced_search_fields,
            precise_filter_fields=precise_filter_fields,
            output_fields=output_fields
        )
        self.es_client = es_client

    def build_query(self, request_data: Dict[str, Any], page_size: int, page_number: int) -> Dict[str, Any]:
        """
        Build ES query DSL with pagination

        Args:
            request_data: Request parameter dictionary
            page_size: Number of items per page
            page_number: Page number (0-indexed)

        Returns:
            ES query DSL
        """
        # Build basic query structure with pagination
        from_val = page_number * page_size
        query = {
            "from": from_val,
            "size": page_size,
            "_source": self.output_fields,
            "query": {
                "bool": {}
            }
        }

        bool_query = query["query"]["bool"]

        # Build must clause (advanced search)
        must_clause = self._build_must_clause(request_data)
        if must_clause:
            bool_query["must"] = [must_clause]

        # Build filter clause (precise filtering)
        filter_clauses = self._build_filter_clauses(request_data)
        if filter_clauses:
            bool_query["filter"] = filter_clauses

        # If bool query is empty, use match_all
        if not bool_query:
            query["query"] = {"match_all": {}}

        return query

    def _build_must_clause(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build must clause (advanced search)

        Args:
            request_data: Request parameter dictionary

        Returns:
            must clause dictionary
        """
        # Only one field, get value directly
        value = request_data.get(self.advanced_search_fields[0])

        if value is None or value == "":
            raise ValueError("Advanced search strategy field cannot be empty when executing query strategy")

        # Use match query
        return {
            "match": {
                self.advanced_search_fields[0]: str(value)
            }
        }

    def _build_filter_clauses(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build filter clause (precise filtering)

        Args:
            request_data: Request parameter dictionary

        Returns:
            filter clause list
        """
        clauses = []

        for field in self.precise_filter_fields:
            filter_field_name = f"filter_{field}"
            value = request_data.get(filter_field_name)

            if value is None:
                continue

            # Use term query uniformly (single-value exact match)
            clauses.append({
                "term": {
                    field: str(value)
                }
            })

        return clauses

    async def execute(
        self,
        request_data: Dict[str, Any],
        page_size: int,
        page_number: int,
        kb_name: str,
        **kwargs
    ) -> SearchResult:
        """
        Execute ES query with pagination

        Args:
            request_data: Request parameter dictionary
            page_size: Number of items per page
            page_number: Page number (0-indexed)
            kb_name: Knowledge base name
            **kwargs: Other parameters

        Returns:
            SearchResult: Search results with pagination
        """
        # Build query
        es_query = self.build_query(request_data, page_size, page_number)

        # Use json.dumps in log output to ensure Chinese characters display correctly (instead of Unicode escape)
        import json
        logger.debug(f"ES Query: {json.dumps(es_query, ensure_ascii=False, indent=2)}")

        # Execute query
        # Elasticsearch Python client automatically handles Unicode strings
        # Ensure all strings in the query dictionary passed to ES are Unicode strings
        response = self.es_client.search(
            index=kb_name,
            body=es_query
        )

        # Parse results
        hits = response.get("hits", {})
        total = hits.get("total", {}).get("value", 0)
        took_ms = response.get("took", 0)

        items = []
        for hit in hits.get("hits", []):
            # _source is already limited by _source field in query DSL, only contains fields specified by output_fields
            item = hit.get("_source", {}).copy()
            # Add ES relevance score
            item["_score"] = hit.get("_score", 0.0)
            items.append(item)

        # Calculate pagination metadata
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        has_next = page_number < total_pages - 1

        # Convert 0-based page to 1-based for user-friendly response
        page_num = page_number + 1

        logger.info(f"✅ ES search completed, returned {len(items)} results, total {total}, page {page_num}/{total_pages}")

        return SearchResult(
            items=items,
            total=total,
            took_ms=took_ms,
            page_number=page_num,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next
        )


class VearchQueryTemplate(BaseQueryTemplate):
    """Vearch query template

    Encapsulates Vearch vector search logic
    """

    def __init__(
        self,
        advanced_search_fields: List[str],
        precise_filter_fields: List[str],
        output_fields: List[str],
        vearch_client,
        embedding_model
    ):
        """
        Initialize Vearch query template

        Args:
            advanced_search_fields: List of advanced search fields
            precise_filter_fields: List of precise filter fields
            output_fields: List of output fields
            vearch_client: Vearch client instance
            embedding_model: Embedding model instance
        """
        super().__init__(
            advanced_search_fields=advanced_search_fields,
            precise_filter_fields=precise_filter_fields,
            output_fields=output_fields
        )
        self.vearch_client = vearch_client
        self.embedding_model = embedding_model

    def build_filter(self, request_data: Dict[str, Any]) -> Optional:
        """
        Build Vearch filter conditions

        Args:
            request_data: Request parameter dictionary

        Returns:
            Vearch Filter object or None
        """
        from vearch.filter import Condition, FieldValue, Filter

        conditions = []

        for field in self.precise_filter_fields:
            filter_field_name = f"filter_{field}"
            value = request_data.get(filter_field_name)

            if value is None:
                continue

            if isinstance(value, (int, float)):
                field_condition = Condition(operator="=", fv=FieldValue(field=field, value=value))
            elif isinstance(value, str):
                field_condition = Condition(operator="IN", fv=FieldValue(field=field, value=[value]))
            else:
                raise ValueError("Value type passed to query interface does not meet requirements, only string, integer, float are supported.")

            # Add exact match condition for current field
            conditions.append(field_condition)

        # If there are filter conditions, create Filter object
        if conditions:
            return Filter(operator="AND", conditions=conditions)

        return None

    async def execute(
        self,
        request_data: Dict[str, Any],
        page_size: int,
        page_number: int,
        kb_name: str,
        **kwargs
    ) -> SearchResult:
        """
        Execute Vearch vector search with pagination

        Args:
            request_data: Request parameter dictionary
            page_size: Number of items per page
            page_number: Page number (0-indexed)
            kb_name: Knowledge base name
            **kwargs: Other parameters

        Returns:
            SearchResult: Search results with pagination
        """
        import numpy as np
        from vearch.utils import VectorInfo

        # Get value of advanced search field
        query_text = request_data.get(self.advanced_search_fields[0])

        if not query_text or query_text == "":
            raise ValueError("Advanced search strategy field cannot be empty when executing query strategy")

        logger.info(f"📝 Query text: {query_text}")

        # Use embedding model to convert text to vector
        try:
            query_vector = self.embedding_model.get_text_embedding(query_text)
            logger.debug(f"✅ Embedding generated successfully, vector dimension: {len(query_vector)}")
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Embedding service exception: {str(e)}")

        # Vector normalization
        query_vector_norm = np.array(query_vector)
        query_vector_norm = query_vector_norm / np.linalg.norm(query_vector_norm)

        # Build VectorInfo object
        # Use dynamically calculated vector field name: field_name + "_vector"
        # For example: if advanced_search_fields = ["name"], then vector_field_name = "name_vector"
        vector_field_name = f"{self.advanced_search_fields[0]}_vector"
        vector_info = VectorInfo(
            field_name=vector_field_name,
            feature=query_vector_norm.tolist()
        )

        # Build filter conditions
        vearch_filter = self.build_filter(request_data)

        # Calculate pagination: Vearch uses limit and offset
        # Note: Vearch may not support offset directly, so we fetch more and skip
        # If page_number=0 and page_size=10, we fetch 10 items (limit=10)
        # If page_number=1 and page_size=10, we need to fetch 20 items and return the last 10
        total_to_fetch = (page_number + 1) * page_size
        offset = page_number * page_size

        # Execute Vearch vector search
        try:
            search_result = self.vearch_client.search(
                database_name=settings.vearch_config.db_name,
                space_name=kb_name,
                vector_infos=[vector_info],
                fields=self.output_fields,
                limit=total_to_fetch,  # Fetch enough items to support pagination
                filter=vearch_filter
            )

            if not search_result.is_success():
                logger.error(f"Vearch search failed: {search_result.msg}")
                raise HTTPException(status_code=500, detail=f"Vearch retrieval failed: {search_result.msg}")

            # Parse results
            items = []
            total = 0
            if search_result.documents and len(search_result.documents) > 0:
                total = len(search_result.documents[0])
                # Apply pagination: skip to offset, take page_size items
                paginated_hits = search_result.documents[0][offset:offset + page_size]
                for hit in paginated_hits:
                    item = {}
                    for field in self.output_fields:
                        item[field] = hit.get(field, "")
                    # Add Vearch similarity score
                    item["_score"] = hit.get("_score", 0.0)
                    items.append(item)

            # Calculate pagination metadata
            total_pages = (total + page_size - 1) // page_size if total > 0 else 0
            has_next = page_number < total_pages - 1

            # Convert 0-based page to 1-based for user-friendly response
            page_num = page_number + 1

            logger.info(f"✅ Vearch search completed, returned {len(items)} results, total {total}, page {page_num}/{total_pages}")

            return SearchResult(
                items=items,
                total=total,
                took_ms=0,  # Vearch does not return took information
                page_number=page_num,
                page_size=page_size,
                total_pages=total_pages,
                has_next=has_next
            )

        except Exception as e:
            logger.error(f"Vearch retrieval exception: {e}")
            raise HTTPException(status_code=500, detail=f"Vearch retrieval service exception: {str(e)}")


# ============================================================================
# Dynamic Endpoint Generator
# ============================================================================

class DynamicEndpointGenerator:
    """Dynamically generate and register retrieval endpoints"""

    def __init__(self, kb_name: str, kb_schema: KBSchema):
        self.kb_name = kb_name
        self.kb_schema = kb_schema
        self.router = APIRouter(prefix=f"/kb/{kb_name}", tags=[f"KB:{kb_name}"])
        # Use passed es_client or get from settings
        self.es_client = settings.es_client
        # Get vearch_client
        self.vearch_client = settings.vearch_client
        # Get embedding model
        self.embedding_model = settings.embedding_model
        # Build field type mapping
        self.field_types = {f.field_name: f.field_type for f in self.kb_schema.fields}
        # Build field description mapping
        self.field_descriptions = {f.field_name: f.field_desc for f in self.kb_schema.fields}
        
        # Query knowledge base description
        self.kb_description = None
        try:
            kb_base_client = ElasticsearchKbBaseManager(self.es_client)
            kb_info_list = kb_base_client.kb_info_search_name(kb_name=kb_name)
            if kb_info_list and len(kb_info_list) > 0:
                kb_info = kb_info_list[0]
                kb_desc = kb_info.get("kb_description", "").strip()
                if kb_desc:
                    self.kb_description = kb_desc
                    logger.info(f"Knowledge base '{kb_name}' description loaded: {kb_desc[:50]}...")
        except Exception as e:
            logger.warning(f"Failed to query knowledge base '{kb_name}' description: {e}, will use default description generation logic")

    def generate_all_endpoints(self) -> APIRouter:
        """Generate corresponding endpoint for each match_rule"""
        # 1. Generate retrieval interfaces based on match_rules
        for idx, match_rule in enumerate(self.kb_schema.match_rules):
            self._generate_search_endpoint(idx, match_rule)

        # 2. Automatically add deposit interface (data write interface)
        self._generate_deposit_endpoint()

        # 3. Automatically add unified search interface (generic search for all fields)
        self._generate_unified_search_endpoint()

        # 4. Automatically add delete interface (delete data by sys_sample_id)
        self._generate_delete_endpoint()

        # 4. Automatically add list_bank interface (list all data in knowledge base)
        @self.router.get(
            "/list_banks",
            summary="List all bank interface information",
            description=f"Return all interface information in bank {self.kb_name}",
            tags=[f"KB:{self.kb_name}"]
        )
        async def list_banks():
            """List all interface information in bank
            
            Returns:
                retrieve and deposit interface information in bank
            """
            from typing import cast
            bank_apis = []

            for route in self.router.routes:
                if route.endpoint.__name__ == "list_banks":
                    continue

                route = cast(APIRoute, route)
                description = route.description
                input_schema = {"type": "object", "properties": {}, "required": []}

                # Extract type from route.path (full path format: /kb/{kb_name}/{type}/...)
                # Example: /kb/hyy_new_structure_1/search/rule_0 -> type is "search" (3rd position, index 3)
                # Example: /kb/hyy_new_structure_1/deposit -> type is "deposit" (3rd position, index 3)
                path_parts = route.path.split("/")
                # path_parts: ['', 'kb', '{kb_name}', '{type}', ...]
                # We want the 3rd position (index 3) which is the type
                endpoint_type = path_parts[3] if len(path_parts) > 3 else "unknown"
                
                # Convert "search" to "retrieve", keep others unchanged
                if endpoint_type == "search":
                    endpoint_type = "retrieve"

                # Only process routes with body_field (POST/PUT requests, etc.)
                if hasattr(route, "body_field") and route.body_field is not None:
                    request_type = route.body_field.type_

                    for field_name, field_type_info in request_type.model_fields.items():
                        field_type_info = cast(FieldInfo, field_type_info)

                        field_type = get_field_type(field_type_info)

                        if field_type is int:
                            t = "integer"
                        elif field_type is float:
                            t = "float"
                        else:
                            t = "string"

                        input_schema["properties"][field_name] = {
                            "type": t,
                            "description": field_type_info.description or "",
                        }

                        if field_type_info.is_required():
                            input_schema["required"].append(field_name)

                bank_apis.append(
                    {
                        "name": route.endpoint.__name__,
                        "endpoint": "/" + "/".join(route.path.split('/')[3:]),
                        "type": endpoint_type,
                        "methods": route.methods,
                        "description": description,
                        "inputSchema": input_schema,
                    }
                )
            return bank_apis

        return self.router

    def _generate_search_endpoint(self, rule_idx: int, match_rule: MatchRule):
        """Generate corresponding endpoint for a single match_rule"""
        # 1. Analyze strategies in match_rule, separate advanced search and precise search
        advanced_policy, precise_policies = self._separate_policies(match_rule)

        # 2. Dynamically generate request model (distinguish advanced search fields and filter fields)
        request_model = self._create_request_model(advanced_policy, precise_policies)

        # 3. Dynamically generate response model
        response_model = self._create_response_model(match_rule)

        # 4. Generate query function
        search_func = self._create_search_function(
            rule_idx=rule_idx,
            match_rule=match_rule,
            advanced_policy=advanced_policy,
            precise_policies=precise_policies,
            request_model=request_model
        )

        # 5. Register to router
        endpoint_path = f"/search/rule_{rule_idx}"
        self.router.add_api_route(
            path=endpoint_path,
            endpoint=search_func,
            methods=["POST"],
            response_model=SearchResult,
            summary=f"Retrieval interface - Rule {rule_idx}",
            description=self._generate_description(advanced_policy, precise_policies, match_rule),
            tags=[f"KB:{self.kb_name}"],
            name=f"{self.kb_name}_search_rule_{rule_idx}",
            # Specify request body model to let FastAPI correctly parse request
            dependencies=[]  # Automatically inferred from function signature
        )

        logger.info(f"✅ Generated endpoint: POST {self.router.prefix}{endpoint_path}")

    def _separate_policies(self, match_rule: MatchRule) -> tuple[MatchPolicy, list[PreciseMatchPolicy]]:
        """Separate advanced search strategies and precise search strategies

        Returns:
            tuple: (advanced search strategy, list of precise search strategies)
        """
        advanced_policy = None
        precise_policies = []

        for policy in match_rule.match_policies:
            if policy.mode in ["es_text", "vearch_vector"]:
                advanced_policy = policy
            elif policy.mode == "precise":
                precise_policies.append(policy)

        return advanced_policy, precise_policies

    def _create_request_model(
            self,
            advanced_policy: MatchPolicy,
            precise_policies: list[PreciseMatchPolicy]
    ):
        """Dynamically create request model

        Field naming rules:
        - Advanced search fields: keep original field name, e.g., name, description
        - Precise search fields: add filter_ prefix, e.g., filter_name, filter_category

        This allows fields with the same name to have different purposes, e.g.:
        - name: for full-text search
        - filter_name: for precise filtering
        """
        endpoint_input_fields = {}

        # 1. Add advanced search fields
        for field_name in advanced_policy.input_fields:
            python_type = self._get_python_type(field_name)
            # Use field description defined in Schema, if not available use default description
            field_desc = self.field_descriptions.get(field_name, field_name)
            endpoint_input_fields[field_name] = (
                python_type,
                Field(..., description=field_desc)
            )

        # 2. Add precise search fields (add filter_ prefix)
        for policy in precise_policies:
            for field_name in policy.input_fields:
                filter_field_name = f"filter_{field_name}"
                python_type = self._get_python_type(field_name)
                # Use field description defined in Schema, if not available use default description
                field_desc = self.field_descriptions.get(field_name, field_name)
                endpoint_input_fields[filter_field_name] = (
                    python_type,
                    Field(..., description=field_desc)
                )

        # 3. Add pagination parameters
        endpoint_input_fields["page_size"] = (int, Field(default=10, ge=1, description="Number of items per page"))
        endpoint_input_fields["page_number"] = (int, Field(default=1, ge=1, description="Page number (starting from 1)"))

        # Dynamically create model with validators
        model_name = f"SearchRequest_{self.kb_name}_Rule{id(advanced_policy)}"
        return create_request_model_with_validators(model_name, **endpoint_input_fields)

    def _create_response_model(self, match_rule: MatchRule):
        """Dynamically create response model"""
        endpoint_output_fields = {}

        for field_name in match_rule.output_fields:
            python_type = self._get_python_type(field_name)
            # Use field description defined in Schema, if not available use field name
            field_desc = self.field_descriptions.get(field_name, field_name)
            endpoint_output_fields[field_name] = (
                Optional[python_type],
                Field(None, description=field_desc)
            )

        model_name = f"SearchResponse_{self.kb_name}_Rule{id(match_rule)}"
        return create_model(model_name, **endpoint_output_fields)

    def _get_python_type(self, field_name: str) -> type:
        """Get corresponding Python type based on field name"""
        field_type = self.field_types.get(field_name, "string")
        if field_type == "integer":
            return int
        elif field_type == "float":
            return float
        else:
            return str

    def _create_deposit_request_model(self):
        """Dynamically create deposit request model based on schema fields

        Creates a Pydantic model that includes:
        - All fields defined in the knowledge base schema (user-defined fields)
        - System default fields (sys_sample_id, sys_group, sys_template, sys_priority, sys_status, sys_executor, sys_overview, sys_remarks)

        Fields accept both their native type and string input for flexibility.

        Returns:
            A Pydantic model class for deposit data items
        """
        deposit_fields = {}

        # Add all user-defined fields from schema with appropriate types
        for field_info in self.kb_schema.fields:
            field_name = field_info.field_name
            field_desc = field_info.field_desc or field_name
            field_type = field_info.field_type

            # Define field type based on schema, allowing string input for flexibility
            if field_type == "integer":
                # Accept int or str (will be converted later)
                deposit_fields[field_name] = (
                    Optional[Union[int, str]],
                    Field(None, description=field_desc)
                )
            elif field_type == "float":
                # Accept float, int, or str (will be converted later)
                deposit_fields[field_name] = (
                    Optional[Union[float, int, str]],
                    Field(None, description=field_desc)
                )
            else:  # string type
                # Accept str or other types (will be converted to string)
                deposit_fields[field_name] = (
                    Optional[Union[str, int, float]],
                    Field(None, description=field_desc)
                )

        # Add system fields (allow flexible input types)
        deposit_fields["sys_sample_id"] = (
            Optional[Union[str, int]],
            Field(None, description="Sample ID (empty for create, filled for update)")
        )
        deposit_fields["sys_group"] = (
            Optional[Union[str, int]],
            Field(None, description="Group identifier")
        )
        deposit_fields["sys_template"] = (
            Optional[Union[str, int]],
            Field(None, description="Template type")
        )
        deposit_fields["sys_priority"] = (
            Optional[Union[int, str]],
            Field(None, description="Priority (1-5)")
        )
        deposit_fields["sys_status"] = (
            Optional[Union[str, int]],
            Field(None, description="Status")
        )
        deposit_fields["sys_executor"] = (
            Optional[Union[str, int]],
            Field(None, description="Executor")
        )
        deposit_fields["sys_overview"] = (
            Optional[Union[str, int]],
            Field(None, description="Overview")
        )
        deposit_fields["sys_remarks"] = (
            Optional[Union[str, int]],
            Field(None, description="Remarks")
        )

        # Dynamically create model
        model_name = f"DepositDataItem_{self.kb_name}"
        return create_model(model_name, **deposit_fields)

    def _create_search_function(
            self,
            rule_idx: int,
            match_rule: MatchRule,
            advanced_policy: MatchPolicy,
            precise_policies: list[PreciseMatchPolicy],
            request_model: Type[BaseModel]
    ):
        """Create actual query function

        Pre-build query template when strategy is determined, only fill values at runtime
        """

        # Use closure to capture required parameters
        kb_name = self.kb_name
        reformat_func = self._reformat_item_with_schema_wrapper

        # Collect field information
        advanced_search_fields = advanced_policy.input_fields
        precise_filter_fields = []
        for policy in precise_policies:
            precise_filter_fields.extend(policy.input_fields)
        output_fields = match_rule.output_fields

        # Determine search mode and create corresponding query template
        search_mode = advanced_policy.mode  # "es_text" or "vearch_vector"

        # Create corresponding query template based on search mode
        if search_mode == "es_text":
            # Create ES query template
            query_template = ESQueryTemplate(
                advanced_search_fields=advanced_search_fields,
                precise_filter_fields=precise_filter_fields,
                output_fields=output_fields,
                es_client=self.es_client
            )
        elif search_mode == "vearch_vector":
            # Create Vearch query template
            query_template = VearchQueryTemplate(
                advanced_search_fields=advanced_search_fields,
                precise_filter_fields=precise_filter_fields,
                output_fields=output_fields,
                vearch_client=self.vearch_client,
                embedding_model=self.embedding_model
            )
        else:
            raise ValueError(f"Unsupported search mode: {search_mode}")

        # Use type annotation: request_model is a dynamically created Pydantic model class
        # Capture request_model through closure to let FastAPI correctly identify the type
        async def search_endpoint(request: request_model) -> SearchResult:
            """Dynamically generated retrieval interface with pagination

            Only fill values in template at runtime, no need to rebuild query structure

            Args:
                request: Dynamically created request model instance (inherits from BaseModel)
            """
            logger.info(f"🔍 Executing search - KB: {kb_name}, Rule: {rule_idx}, Mode: {search_mode}")

            try:
                request_data = request.model_dump()  # Pydantic v2
            except Exception as e:
                logger.warning(f"Failed to get request parameters: {e}")

            try:
                # Extract pagination parameters from request
                page_size = request_data.get("page_size", 10)
                page_number = request_data.get("page_number", 1)

                # Validate pagination parameters
                if page_size <= 0:
                    raise ValueError("page_size must be greater than 0")
                if page_number < 1:
                    raise ValueError("page_number must be greater than or equal to 1")

                # Convert page_number (1-based) to ES offset (0-based)
                page_index = page_number - 1

                # Use template uniformly to execute query (both ES and Vearch use the same interface!)
                if search_mode == "es_text":
                    result = await query_template.execute(
                        request_data=request_data,
                        page_size=page_size,
                        page_number=page_index,
                        kb_name=kb_name
                    )
                elif search_mode == "vearch_vector":
                    result = await query_template.execute(
                        request_data=request_data,
                        page_size=page_size,
                        page_number=page_index,
                        kb_name=kb_name
                    )

                # Reformat items to wrap user schema fields in 'schema' dict
                reformatted_items = [reformat_func(item) for item in result.items]
                result.items = reformatted_items

                return result

            except Exception as e:
                logger.error(f"Search failed: {e}")
                raise HTTPException(status_code=500, detail=f"Search service exception: {str(e)}")

        # Set function name
        search_endpoint.__name__ = f"search_rule_{rule_idx}"

        return search_endpoint

    def _reformat_item_with_schema_wrapper(self, item: dict) -> dict:
        """Reformat item to wrap user schema fields in a 'schema' dict

        System fields and _score remain at top level.
        All user-defined schema fields are grouped under 'schema' key.

        Args:
            item: Original item dictionary

        Returns:
            Reformatted item with schema wrapper
        """
        # Define system fields that stay at top level
        system_fields = {
            'kb_id', 'ori_file_id', 'chunk_id',
            'sys_sample_id', 'sys_group', 'sys_template', 'sys_priority',
            'sys_status', 'sys_executor', 'sys_overview', 'sys_remarks',
            'sys_create_time', 'sys_update_time',
        }

        # Get user schema field names
        schema_field_names = {f.field_name for f in self.kb_schema.fields}

        # Separate fields
        top_level = {}
        schema_fields = {}

        for key, value in item.items():
            if key in system_fields or key.startswith('_'):
                # System fields and special fields (like _score) stay at top level
                top_level[key] = value
            elif key in schema_field_names:
                # User schema fields go into schema dict
                schema_fields[key] = value
            else:
                # Unknown fields also stay at top level for safety
                top_level[key] = value

        # Build final result
        result = top_level.copy()
        if schema_fields:
            result['schema'] = schema_fields

        return result

    def _generate_description(
            self,
            advanced_policy: MatchPolicy,
            precise_policies: list[PreciseMatchPolicy],
            match_rule: MatchRule
    ) -> str:
        """Generate endpoint description

        Priority:
        1. If knowledge base has kb_description, use it directly
        2. Otherwise use default field detail generation logic
        """
        # If knowledge base description exists, use it preferentially
        if self.kb_description:
            return self.kb_description

        # Otherwise use default generation logic
        desc_parts = []

        # Advanced search description (with field descriptions)
        if advanced_policy:
            if advanced_policy.mode == "es_text":
                desc_parts.append(f"**Main Query Strategy**: ES full-text search")
                # Add field detailed descriptions
                field_details = []
                for field_name in advanced_policy.input_fields:
                    field_desc = self.field_descriptions.get(field_name, field_name)
                    field_details.append(f"{field_name} ({field_desc})")
                desc_parts.append(f"**Search Fields**: {', '.join(field_details)}")
            elif advanced_policy.mode == "vearch_vector":
                desc_parts.append(f"**Main Query Strategy**: Vearch vector search")
                # Add field detailed descriptions
                field_details = []
                for field_name in advanced_policy.input_fields:
                    field_desc = self.field_descriptions.get(field_name, field_name)
                    field_details.append(f"{field_name} ({field_desc})")
                desc_parts.append(f"**Search Fields**: {', '.join(field_details)}")

        # Filter condition description (with field descriptions)
        if precise_policies:
            filter_field_details = []
            for policy in precise_policies:
                for field_name in policy.input_fields:
                    field_desc = self.field_descriptions.get(field_name, field_name)
                    filter_field_details.append(f"{field_name} ({field_desc})")
            desc_parts.append(f"**Filter Conditions**: {', '.join(set(filter_field_details))} (exact match)")

        # Output fields (with field descriptions)
        output_field_details = []
        for field_name in match_rule.output_fields:
            field_desc = self.field_descriptions.get(field_name, field_name)
            output_field_details.append(f"{field_name} ({field_desc})")
        desc_parts.append(f"**Output Fields**: {', '.join(output_field_details)}")

        return "\n\n".join(desc_parts)

    def _generate_deposit_endpoint(self):
        """Generate deposit interface (data write/update interface)

        This endpoint supports both create and update operations based on _sample_id:
        - If _sample_id is empty or None: create new record
        - If _sample_id has value: update existing record
        """
        # Create dynamic deposit request model based on schema
        deposit_item_model = self._create_deposit_request_model()

        # Use closure to capture the model type
        kb_name = self.kb_name
        kb_schema = self.kb_schema

        @self.router.post(
            "/deposit",
            summary="Data write/update interface",
            description=f"Write or update data in knowledge base {self.kb_name}. "
                       f"If sys_sample_id is empty, create new record. If sys_sample_id has value, update existing record. "
                       f"Protected fields (cannot be modified): kb_id, sys_sample_id, sys_group.",
            tags=[f"KB:{self.kb_name}"]
        )
        async def deposit(
            data: deposit_item_model = Body(
                ...,
                description=f"Data to write/update. All fields accept string input and will be converted according to schema. "
                           f"User fields: {', '.join([f.field_name for f in kb_schema.fields])}. "
                           f"System fields: sys_sample_id, sys_group, sys_template, sys_priority, sys_status, sys_executor, sys_overview, sys_remarks."
            )
        ):
            """Data write/update interface

            Functions:
            - If sys_sample_id is empty or None: create new record
            - If sys_sample_id has value: update existing record (kb_id, sys_sample_id, sys_group cannot be modified)
            - Perform data type conversion according to schema (all input can be string)
            - Write to Elasticsearch and Vearch (if vectorization is needed)

            Args:
                data: Data item to write/update

            Returns:
                Operation result information
            """
            # Initialize clients
            kb_base_client = ElasticsearchKbBaseManager(self.es_client)
            kb_file_client = ElasticsearchKbFileManager(self.es_client)

            # 1. Query knowledge base information, get kb_id and kb_type
            kb_info_list = kb_base_client.kb_info_search_name(kb_name=kb_name)
            if not kb_info_list or len(kb_info_list) == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"Knowledge base '{kb_name}' does not exist"
                )

            kb_info = kb_info_list[0]
            kb_id = kb_info.get("kb_id")
            kb_type = kb_info.get("kb_type", "structured")

            if not kb_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to get kb_id for knowledge base '{kb_name}'"
                )

            # 2. Validate schema
            if not check_kb_schema(kb_schema):
                raise HTTPException(
                    status_code=400,
                    detail="Current knowledge base kb schema validation failed, please check kb schema!"
                )

            # 3. Convert Pydantic model to dictionary (exclude None values)
            data_dict = data.model_dump(exclude_none=True)

            # 4. Check sys_sample_id to determine create or update
            sample_id = data_dict.get("sys_sample_id", "").strip()
            is_update = bool(sample_id)

            if is_update:
                # Update mode: query existing document
                logger.info(f"Update mode: sys_sample_id={sample_id}")

                # Query existing document from ES
                try:
                    query = {
                        "query": {
                            "bool": {
                                "must": [
                                    {"term": {"kb_id": kb_id}},
                                    {"term": {"sys_sample_id": sample_id}}
                                ]
                            }
                        },
                        "size": 1
                    }

                    response = self.es_client.search(
                        index=kb_name,
                        body=query
                    )

                    hits = response.get("hits", {}).get("hits", [])
                    if not hits:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Record with sys_sample_id='{sample_id}' not found in knowledge base '{kb_name}'"
                        )

                    # Get existing document
                    existing_doc = hits[0]["_source"]
                    es_doc_id = hits[0]["_id"]

                    logger.info(f"Found existing document: es_doc_id={es_doc_id}")

                    # Protect fields that cannot be modified
                    protected_fields = ["kb_id", "sys_sample_id", "sys_group"]
                    for field in protected_fields:
                        if field in data_dict and data_dict[field] != existing_doc.get(field):
                            logger.warning(
                                f"Attempted to modify protected field '{field}', ignoring. "
                                f"Original: {existing_doc.get(field)}, Attempted: {data_dict[field]}"
                            )
                            # Use original value
                            data_dict[field] = existing_doc.get(field)

                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Failed to query existing document: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to query existing document: {str(e)}"
                    )

                # Merge with existing document (keep fields not in data_dict)
                merged_dict = existing_doc.copy()
                merged_dict.update(data_dict)

                # Ensure protected fields are not modified
                merged_dict["kb_id"] = kb_id
                merged_dict["sys_sample_id"] = sample_id
                merged_dict["sys_group"] = existing_doc.get("sys_group", f"mock_file_{kb_id}")

                # Update system fields
                merged_dict["sys_update_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Remove sys_create_time from data_dict to keep original
                data_dict = merged_dict

            else:
                # Create mode: generate new sys_sample_id
                logger.info("Create mode: generating new sys_sample_id")
                sample_id = str(uuid.uuid4().hex[:16])
                data_dict["sys_sample_id"] = sample_id

                # Set default values for system fields if not provided
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                default_group = data_dict.get("sys_group", f"mock_file_{kb_id}")

                data_dict.setdefault("kb_id", kb_id)
                data_dict.setdefault("sys_group", default_group)
                data_dict.setdefault("sys_template", "default")
                data_dict.setdefault("sys_priority", "3")
                data_dict.setdefault("sys_status", "已入库")
                data_dict.setdefault("sys_executor", "")
                data_dict.setdefault("sys_overview", "")
                data_dict.setdefault("sys_remarks", "")
                data_dict.setdefault("sys_create_time", current_time)
                data_dict.setdefault("sys_update_time", current_time)

            # 5. Convert to DataFrame for type conversion
            try:
                df = pd.DataFrame([data_dict])
            except Exception as e:
                logger.error(f"Failed to convert data to DataFrame: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to convert data to DataFrame: {str(e)}"
                )

            # 6. Convert DataFrame column types according to schema
            try:
                df = convert_dataframe_types_by_schema(df, kb_schema)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Field type conversion failed: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Field type conversion failed: {str(e)}"
                )

            # 7. Ensure system fields have correct types
            df['kb_id'] = df['kb_id'].astype(str)
            df['sys_sample_id'] = df['sys_sample_id'].astype(str)
            df['sys_group'] = df['sys_group'].astype(str)

            # Convert sys_priority to integer if it's a string
            if 'sys_priority' in df.columns:
                try:
                    df['sys_priority'] = pd.to_numeric(df['sys_priority'], errors='coerce').fillna(3).astype(int)
                except Exception as e:
                    logger.warning(f"Failed to convert sys_priority to integer: {e}, using default value 3")
                    df['sys_priority'] = 3

            # 8. Write/Update in ES
            if is_update:
                # Update existing document
                try:
                    doc_to_update = df.iloc[0].to_dict()

                    # Handle NaN values
                    for key, value in doc_to_update.items():
                        if pd.isna(value):
                            doc_to_update[key] = None

                    # Update document in ES
                    response = self.es_client.index(
                        index=kb_name,
                        id=es_doc_id,
                        body=doc_to_update,
                        refresh=True
                    )

                    if response.get("result") not in ["updated", "noop"]:
                        logger.error(f"Failed to update document in ES: {response}")
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to update document in ES"
                        )

                    logger.info(f"Successfully updated document in ES: es_doc_id={es_doc_id}")

                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Failed to update document in ES: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to update document in ES: {str(e)}"
                    )

            else:
                # Create new document
                es_add_result = kb_file_client.kb_add_df(kb_name=kb_name, df=df)
                if not es_add_result:
                    logger.error("Failed to add data to ES")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to add data to ES"
                    )
                logger.info(f"Successfully added data to ES")

            # 9. Handle vectorization and Vearch
            if kb_schema.match_rules:
                # Collect all vector matching strategies
                vec_matches = [
                    policy
                    for match_rule in kb_schema.match_rules
                    for policy in match_rule.match_policies
                    if isinstance(policy, VearchVectorMatchPolicy)
                ]

                if vec_matches:
                    vearch_manager = VearchManager(vearch_client=self.vearch_client)

                    try:
                        # Generate vector embeddings
                        for vec_match in vec_matches:
                            field_name = vec_match.input_fields[0]

                            # Check if field exists
                            if field_name not in df.columns:
                                logger.warning(f"Field {field_name} does not exist in DataFrame, skipping vectorization")
                                continue

                            # Check if field has data
                            if df[field_name].isnull().all():
                                logger.warning(f"Field {field_name} is all empty values, skipping vectorization")
                                continue

                            # Check if field values are empty or whitespace-only strings
                            texts = df[field_name].astype(str).tolist()
                            if all(not t.strip() for t in texts):
                                logger.warning(f"Field {field_name} contains only empty strings, skipping vectorization")
                                continue
                            embeddings = self.embedding_model.get_text_embedding_batch(texts, show_progress=True)

                            vector_field_name = f"{field_name}_vector"
                            df[vector_field_name] = embeddings
                            logger.info(f"Successfully generated vector field {vector_field_name} for field {field_name}")

                        # Write/Update in Vearch (upsert will handle both create and update)
                        vearch_result = vearch_manager.add_df(
                            database_name=settings.vearch_config.db_name,
                            space_name=kb_name,
                            df=df
                        )

                        if not vearch_result:
                            logger.error("Failed to write vector data to Vearch")
                            raise HTTPException(
                                status_code=500,
                                detail="Failed to write vector data to Vearch, please check Vearch service status"
                            )
                        logger.info(f"Successfully wrote vector data to Vearch space: {kb_name}")

                    except HTTPException:
                        raise
                    except Exception as e:
                        logger.error(f"Vectorization processing failed: {e}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Vectorization processing failed: {str(e)}"
                        )

            # 10. Update file information (only for create mode)
            if not is_update:
                group_id = data_dict["sys_group"]
                result = kb_file_client.get_kb_file_info(kb_id=kb_id, ori_file_id=group_id)
                ori_file_info = result["_source"] if result else None
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if not ori_file_info:
                    # If current knowledge base doesn't have this file yet, write file information to kb_file
                    mock_file_type = "md" if kb_type == "unstructured" else "csv"
                    kb_file_item = {
                        "kb_id": kb_id,
                        "ori_file_id": group_id,
                        "ori_file_type": mock_file_type,
                        "file_name": f"deposit_{group_id}.{mock_file_type}",
                        "file_path": f"/{group_id}.{mock_file_type}",
                        "document_md5": "",
                        "file_store_mode": "",
                        "file_extra_info": {},
                        "language": "zh",
                        "create_time": current_time,
                        "update_time": current_time,
                    }
                    if not kb_file_client.kb_add_file(kb_file_item):
                        logger.error("Failed to add kb file info to ES")
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to add kb file info to ES"
                        )
                else:
                    ori_file_info["update_time"] = current_time
                    if not kb_file_client.kb_update_file_info(ori_file_info):
                        logger.error("Failed to update kb file info in ES")
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to update kb file info in ES"
                        )

            return {
                "code": 200,
                "msg": "success",
                "data": {
                    "operation": "update" if is_update else "create",
                    "sys_sample_id": sample_id,
                    "message": f"Data {'updated' if is_update else 'inserted'} successfully"
                }
            }

        logger.info(f"✅ Generated deposit interface: POST {self.router.prefix}/deposit")

    def _create_unified_search_request_model(self):
        """Dynamically create unified search request model

        Creates a Pydantic model that includes:
        - All fields defined in the knowledge base schema (user-defined fields)
        - System fields from deposit model
        - Four additional search control fields:
          - _page_size: Page size (default 10, allowed: 10/20/50/100/200)
          - _page_num: Page number (default 1, starting from 1)
          - _order_by: Sort field (default _score, must be int/float field or _score)
          - _is_asc: Ascending order (default False)

        All schema fields are optional for flexible querying.

        Returns:
            A Pydantic model class for unified search requests
        """
        search_fields = {}

        # Add all user-defined fields from schema (all optional, accept string for conversion)
        for field_info in self.kb_schema.fields:
            field_name = field_info.field_name
            field_desc = field_info.field_desc or field_name

            # All fields are optional and accept string input
            search_fields[field_name] = (
                Optional[str],
                Field(None, description=f"Query filter: {field_desc}")
            )

        # Add system fields (all optional)
        search_fields["sys_sample_id"] = (
            Optional[str],
            Field(None, description="Sample ID filter")
        )
        search_fields["sys_group"] = (
            Optional[str],
            Field(None, description="Group identifier filter")
        )
        search_fields["sys_template"] = (
            Optional[str],
            Field(None, description="Template type filter")
        )
        search_fields["sys_priority"] = (
            Optional[str],
            Field(None, description="Priority filter (1-5)")
        )
        search_fields["sys_status"] = (
            Optional[str],
            Field(None, description="Status filter")
        )
        search_fields["sys_executor"] = (
            Optional[str],
            Field(None, description="Executor filter")
        )
        search_fields["sys_overview"] = (
            Optional[str],
            Field(None, description="Overview filter")
        )
        search_fields["sys_remarks"] = (
            Optional[str],
            Field(None, description="Remarks filter")
        )

        # Add search control fields (use alias to support underscore prefix in API)
        # Pydantic doesn't allow field names starting with underscore, so we use alias
        search_fields["page_size"] = (
            int,
            Field(
                default=10,
                ge=1,
                le=200,
                description="Page size (allowed: 10/20/50/100/200)",
                alias="_page_size"
            )
        )
        search_fields["page_number"] = (
            int,
            Field(
                default=1,
                ge=1,
                description="Page number (starting from 1)",
                alias="_page_number"
            )
        )
        search_fields["order_by"] = (
            str,
            Field(
                default="_score",
                description="Sort field (must be numeric field or _score)",
                alias="_order_by"
            )
        )
        search_fields["is_asc"] = (
            bool,
            Field(
                default=False,
                description="Ascending order (default: descending by relevance)",
                alias="_is_asc"
            )
        )

        # Dynamically create model with configuration to support both alias and field name
        model_name = f"UnifiedSearchRequest_{self.kb_name}"

        # Create model with ConfigDict to support populate_by_name
        # This allows API to accept both "_page_size" (alias) and "page_size" (field name)
        return create_model(
            model_name,
            __config__=ConfigDict(populate_by_name=True),
            **search_fields
        )

    def _generate_unified_search_endpoint(self):
        """Generate unified search interface

        This endpoint provides a flexible search across all fields in the knowledge base:
        - Query by any combination of schema fields
        - Support pagination with _page_size and _page_num
        - Support sorting by _order_by (must be numeric fields or _score)
        - Support sort order control with _is_asc
        """
        # Create dynamic unified search request model
        search_request_model = self._create_unified_search_request_model()

        # Use closure to capture the model type
        kb_name = self.kb_name
        kb_schema = self.kb_schema
        es_client = self.es_client
        field_types = self.field_types
        reformat_func = self._reformat_item_with_schema_wrapper

        @self.router.post(
            "/search",
            summary="Unified search interface",
            description=f"Flexible search across all fields in knowledge base {self.kb_name}. "
                       f"Query by any combination of fields with pagination and sorting support.",
            response_model=SearchResult,
            tags=[f"KB:{self.kb_name}"]
        )
        async def unified_search(
            request: search_request_model = Body(
                ...,
                description=f"Search query with optional filters. "
                           f"User fields: {', '.join([f.field_name for f in kb_schema.fields])}. "
                           f"System fields: sys_sample_id, sys_group, sys_template, sys_priority, sys_status, sys_executor, sys_overview, sys_remarks. "
                           f"Control fields: _page_size, _page_num, _order_by, _is_asc."
            )
        ):
            """Unified search interface

            Functions:
            - Query by any combination of schema fields (all fields are filters)
            - Support pagination with _page_size and _page_num
            - Support sorting by _order_by (numeric fields or _score)
            - Support sort order control with _is_asc

            Args:
                request: Search request with filters and control parameters

            Returns:
                SearchResult with paginated results
            """
            try:
                # Convert Pydantic model to dictionary (exclude None values)
                # Note: field names are without underscore prefix (page_size, not _page_size)
                request_data = request.model_dump(exclude_none=True)

                # Extract control parameters (use field names without underscore)
                page_size = request_data.pop("page_size", 10)
                page_num = request_data.pop("page_number", 1)  # Fixed: use page_number to match field definition
                order_by = request_data.pop("order_by", "_score")
                is_asc = request_data.pop("is_asc", False)

                # Validate page_size
                allowed_sizes = [10, 20, 50, 100, 200]
                if page_size not in allowed_sizes:
                    raise HTTPException(
                        status_code=400,
                        detail=f"_page_size must be one of {allowed_sizes}"
                    )

                # Validate order_by field
                if order_by != "_score":
                    # Check if field exists in schema
                    if order_by not in field_types:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid _order_by field '{order_by}'. Must be '_score' or one of the schema fields: {list(field_types.keys())}"
                        )

                    # Check if field is numeric (int or float)
                    field_type = field_types[order_by]
                    if field_type not in ["integer", "float"]:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Field '{order_by}' cannot be used for sorting. Only numeric fields (integer/float) are allowed. Field type: {field_type}"
                        )

                # Convert page_num (1-based) to ES offset (0-based)
                page = page_num - 1
                from_val = page * page_size

                # Build ES query
                query = {
                    "from": from_val,
                    "size": page_size,
                    "query": {
                        "bool": {
                            "filter": []
                        }
                    }
                }

                # Build filter conditions for all provided fields
                # Strategy: use match for string fields (text type), term for numeric fields
                for field_name, value in request_data.items():
                    if value is None or value == "":
                        continue

                    # Determine query type based on field type
                    field_type = field_types.get(field_name, "string")  # Default to string for system fields

                    if field_type == "string":
                        # For string fields (text type in ES), use match query to support analyzed text
                        # This allows matching tokenized content
                        query["query"]["bool"]["must"] = query["query"]["bool"].get("must", [])
                        query["query"]["bool"]["must"].append({
                            "match": {
                                field_name: str(value)
                            }
                        })
                    else:
                        # For integer/float fields, use term query for exact match
                        query["query"]["bool"]["filter"].append({
                            "term": {
                                field_name: str(value)
                            }
                        })

                # If no filters provided, use match_all
                if not query["query"]["bool"]["filter"] and not query["query"]["bool"].get("must"):
                    query["query"] = {"match_all": {}}
                elif not query["query"]["bool"]["filter"]:
                    # If only must conditions exist, remove empty filter
                    del query["query"]["bool"]["filter"]

                # Add sorting
                if order_by == "_score":
                    # Sort by relevance score
                    query["sort"] = [
                        {
                            "_score": {
                                "order": "asc" if is_asc else "desc"
                            }
                        }
                    ]
                else:
                    # Sort by specified field
                    query["sort"] = [
                        {
                            order_by: {
                                "order": "asc" if is_asc else "desc"
                            }
                        }
                    ]

                # Log query for debugging
                import json
                logger.debug(f"Unified Search Query: {json.dumps(query, ensure_ascii=False, indent=2)}")

                # Execute ES query
                response = es_client.search(
                    index=kb_name,
                    body=query
                )

                # Parse results
                hits = response.get("hits", {})
                total = hits.get("total", {}).get("value", 0)
                took_ms = response.get("took", 0)

                items = []
                for hit in hits.get("hits", []):
                    item = hit.get("_source", {}).copy()
                    # Add ES relevance score
                    item["_score"] = hit.get("_score", 0.0)
                    # Reformat item to wrap user schema fields in 'schema' dict
                    reformatted_item = reformat_func(item)
                    items.append(reformatted_item)

                # Calculate pagination metadata
                total_pages = (total + page_size - 1) // page_size if total > 0 else 0
                has_next = page_num < total_pages

                logger.info(f"✅ Unified search completed, returned {len(items)} results, total {total}, page {page_num}/{total_pages}")

                return SearchResult(
                    items=items,
                    total=total,
                    took_ms=took_ms,
                    page_number=page_num,  # Return 1-based page for user-friendly response
                    page_size=page_size,
                    total_pages=total_pages,
                    has_next=has_next
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Unified search failed: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Unified search failed: {str(e)}"
                )

        logger.info(f"✅ Generated unified search interface: POST {self.router.prefix}/search")

    def _generate_delete_endpoint(self):
        """Generate delete interface (delete data by sys_sample_id)

        This endpoint deletes a single data item from both ES and Vearch:
        - Required parameter: sys_sample_id
        - Deletes from Elasticsearch index
        - Deletes from Vearch space (if vectorization is enabled)
        """
        # Use closure to capture required variables
        kb_name = self.kb_name
        kb_schema = self.kb_schema
        es_client = self.es_client
        vearch_client = self.vearch_client

        @self.router.delete(
            "/delete/{sys_sample_id}",
            summary="Delete data by sys_sample_id",
            description=f"Delete a single data item from knowledge base {self.kb_name} by sys_sample_id. "
                       f"This will remove the data from both Elasticsearch and Vearch (if applicable).",
            tags=[f"KB:{self.kb_name}"]
        )
        async def delete_data(
            sys_sample_id: str = Path(..., description="Sample ID to delete")
        ):
            """Delete data by sys_sample_id

            Functions:
            - Query document by sys_sample_id
            - Delete from Elasticsearch
            - Delete from Vearch (if vectorization is enabled)

            Args:
                sys_sample_id: Sample ID to delete

            Returns:
                Delete operation result
            """
            # Initialize clients
            kb_base_client = ElasticsearchKbBaseManager(es_client)

            # 1. Query knowledge base information to get kb_id
            kb_info_list = kb_base_client.kb_info_search_name(kb_name=kb_name)
            if not kb_info_list or len(kb_info_list) == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"Knowledge base '{kb_name}' does not exist"
                )

            kb_info = kb_info_list[0]
            kb_id = kb_info.get("kb_id")

            if not kb_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to get kb_id for knowledge base '{kb_name}'"
                )

            # 2. Query document by sys_sample_id to verify existence
            try:
                query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"kb_id": kb_id}},
                                {"term": {"sys_sample_id": sys_sample_id}}
                            ]
                        }
                    },
                    "size": 1
                }

                response = es_client.search(
                    index=kb_name,
                    body=query
                )

                hits = response.get("hits", {}).get("hits", [])
                if not hits:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Record with sys_sample_id='{sys_sample_id}' not found in knowledge base '{kb_name}'"
                    )

                # Get document ID
                es_doc_id = hits[0]["_id"]
                logger.info(f"Found document to delete: es_doc_id={es_doc_id}, sys_sample_id={sys_sample_id}")

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to query document: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to query document: {str(e)}"
                )

            # 3. Delete from Elasticsearch
            try:
                delete_response = es_client.delete(
                    index=kb_name,
                    id=es_doc_id,
                    refresh=True
                )

                if delete_response.get("result") != "deleted":
                    logger.error(f"Failed to delete document from ES: {delete_response}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to delete document from ES"
                    )

                logger.info(f"Successfully deleted document from ES: es_doc_id={es_doc_id}")

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to delete document from ES: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete document from ES: {str(e)}"
                )

            # 4. Delete from Vearch (if vectorization is enabled)
            if kb_schema.match_rules:
                # Check if there are vector matching policies
                vec_matches = [
                    policy
                    for match_rule in kb_schema.match_rules
                    for policy in match_rule.match_policies
                    if isinstance(policy, VearchVectorMatchPolicy)
                ]

                if vec_matches:
                    try:
                        from vearch.filter import Condition, FieldValue, Filter

                        # Build Vearch filter to delete by sys_sample_id
                        condition_list = [
                            Condition(
                                operator="IN",
                                fv=FieldValue(field="kb_id", value=[kb_id])
                            ),
                            Condition(
                                operator="IN",
                                fv=FieldValue(field="sys_sample_id", value=[sys_sample_id])
                            )
                        ]

                        filters = Filter(operator="AND", conditions=condition_list)

                        # Execute delete operation
                        vearch_response = vearch_client.delete(
                            database_name=settings.vearch_config.db_name,
                            space_name=kb_name,
                            filter=filters
                        )

                        if vearch_response.is_success():
                            logger.info(f"Successfully deleted vector data from Vearch: sys_sample_id={sys_sample_id}")
                        else:
                            logger.warning(f"Failed to delete vector data from Vearch: {vearch_response.msg}")
                            # Don't raise exception here, ES deletion already succeeded

                    except Exception as e:
                        logger.warning(f"Failed to delete vector data from Vearch: {e}")
                        # Don't raise exception here, ES deletion already succeeded

            return {
                "code": 200,
                "msg": "success",
                "data": {
                    "sys_sample_id": sys_sample_id,
                    "message": "Data deleted successfully"
                }
            }

        logger.info(f"✅ Generated delete interface: DELETE {self.router.prefix}/delete/{{sys_sample_id}}")

