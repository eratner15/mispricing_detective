import requests


class SecApiClient:
    def __init__(self, api_key, timeout_seconds=15):
        self.api_key = api_key
        self.base_url = "https://api.sec-api.io"
        self.timeout_seconds = timeout_seconds

    def get_latest_filings(self, ticker):
        """Fetch latest 10-K, 10-Q, Form 4, and SC 13D filings."""
        query = {
            "query": {
                "query_string": {
                    "query": (
                        f'ticker:{ticker} AND '
                        '(formType:"10-K" OR formType:"10-Q" OR formType:"4" OR formType:"SC 13D")'
                    )
                }
            },
            "from": "0",
            "size": "20",
            "sort": [{"filedAt": {"order": "desc"}}],
        }
        try:
            response = requests.post(
                f"{self.base_url}?token={self.api_key}",
                json=query,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            filings = response.json().get('filings', [])

            organized_filings = {"10-K": [], "10-Q": [], "4": [], "SC 13D": []}
            for filing in filings:
                form_type = filing.get('formType')
                if form_type in organized_filings:
                    organized_filings[form_type].append(filing)
            return organized_filings
        except requests.exceptions.RequestException as e:
            print(f"SEC API request failed: {e}")
            return {}
