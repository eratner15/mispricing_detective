# --- File: main.py ---
# This file contains the Flask application that serves as the backend API
# for the Mispricing Detective tool. It orchestrates data fetching and analysis.

from flask import Flask, jsonify
from flask_cors import CORS
import os
from sec_client import SecApiClient
from fmp_client import FmpApiClient
from analysis_engine import AnalysisEngine

# --- Configuration ---
# Use environment variables for API keys for security.
FMP_API_KEY = os.getenv("FMP_API_KEY", "YOUR_FMP_API_KEY") 
SEC_API_KEY = os.getenv("SEC_API_KEY", "758e5d6bc84238feaa6b6f070c3604e11e277a53016ae0af6af152e844b1d8ea")

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app) # Allows the React frontend to make requests to this server

# --- Service Initialization ---
# Initialize our data clients and analysis engine
sec_client = SecApiClient(SEC_API_KEY)
fmp_client = FmpApiClient(FMP_API_KEY)
analysis_engine = AnalysisEngine()

# --- Main API Endpoint ---
@app.route('/analyze/<string:ticker>', methods=['GET'])
def analyze_ticker(ticker):
    """
    This is the main endpoint for the application. It aggregates all necessary
    data for a given ticker and organizes it into the Four-Pillar structure.
    """
    if not ticker:
        return jsonify({"error": "Ticker symbol is required."}), 400
        
    ticker = ticker.upper()
    
    try:
        # --- Phase 1: Data Aggregation ---
        # Fetch data from both our API clients
        financials = fmp_client.get_financial_data(ticker)
        if "error" in financials: return jsonify(financials), 500
        
        metrics = fmp_client.get_key_metrics(ticker)
        profile_data = fmp_client.get_profile_and_quote(ticker)
        news = fmp_client.get_news(ticker)
        filings = sec_client.get_latest_filings(ticker)
        
        # --- Phase 2: Analysis ---
        # Perform calculations using the analysis engine
        reclassified_cash_flow = analysis_engine.calculate_reclassified_cash_flow(
            financials.get("income_statement", []),
            financials.get("balance_sheet", []),
            financials.get("cash_flow_statement", [])
        )
        news_sentiment = analysis_engine.analyze_sentiment(news)
        valuation_analysis = analysis_engine.calculate_valuation_metrics(
            reclassified_cash_flow,
            profile_data.get("enterprise_value", {}),
            financials.get("income_statement", [])
        )
        catalyst_guideposts = analysis_engine.find_catalysts(filings)

        # --- Pillar Structuring ---
        # Assemble the final JSON response for the frontend
        pillar1_data = {
            "reclassified_cash_flow_analysis": reclassified_cash_flow,
            "key_metrics": metrics,
            "company_profile": profile_data.get("profile", {}),
            "sec_filings": {
                "10-K": filings.get("10-K", [{}])[0].get("link", "#"),
                "10-Q": filings.get("10-Q", [{}])[0].get("link", "#"),
            }
        }
        pillar2_data = {
            "market_data": profile_data.get("quote", {}),
            "news_sentiment": news_sentiment,
            "munger_checklist": analysis_engine.get_munger_checklist()
        }
        pillar3_data = {
            "valuation_analysis": valuation_analysis,
            "key_metrics": metrics,
            "market_data": profile_data.get("quote", {}),
        }
        pillar4_data = {"guideposts": catalyst_guideposts}

        response_data = {
            "ticker": ticker,
            "companyName": profile_data.get("profile", {}).get("companyName", "N/A"),
            "pillars": {
                "business_quality": pillar1_data,
                "contrarian_analysis": pillar2_data,
                "valuation": pillar3_data,
                "catalysts": pillar4_data
            }
        }
        return jsonify(response_data)

    except Exception as e:
        print(f"An unexpected error occurred for ticker {ticker}: {e}")
        return jsonify({"error": f"A server error occurred: {str(e)}"}), 500

# --- How to Run This Backend ---
# 1. Create a project folder. Inside it, create these files:
#    main.py, fmp_client.py, sec_client.py, analysis_engine.py, requirements.txt
#
# 2. Populate requirements.txt with:
#    Flask
#    Flask-Cors
#    requests
#    textblob
#
# 3. Install dependencies:
#    pip install -r requirements.txt
#
# 4. Download NLP corpus for TextBlob:
#    python -m textblob.download_corpora
#
# 5. Set your FMP API key (the SEC key is already in the code):
#    export FMP_API_KEY='your_financial_modeling_prep_api_key'
#
# 6. Run the server:
#    flask --app main run
#
# The backend will now be running on http://127.0.0.1:5000
#
if __name__ == '__main__':
    app.run(debug=True, port=5000)
