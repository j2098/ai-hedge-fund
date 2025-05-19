import os
import requests
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from src.api_handlers.base_handler import BaseApiHandler
from src.data.cache import get_cache
from src.data.models import (
    CompanyNews,
    FinancialMetrics,
    Price,
    LineItem,
    InsiderTrade,
)


class FinnhubApiHandler(BaseApiHandler):
    """
    API handler for Finnhub API (finnhub.io).
    """

    def __init__(self):
        """Initialize the handler with cache."""
        self._cache = get_cache()
        self._api_key = os.environ.get("FINNHUB_API_KEY")
        self._base_url = "https://finnhub.io/api/v1"

        if not self._api_key:
            raise ValueError("FINNHUB_API_KEY environment variable is not set")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        return {"X-Finnhub-Token": self._api_key}

    def _convert_to_unix_timestamp(self, date_str: str) -> int:
        """Convert date string to Unix timestamp."""
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return int(dt.timestamp())

    def get_prices(self, ticker: str, start_date: str, end_date: str) -> List[Price]:
        """Fetch price data from cache or API."""
        # Check cache first
        if cached_data := self._cache.get_prices(ticker):
            # Filter cached data by date range and convert to Price objects
            filtered_data = [Price(**price) for price in cached_data if start_date <= price["time"] <= end_date]
            if filtered_data:
                return filtered_data

        # If not in cache or no data in range, fetch from API
        # Convert dates to Unix timestamps for Finnhub
        start_timestamp = self._convert_to_unix_timestamp(start_date)
        end_timestamp = self._convert_to_unix_timestamp(end_date) + 86400  # Add one day to include end_date

        # Finnhub requires resolution parameter (D for daily)
        url = f"{self._base_url}/stock/candle?symbol={ticker}&resolution=D&from={start_timestamp}&to={end_timestamp}"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            raise Exception(f"Error fetching data: {ticker} - {response.status_code} - {response.text}")

        data = response.json()

        # Check if the response is valid
        if data.get("s") == "no_data":
            return []

        # Convert Finnhub data format to our Price model
        prices = []
        for i in range(len(data.get("t", []))):
            timestamp = data["t"][i]
            date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

            price = Price(
                time=date_str,
                open=data["o"][i],
                high=data["h"][i],
                low=data["l"][i],
                close=data["c"][i],
                volume=data["v"][i],
                ticker=ticker
            )
            prices.append(price)

        if not prices:
            return []

        # Cache the results as dicts
        self._cache.set_prices(ticker, [p.model_dump() for p in prices])
        return prices

    def get_financial_metrics(
        self, ticker: str, end_date: str, period: str = "ttm", limit: int = 10
    ) -> List[FinancialMetrics]:
        """Fetch financial metrics from cache or API."""
        # Check cache first
        if cached_data := self._cache.get_financial_metrics(ticker):
            # Filter cached data by date and limit
            filtered_data = [FinancialMetrics(**metric) for metric in cached_data if metric["report_period"] <= end_date]
            filtered_data.sort(key=lambda x: x.report_period, reverse=True)
            if filtered_data:
                return filtered_data[:limit]

        # If not in cache or insufficient data, fetch from API
        # Finnhub has separate endpoints for different metrics, we'll need to combine them

        # Basic financials
        url = f"{self._base_url}/stock/metric?symbol={ticker}&metric=all"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            raise Exception(f"Error fetching metrics: {ticker} - {response.status_code} - {response.text}")

        metrics_data = response.json()

        # Financial ratios from latest filing
        url = f"{self._base_url}/stock/financial-ratios?symbol={ticker}"
        ratios_response = requests.get(url, headers=self._get_headers())

        if ratios_response.status_code != 200:
            raise Exception(f"Error fetching ratios: {ticker} - {ratios_response.status_code} - {ratios_response.text}")

        # 安全地解析JSON，处理空响应
        try:
            ratios_data = ratios_response.json()
        except Exception as e:
            print(f"\n\033[91mFINNHUB ERROR\033[0m: Failed to parse JSON for {ticker} financial ratios: {e}")
            print(f"Response content: {ratios_response.content[:200]}...")
            ratios_data = {}

        # Convert Finnhub data to our FinancialMetrics model
        financial_metrics = []

        # Process annual metrics
        annual_metrics = metrics_data.get("metric", {})

        # Get the latest report date
        report_date = datetime.now().strftime("%Y-%m-%d")
        if ratios_data.get("series") and ratios_data["series"].get("annual"):
            annual_ratios = ratios_data["series"]["annual"]
            if annual_ratios:
                # Get the latest report date from ratios
                latest_period = list(annual_ratios.values())[0][-1]["period"] if list(annual_ratios.values())[0] else None
                if latest_period:
                    report_date = latest_period

        # Create a FinancialMetrics object
        metric = FinancialMetrics(
            ticker=ticker,
            report_period=report_date,
            period=period,

            # Financial metrics
            return_on_equity=annual_metrics.get("roeTTM"),
            return_on_assets=annual_metrics.get("roaTTM"),
            gross_margin=annual_metrics.get("grossMarginTTM"),
            operating_margin=annual_metrics.get("operatingMarginTTM"),
            net_margin=annual_metrics.get("netMarginTTM"),
            debt_to_equity=annual_metrics.get("totalDebt/totalEquityQuarterly"),
            current_ratio=annual_metrics.get("currentRatioQuarterly"),
            quick_ratio=annual_metrics.get("quickRatioQuarterly"),
            interest_coverage=annual_metrics.get("interestCoverage"),
            dividend_yield=annual_metrics.get("dividendYieldIndicatedAnnual"),
            payout_ratio=annual_metrics.get("payoutRatioTTM"),
            price_to_earnings=annual_metrics.get("peBasicExclExtraTTM"),
            price_to_book=annual_metrics.get("pbQuarterly"),
            price_to_sales=annual_metrics.get("psTTM"),
            market_cap=annual_metrics.get("marketCapitalization"),
            enterprise_value=annual_metrics.get("enterpriseValue"),
            enterprise_value_to_revenue=annual_metrics.get("evToRevenue"),
            enterprise_value_to_ebitda=annual_metrics.get("evToEBITDA"),
        )

        financial_metrics.append(metric)

        if not financial_metrics:
            return []

        # Cache the results as dicts
        self._cache.set_financial_metrics(ticker, [m.model_dump() for m in financial_metrics])
        return financial_metrics

    def search_line_items(
        self, ticker: str, line_items: List[str], end_date: str, period: str = "ttm", limit: int = 10
    ) -> List[LineItem]:
        """Fetch line items from API."""
        # Finnhub doesn't have a direct equivalent to line items search
        # We'll use the financial statements endpoint and extract the requested items

        url = f"{self._base_url}/stock/financials?symbol={ticker}&statement=all&freq=annual"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            raise Exception(f"Error fetching financials: {ticker} - {response.status_code} - {response.text}")

        # 安全地解析JSON
        try:
            data = response.json()
        except Exception as e:
            print(f"\n\033[91mFINNHUB ERROR\033[0m: Failed to parse JSON for {ticker} financials: {e}")
            print(f"Response content: {response.content[:200]}...")
            data = {}

        # Convert Finnhub data to our LineItem model
        line_item_results = []

        # Map common line item names to Finnhub's naming
        line_item_mapping = {
            "capital_expenditure": "capitalExpenditures",
            "depreciation_and_amortization": "depreciationAndAmortization",
            "net_income": "netIncome",
            "outstanding_shares": "outstandingShares",
            "total_assets": "totalAssets",
            "total_liabilities": "totalLiabilities",
            "dividends_and_other_cash_distributions": "dividendsPaid",
            "issuance_or_purchase_of_equity_shares": "issuanceOfCapitalStock",
        }

        # Process the financial statements
        statements = data.get("financials", [])

        # Filter by date
        filtered_statements = [s for s in statements if s.get("year") and str(s["year"]) <= end_date.split("-")[0]]

        # Sort by date (most recent first)
        filtered_statements.sort(key=lambda x: x.get("year", 0), reverse=True)

        # Limit the number of statements
        filtered_statements = filtered_statements[:limit]

        # Extract requested line items
        for statement in filtered_statements:
            for item_name in line_items:
                finnhub_name = line_item_mapping.get(item_name)
                if finnhub_name and finnhub_name in statement:
                    value = statement[finnhub_name]

                    # Create a LineItem object
                    line_item = LineItem(
                        ticker=ticker,
                        line_item=item_name,
                        value=float(value) if value is not None else None,
                        report_period=f"{statement.get('year')}-12-31",  # Assuming annual reports end on Dec 31
                        period=period,
                    )

                    line_item_results.append(line_item)

        return line_item_results

    def get_insider_trades(
        self, ticker: str, end_date: str, start_date: Optional[str] = None, limit: int = 1000
    ) -> List[InsiderTrade]:
        """Fetch insider trades from cache or API."""
        # Check cache first
        if cached_data := self._cache.get_insider_trades(ticker):
            # Filter cached data by date range
            filtered_data = [InsiderTrade(**trade) for trade in cached_data if (start_date is None or (trade.get("transaction_date") or trade["filing_date"]) >= start_date) and (trade.get("transaction_date") or trade["filing_date"]) <= end_date]
            filtered_data.sort(key=lambda x: x.transaction_date or x.filing_date, reverse=True)
            if filtered_data:
                return filtered_data

        # If not in cache or insufficient data, fetch from API
        url = f"{self._base_url}/stock/insider-transactions?symbol={ticker}"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            raise Exception(f"Error fetching insider trades: {ticker} - {response.status_code} - {response.text}")

        # 安全地解析JSON
        try:
            data = response.json()
        except Exception as e:
            print(f"\n\033[91mFINNHUB ERROR\033[0m: Failed to parse JSON for {ticker} insider trades: {e}")
            print(f"Response content: {response.content[:200]}...")
            data = {}

        # Convert Finnhub data to our InsiderTrade model
        insider_trades = []

        for trade in data.get("data", []):
            # Convert Finnhub date format (YYYY-MM-DD) to our format
            filing_date = trade.get("filingDate", "")
            transaction_date = trade.get("transactionDate", "")

            # Skip if outside date range
            if start_date and transaction_date < start_date:
                continue
            if transaction_date > end_date:
                continue

            # Create an InsiderTrade object
            insider_trade = InsiderTrade(
                ticker=ticker,
                filing_date=filing_date,
                transaction_date=transaction_date,
                insider_name=trade.get("name", ""),
                title=trade.get("officerTitle", ""),
                transaction_type=trade.get("transactionCode", ""),
                shares=trade.get("share", 0),
                price=trade.get("transactionPrice", 0),
                value=trade.get("value", 0),
            )

            insider_trades.append(insider_trade)

        # Sort by transaction date (most recent first)
        insider_trades.sort(key=lambda x: x.transaction_date or x.filing_date, reverse=True)

        # Limit the number of trades
        insider_trades = insider_trades[:limit]

        if not insider_trades:
            return []

        # Cache the results
        self._cache.set_insider_trades(ticker, [trade.model_dump() for trade in insider_trades])
        return insider_trades

    def get_company_news(
        self, ticker: str, end_date: str, start_date: Optional[str] = None, limit: int = 1000
    ) -> List[CompanyNews]:
        """Fetch company news from cache or API."""
        # Check cache first
        if cached_data := self._cache.get_company_news(ticker):
            # Filter cached data by date range
            filtered_data = [CompanyNews(**news) for news in cached_data if (start_date is None or news["date"] >= start_date) and news["date"] <= end_date]
            filtered_data.sort(key=lambda x: x.date, reverse=True)
            if filtered_data:
                return filtered_data

        # If not in cache or insufficient data, fetch from API
        # Set default start_date to 1 month before end_date if not provided
        if not start_date:
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
            start_date_dt = end_date_dt - timedelta(days=30)
            start_date = start_date_dt.strftime("%Y-%m-%d")

        url = f"{self._base_url}/company-news?symbol={ticker}&from={start_date}&to={end_date}"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            raise Exception(f"Error fetching company news: {ticker} - {response.status_code} - {response.text}")

        # 安全地解析JSON
        try:
            news_data = response.json()
        except Exception as e:
            print(f"\n\033[91mFINNHUB ERROR\033[0m: Failed to parse JSON for {ticker} company news: {e}")
            print(f"Response content: {response.content[:200]}...")
            news_data = []

        # Convert Finnhub data to our CompanyNews model
        company_news = []

        for news in news_data:
            # Convert Finnhub timestamp to date string
            news_date = datetime.fromtimestamp(news.get("datetime", 0)).strftime("%Y-%m-%d")

            # Create a CompanyNews object
            news_item = CompanyNews(
                ticker=ticker,
                date=news_date,
                headline=news.get("headline", ""),
                summary=news.get("summary", ""),
                source=news.get("source", ""),
                url=news.get("url", ""),
            )

            company_news.append(news_item)

        # Sort by date (most recent first)
        company_news.sort(key=lambda x: x.date, reverse=True)

        # Limit the number of news items
        company_news = company_news[:limit]

        if not company_news:
            return []

        # Cache the results
        self._cache.set_company_news(ticker, [news.model_dump() for news in company_news])
        return company_news

    def get_market_cap(self, ticker: str, end_date: str) -> Optional[float]:
        """Fetch market cap from the API."""
        # Finnhub provides market cap in the company profile endpoint
        # Note: Finnhub doesn't support historical market cap, so we ignore end_date
        url = f"{self._base_url}/stock/profile2?symbol={ticker}"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            print(f"Error fetching company profile: {ticker} - {response.status_code}")
            return None

        # 安全地解析JSON
        try:
            profile_data = response.json()
        except Exception as e:
            print(f"\n\033[91mFINNHUB ERROR\033[0m: Failed to parse JSON for {ticker} company profile: {e}")
            print(f"Response content: {response.content[:200]}...")
            return None

        # Get market cap from profile
        market_cap = profile_data.get("marketCapitalization")

        # Convert from millions to actual value
        if market_cap:
            return market_cap * 1000000

        return None
