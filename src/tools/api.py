from datetime import datetime
import os
import pandas as pd
from typing import List, Optional

from src.api_handlers.api_factory import ApiFactory, ApiProvider
from src.data.models import (
    CompanyNews,
    FinancialMetrics,
    Price,
    LineItem,
    InsiderTrade,
)

# Get API provider from environment variable or use default
api_provider_name = os.environ.get("API_PROVIDER", "").lower()
api_provider = None

if api_provider_name == "finnhub":
    api_provider = ApiProvider.FINNHUB
elif api_provider_name == "financial_datasets":
    api_provider = ApiProvider.FINANCIAL_DATASETS

# Get the appropriate API handler
api_handler = ApiFactory.get_handler(api_provider)
print(f"\n\033[92mINFO\033[0m: Using API provider: {api_provider}")

def get_prices(ticker: str, start_date: str, end_date: str) -> List[Price]:
    """
    Fetch price data for a given ticker and date range.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List of Price objects or empty list if data cannot be retrieved
    """
    try:
        return api_handler.get_prices(ticker, start_date, end_date)
    except Exception as e:
        # If the primary API fails, try the other API
        if api_provider == ApiProvider.FINANCIAL_DATASETS:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINNHUB)
                return fallback_handler.get_prices(ticker, start_date, end_date)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回空列表
                print(f"Warning: Failed to get prices for {ticker}: {e}. Fallback also failed: {fallback_error}")
                return []
        elif api_provider == ApiProvider.FINNHUB:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINANCIAL_DATASETS)
                return fallback_handler.get_prices(ticker, start_date, end_date)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回空列表
                print(f"Warning: Failed to get prices for {ticker}: {e}. Fallback also failed: {fallback_error}")
                return []
        else:
            # 记录错误并返回空列表
            print(f"Warning: Failed to get prices for {ticker}: {e}")
            return []


def get_financial_metrics(
    ticker: str,
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
) -> List[FinancialMetrics]:
    """
    Fetch financial metrics for a given ticker.

    Args:
        ticker: Stock ticker symbol
        end_date: End date in YYYY-MM-DD format
        period: Reporting period (e.g., "ttm" for trailing twelve months)
        limit: Maximum number of records to return

    Returns:
        List of FinancialMetrics objects or empty list if data cannot be retrieved
    """
    try:
        return api_handler.get_financial_metrics(ticker, end_date, period, limit)
    except Exception as e:
        # If the primary API fails, try the other API
        if api_provider == ApiProvider.FINANCIAL_DATASETS:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINNHUB)
                return fallback_handler.get_financial_metrics(ticker, end_date, period, limit)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回空列表
                print(f"\n\033[91mAPI ERROR\033[0m: Failed to get financial metrics for {ticker}: {e}")
                print(f"\033[91mFALLBACK ERROR\033[0m: {fallback_error}")
                return []
        elif api_provider == ApiProvider.FINNHUB:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINANCIAL_DATASETS)
                return fallback_handler.get_financial_metrics(ticker, end_date, period, limit)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回空列表
                print(f"\n\033[91mAPI ERROR\033[0m: Failed to get financial metrics for {ticker}: {e}")
                print(f"\033[91mFALLBACK ERROR\033[0m: {fallback_error}")
                return []
        else:
            # 记录错误并返回空列表
            print(f"\n\033[91mAPI ERROR\033[0m: Failed to get financial metrics for {ticker}: {e}")
            return []


def search_line_items(
    ticker: str,
    line_items: List[str],
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
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
        List of LineItem objects or empty list if data cannot be retrieved
    """
    try:
        return api_handler.search_line_items(ticker, line_items, end_date, period, limit)
    except Exception as e:
        # If the primary API fails, try the other API
        if api_provider == ApiProvider.FINANCIAL_DATASETS:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINNHUB)
                return fallback_handler.search_line_items(ticker, line_items, end_date, period, limit)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回空列表
                print(f"Warning: Failed to search line items for {ticker}: {e}. Fallback also failed: {fallback_error}")
                return []
        elif api_provider == ApiProvider.FINNHUB:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINANCIAL_DATASETS)
                return fallback_handler.search_line_items(ticker, line_items, end_date, period, limit)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回空列表
                print(f"Warning: Failed to search line items for {ticker}: {e}. Fallback also failed: {fallback_error}")
                return []
        else:
            # 记录错误并返回空列表
            print(f"Warning: Failed to search line items for {ticker}: {e}")
            return []


def get_insider_trades(
    ticker: str,
    end_date: str,
    start_date: Optional[str] = None,
    limit: int = 1000,
) -> List[InsiderTrade]:
    """
    Fetch insider trades for a given ticker.

    Args:
        ticker: Stock ticker symbol
        end_date: End date in YYYY-MM-DD format
        start_date: Optional start date in YYYY-MM-DD format
        limit: Maximum number of records to return

    Returns:
        List of InsiderTrade objects or empty list if data cannot be retrieved
    """
    try:
        return api_handler.get_insider_trades(ticker, end_date, start_date, limit)
    except Exception as e:
        # If the primary API fails, try the other API
        if api_provider == ApiProvider.FINANCIAL_DATASETS:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINNHUB)
                return fallback_handler.get_insider_trades(ticker, end_date, start_date, limit)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回空列表
                print(f"Warning: Failed to get insider trades for {ticker}: {e}. Fallback also failed: {fallback_error}")
                return []
        elif api_provider == ApiProvider.FINNHUB:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINANCIAL_DATASETS)
                return fallback_handler.get_insider_trades(ticker, end_date, start_date, limit)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回空列表
                print(f"Warning: Failed to get insider trades for {ticker}: {e}. Fallback also failed: {fallback_error}")
                return []
        else:
            # 记录错误并返回空列表
            print(f"Warning: Failed to get insider trades for {ticker}: {e}")
            return []


def get_company_news(
    ticker: str,
    end_date: str,
    start_date: Optional[str] = None,
    limit: int = 1000,
) -> List[CompanyNews]:
    """
    Fetch company news for a given ticker.

    Args:
        ticker: Stock ticker symbol
        end_date: End date in YYYY-MM-DD format
        start_date: Optional start date in YYYY-MM-DD format
        limit: Maximum number of records to return

    Returns:
        List of CompanyNews objects or empty list if data cannot be retrieved
    """
    try:
        return api_handler.get_company_news(ticker, end_date, start_date, limit)
    except Exception as e:
        # If the primary API fails, try the other API
        if api_provider == ApiProvider.FINANCIAL_DATASETS:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINNHUB)
                return fallback_handler.get_company_news(ticker, end_date, start_date, limit)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回空列表
                print(f"Warning: Failed to get company news for {ticker}: {e}. Fallback also failed: {fallback_error}")
                return []
        elif api_provider == ApiProvider.FINNHUB:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINANCIAL_DATASETS)
                return fallback_handler.get_company_news(ticker, end_date, start_date, limit)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回空列表
                print(f"Warning: Failed to get company news for {ticker}: {e}. Fallback also failed: {fallback_error}")
                return []
        else:
            # 记录错误并返回空列表
            print(f"Warning: Failed to get company news for {ticker}: {e}")
            return []


def get_market_cap(
    ticker: str,
    end_date: str,
) -> Optional[float]:
    """
    Fetch market capitalization for a given ticker.

    Args:
        ticker: Stock ticker symbol
        end_date: End date in YYYY-MM-DD format

    Returns:
        Market capitalization as a float, or None if not available
    """
    try:
        return api_handler.get_market_cap(ticker, end_date)
    except Exception as e:
        # If the primary API fails, try the other API
        if api_provider == ApiProvider.FINANCIAL_DATASETS:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINNHUB)
                return fallback_handler.get_market_cap(ticker, end_date)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回None
                print(f"Warning: Failed to get market cap for {ticker}: {e}. Fallback also failed: {fallback_error}")
                return None
        elif api_provider == ApiProvider.FINNHUB:
            try:
                fallback_handler = ApiFactory.get_handler(ApiProvider.FINANCIAL_DATASETS)
                return fallback_handler.get_market_cap(ticker, end_date)
            except Exception as fallback_error:
                # 如果两个API都失败，记录错误并返回None
                print(f"Warning: Failed to get market cap for {ticker}: {e}. Fallback also failed: {fallback_error}")
                return None
        else:
            # 记录错误并返回None
            print(f"Warning: Failed to get market cap for {ticker}: {e}")
            return None


def prices_to_df(prices: List[Price]) -> pd.DataFrame:
    """
    Convert a list of Price objects to a pandas DataFrame.

    Args:
        prices: List of Price objects

    Returns:
        DataFrame with price data
    """
    df = pd.DataFrame([p.model_dump() for p in prices])
    if df.empty:
        return pd.DataFrame(columns=["open", "close", "high", "low", "volume"])

    df["Date"] = pd.to_datetime(df["time"])
    df.set_index("Date", inplace=True)
    numeric_cols = ["open", "close", "high", "low", "volume"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df.sort_index(inplace=True)
    return df


def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Get price data for a ticker and convert to DataFrame.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        DataFrame with price data
    """
    prices = get_prices(ticker, start_date, end_date)
    return prices_to_df(prices)
