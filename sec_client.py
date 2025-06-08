# --- File: sec_client.py ---
# Handles all communication with the sec-api.io API.

import requests

class SecApiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.sec-api.io"

    def get_latest_filings(self, ticker):
        """Fetches latest 10-K, 10-Q, Form 4, and 13D filings."""
        query = {
            "query": { "query_string": { "query": f"ticker:{ticker} AND (formType:\"10-K\" OR formType:\"10-Q\" OR formType:\"4\" OR formType:\"SC 13D\")" }},
            "from": "0",
            "size": "20",
            "sort": [{ "filedAt": { "order": "desc" }}]
        }
        try:
            response = requests.post(f"{self.base_url}?token={self.api_key}", json=query)
            response.raise_for_status()
            filings = response.json().get('filings', [])
            
            # Organize filings by form type
            organized_filings = {"10-K": [], "10-Q": [], "4": [], "SC 13D": []}
            for f in filings:
                form_type = f.get('formType')
                if form_type in organized_filings:
                    organized_filings[form_type].append(f)
            return organized_filings
        except requests.exceptions.RequestException as e:
            print(f"SEC API request failed: {e}")
            return {}