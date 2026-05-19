"""base_vector_db.py Base Vector Database Class Module.

This file defines the abstract base class for vector database services, inheriting from
BaseDB and providing the interface contract for vector database operations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from oxygent.databases.base_db import BaseDB

logger = logging.getLogger(__name__)


class BaseVectorDB(BaseDB, ABC):
    """Abstract base class defining the vector database interface."""

    @abstractmethod
    async def create_space(self, index_name: str, body: dict[str, Any]) -> Any:
        """Create a new vector space/index. Subclasses must implement."""
        pass

    @abstractmethod
    async def query_search(self, index_name: str, body: dict[str, Any]) -> Any:
        """Search for vectors similar to the query. Subclasses must implement."""
        pass
