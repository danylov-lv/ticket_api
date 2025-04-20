from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """
    Abstract base class for repository pattern.
    This class defines the basic CRUD operations to follow in the repository.
    Based on the repository needs, some methods can be omitted or added.
    This class is not intended to be used directly, but rather as a base class for specific repository implementations.

    """

    @abstractmethod
    def create(self, item):
        """
        Create a new item in the repository.

        Args:
            item: The item to be created.

        Returns:
            The created item with its ID.
        """
        pass

    @abstractmethod
    def get(self, item_id):
        """
        Retrieve an item from the repository by its ID.

        Args:
            item_id: The ID of the item to be retrieved.

        Returns:
            The retrieved item or None if not found.
        """
        pass

    @abstractmethod
    def update(self, item_id, item):
        """
        Update an existing item in the repository.

        Args:
            item_id: The ID of the item to be updated.
            item: The updated item data.

        Returns:
            The updated item.
        """
        pass

    @abstractmethod
    def delete(self, item_id):
        """
        Delete an item from the repository by its ID.

        Args:
            item_id: The ID of the item to be deleted.
        """
        pass

    @abstractmethod
    def exists(self, item_id) -> bool:
        """
        Check if an item exists in the repository by its ID.

        Args:
            item_id: The ID of the item to check.

        Returns:
            True if the item exists, False otherwise.
        """
        pass

    @abstractmethod
    def get_all(self):
        """
        Retrieve all items from the repository.

        Returns:
            A list of all items in the repository.
        """
        pass
