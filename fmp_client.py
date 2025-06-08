# --- File: fmp_client.py ---
# Handles all communication with the Financial Modeling Prep API.

import requests

class FmpApiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"

    def _make_request(self, endpoint):
        """Generic request helper."""
        try:
            url = f"{self.base_url}/{endpoint}&apikey={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"FMP API request failed for endpoint {endpoint}: {e}")
            return None

    def get_financial_data(self, ticker, period="annual", limit=10):
        income_statement = self._make_request(f"income-statement/{ticker}?period={period}&limit={limit}")
        balance_sheet = self._make_request(f"balance-sheet-statement/{ticker}?period={period}&limit={limit}")
        cash_flow_statement = self._make_request(f"cash-flow-statement/{ticker}?period={period}&limit={limit}")

        if not all([income_statement, balance_sheet, cash_flow_statement]):
            return {"error": f"Failed to retrieve complete financial data for {ticker} from FMP."}
        
        return {
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow_statement": cash_flow_statement
        }

    def get_key_metrics(self, ticker, period="annual", limit=10):
        return self._make_request(f"key-metrics/{ticker}?period={period}&limit={limit}") or []

    def get_profile_and_quote(self, ticker):
        profile = self._make_request(f"profile/{ticker}?")
        quote = self._make_request(f"quote/{ticker}?")
        enterprise_values = self._make_request(f"enterprise-values/{ticker}?period=annual&limit=1")
        return {
            "profile": profile[0] if profile else {},
            "quote": quote[0] if quote else {},
            "enterprise_value": enterprise_values[0] if enterprise_values else {}
        }

    def get_news(self, ticker, limit=50):
        return self._make_request(f"stock_news?tickers={ticker}&limit={limit}") or []