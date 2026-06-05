"""Database factory for OxyGent.

Provides DBFactory, a singleton factory for creating and caching database client instances.
"""

from typing import Any


class DBFactory:
    """Singleton factory that creates and caches database client instances (ES, Redis, Vector)."""

    _instance: Any = None
    _created_class: type | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "DBFactory":
        """Create or return a singleton instance of SingletonFactory, ensure only one
        instance of the factory is created."""
        if not hasattr(cls, "_factory_instance"):
            cls._factory_instance = super().__new__(cls)
        return cls._factory_instance

    def get_instance(self, class_type: type, *args: Any, **kwargs: Any) -> Any:
        """Get instance of assigned class_type.

        Create instance if not exists, otherwise return the existing instance.
        Only permits instance of the same class to be created.

        Args:
            class_type: the class type to be created
            *args: location arguments
            **kwargs: keyword arguments
        Returns:
            class_type: the instance of the class_type

        Raises:
            Exception: when the class_type is not the same as the created class
        """
        if self._instance is None:
            # Create 1st instance
            self._instance = class_type(*args, **kwargs)
            self._created_class = class_type
        elif self._created_class != class_type:
            # Have existing instance, but the class_type is not the same as the created class
            raise Exception(
                f"DBFactory can only produce single instance of a class: {self._created_class.__name__}"
            )
        return self._instance
