from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.data.models import (
    Price,
    FinancialMetrics,
    LineItem,
    InsiderTrade,
    CompanyNews,
)


class BaseApiHandler(ABC):
    """
    Abstract base class for all API handlers.
    Each API handler must implement these methods to provide standardized data access.
    """

    @abstractmethod
    def get_prices(self, ticker: str, start_date: str, end_date: str) -> List[Price]:
        """
        Fetch price data for a given ticker and date range.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of Price objects
        """
        pass

    @abstractmethod
    def get_financial_metrics(
        self, ticker: str, end_date: str, period: str = "ttm", limit: int = 10
    ) -> List[FinancialMetrics]:
        """
        Fetch financial metrics for a given ticker.
        
        Args:
            ticker: Stock ticker symbol
            end_date: End date in YYYY-MM-DD format
            period: Reporting period (e.g., "ttm" for trailing twelve months)
            limit: Maximum number of records to return
            
        Returns:
            List of FinancialMetrics objects
        """
        pass

    @abstractmethod
    def search_line_items(
        self, ticker: str, line_items: List[str], end_date: str, period: str = "ttm", limit: int = 10
    ) -> List[LineItem]:
        """
        Search for specific financial line items.
        
        Args:
            ticker: Stock ticker symbol
            line_items: List of line item names to search for
            end_date: End date in YYYY-MM-DD format
            period: Reporting period (e.g., "ttm" for trailing twelve months)
            limit: Maximum number of records to return
            
        Returns:
            List of LineItem objects
        """
        pass

    @abstractmethod
    def get_insider_trades(
        self, ticker: str, end_date: str, start_date: Optional[str] = None, limit: int = 1000
    ) -> List[InsiderTrade]:
        """
        Fetch insider trades for a given ticker.
        
        Args:
            ticker: Stock ticker symbol
            end_date: End date in YYYY-MM-DD format
            start_date: Optional start date in YYYY-MM-DD format
            limit: Maximum number of records to return
            
        Returns:
            List of InsiderTrade objects
        """
        pass

    @abstractmethod
    def get_company_news(
        self, ticker: str, end_date: str, start_date: Optional[str] = None, limit: int = 1000
    ) -> List[CompanyNews]:
        """
        Fetch company news for a given ticker.
        
        Args:
            ticker: Stock ticker symbol
            end_date: End date in YYYY-MM-DD format
            start_date: Optional start date in YYYY-MM-DD format
            limit: Maximum number of records to return
            
        Returns:
            List of CompanyNews objects
        """
        pass

    @abstractmethod
    def get_market_cap(self, ticker: str, end_date: str) -> Optional[float]:
        """
        Fetch market capitalization for a given ticker.
        
        Args:
            ticker: Stock ticker symbol
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Market capitalization as a float, or None if not available
        """
        pass

    @staticmethod
    def format_date(date_str: str) -> str:
        """
        Standardize date format to YYYY-MM-DD.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Standardized date string in YYYY-MM-DD format
        """
        if isinstance(date_str, datetime):
            return date_str.strftime("%Y-%m-%d")
        
        # If already in YYYY-MM-DD format, return as is
        if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
            return date_str
            
        # Try to parse the date string
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            try:
                dt = datetime.strptime(date_str, "%m/%d/%Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                try:
                    dt = datetime.strptime(date_str, "%d-%m-%Y")
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    # Return as is if we can't parse it
                    return date_str
