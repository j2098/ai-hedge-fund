import os
from enum import Enum
from typing import Dict, Optional

from src.api_handlers.base_handler import BaseApiHandler
from src.api_handlers.financial_datasets_handler import FinancialDatasetsApiHandler
from src.api_handlers.finnhub_handler import FinnhubApiHandler


class ApiProvider(Enum):
    """Enum for supported API providers."""
    FINANCIAL_DATASETS = "financial_datasets"
    FINNHUB = "finnhub"


class ApiFactory:
    """Factory class for creating API handlers."""
    
    _handlers: Dict[ApiProvider, BaseApiHandler] = {}
    _default_provider: Optional[ApiProvider] = None
    
    @classmethod
    def get_handler(cls, provider: Optional[ApiProvider] = None) -> BaseApiHandler:
        """
        Get an API handler for the specified provider.
        If provider is None, returns the default handler.
        
        Args:
            provider: The API provider to use
            
        Returns:
            An instance of BaseApiHandler
            
        Raises:
            ValueError: If the provider is not supported or no default provider is set
        """
        # If no provider specified, use default
        if provider is None:
            if cls._default_provider is None:
                cls._determine_default_provider()
            provider = cls._default_provider
            
        # If we still don't have a provider, raise an error
        if provider is None:
            raise ValueError("No API provider specified and no default provider available")
            
        # Create handler if it doesn't exist
        if provider not in cls._handlers:
            cls._create_handler(provider)
            
        return cls._handlers[provider]
    
    @classmethod
    def _create_handler(cls, provider: ApiProvider) -> None:
        """
        Create a new handler for the specified provider.
        
        Args:
            provider: The API provider to create a handler for
            
        Raises:
            ValueError: If the provider is not supported
        """
        if provider == ApiProvider.FINANCIAL_DATASETS:
            cls._handlers[provider] = FinancialDatasetsApiHandler()
        elif provider == ApiProvider.FINNHUB:
            cls._handlers[provider] = FinnhubApiHandler()
        else:
            raise ValueError(f"Unsupported API provider: {provider}")
    
    @classmethod
    def _determine_default_provider(cls) -> None:
        """
        Determine the default API provider based on available API keys.
        Sets the default provider to the first available provider.
        """
        # Check for Finnhub API key
        if os.environ.get("FINNHUB_API_KEY"):
            cls._default_provider = ApiProvider.FINNHUB
        # Check for Financial Datasets API key
        elif os.environ.get("FINANCIAL_DATASETS_API_KEY"):
            cls._default_provider = ApiProvider.FINANCIAL_DATASETS
        # Default to Financial Datasets (which works for free tickers)
        else:
            cls._default_provider = ApiProvider.FINANCIAL_DATASETS
    
    @classmethod
    def set_default_provider(cls, provider: ApiProvider) -> None:
        """
        Set the default API provider.
        
        Args:
            provider: The API provider to set as default
        """
        cls._default_provider = provider
