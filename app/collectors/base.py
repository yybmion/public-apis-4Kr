"""
Base Collector Class
Stock Intelligence System
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from app.utils.logger import collector_logger, LoggerMixin


class BaseCollector(ABC, LoggerMixin):
    """
    Abstract base class for all data collectors

    All collectors must implement:
    - collect(): Main data collection method
    - validate_data(): Data validation method
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize collector

        Args:
            api_key: API key for external service
        """
        self.api_key = api_key
        self.source_name = self.__class__.__name__

    @abstractmethod
    async def collect(self, **kwargs) -> Dict[str, Any]:
        """
        Collect data from external source

        This method must be implemented by all subclasses

        Args:
            **kwargs: Collection parameters

        Returns:
            Dict containing collected data

        Raises:
            CollectionError: If data collection fails
        """
        pass

    @abstractmethod
    def validate_data(self, data: Dict) -> bool:
        """
        Validate collected data

        This method must be implemented by all subclasses

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def add_metadata(self, data: Dict) -> Dict:
        """
        Add metadata to collected data

        Args:
            data: Original data

        Returns:
            Data with metadata added
        """
        return {
            **data,
            "_metadata": {
                "source": self.source_name,
                "collected_at": datetime.now().isoformat(),
                "verified": self.validate_data(data)
            }
        }

    async def safe_collect(self, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Safely collect data with error handling

        Args:
            **kwargs: Collection parameters

        Returns:
            Collected data or None if failed
        """
        try:
            self.log_info(f"Starting data collection", **kwargs)
            data = await self.collect(**kwargs)

            if not self.validate_data(data):
                self.log_warning(f"Data validation failed", data=str(data)[:200])
                return None

            self.log_info(f"Data collection successful", **kwargs)
            return self.add_metadata(data)

        except Exception as e:
            self.log_error(f"Data collection failed: {str(e)}", **kwargs)
            return None

    async def batch_collect(self, items: list, **kwargs) -> list:
        """
        Collect data for multiple items in batch

        Args:
            items: List of items to collect
            **kwargs: Additional parameters

        Returns:
            List of collected data
        """
        tasks = [self.safe_collect(item=item, **kwargs) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None and exceptions
        valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]

        self.log_info(
            f"Batch collection complete",
            total=len(items),
            successful=len(valid_results),
            failed=len(items) - len(valid_results)
        )

        return valid_results


class CollectionError(Exception):
    """Exception raised for data collection errors"""

    def __init__(self, message: str, source: str = None, details: Dict = None):
        self.message = message
        self.source = source
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        return f"CollectionError [{self.source}]: {self.message}"


class ValidationError(Exception):
    """Exception raised for data validation errors"""

    def __init__(self, message: str, data: Any = None):
        self.message = message
        self.data = data
        super().__init__(self.message)

    def __str__(self):
        return f"ValidationError: {self.message}"
