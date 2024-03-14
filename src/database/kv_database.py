from abc import ABC, abstractmethod
from typing import Any, Dict

class KV_Database(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__()
        # Initialization can be arbitrary and flexible for subclass implementations.
    
    @abstractmethod
    def insert(self, category, key, value) -> None:
        """Insert a key-value pair."""
        pass

    @abstractmethod
    def set(self, category, key, value) -> None:
        """Set a value for a given key. Raise error if key exists."""
        pass

    @abstractmethod
    def update(self, category, key, updated_values) -> None:
        """Update the specified values for a given key. Raise error if key does not exist."""
        pass

    @abstractmethod
    def get(self, category, key) -> Dict[str, Any]:
        """Retrieve the value associated with a key."""
        pass

    @abstractmethod
    def delete(self, category, key) -> None:
        """Delete a key-value pair."""
        pass

    @abstractmethod
    def exists(self, category, key) -> bool:
        """Check if a key exists."""
        pass

    @abstractmethod
    def append(self, category, key, value) -> None:
        """Append a value to a list associated with a key."""
        pass

    @abstractmethod
    def remove_from_list(self, category, key, value) -> None:
        """Remove a value from a list associated with a key."""
        pass