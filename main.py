from flask import Flask, jsonify
from flask_cors import CORS
import os
from sec_client import SecApiClient
from fmp_client import FmpApiClient
from analysis_engine import AnalysisEngine

# --- Configuration ---
# API keys are expected via environment variables.
FMP_API_KEY = os.getenv("FMP_API_KEY", "")
SEC_API_KEY = os.getenv("SEC_API_KEY", "")

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Service Initialization ---
sec_client = SecApiClient(SEC_API_KEY)
fmp_client = FmpApiClient(FMP_API_KEY)
analysis_engine = AnalysisEngine()


@app.route('/healthz', methods=['GET'])
def health_check():
    missing_keys = []
    if not FMP_API_KEY:
        missing_keys.append('FMP_API_KEY')
    if not SEC_API_KEY:
        missing_keys.append('SEC_API_KEY')

    return jsonify({
        'status': 'ok' if not missing_keys else 'degraded',
        'missing_api_keys': missing_keys,
    }), 200


@app.route('/analyze/<string:ticker>', methods=['GET'])
def analyze_ticker(ticker):
    """
    Main endpoint for aggregating and analyzing ticker-level data.
    """
    if not ticker:
        return jsonify({"error": "Ticker symbol is required."}), 400

    missing_keys = [key for key, value in {
        'FMP_API_KEY': FMP_API_KEY,
        'SEC_API_KEY': SEC_API_KEY,
    }.items() if not value]
    if missing_keys:
        return jsonify({
            "error": "Missing required API keys.",
            "missing": missing_keys,
        }), 500

    ticker = ticker.upper()

    try:
        financials = fmp_client.get_financial_data(ticker)
        if "error" in financials:
            return jsonify(financials), 500

        metrics = fmp_client.get_key_metrics(ticker)
        profile_data = fmp_client.get_profile_and_quote(ticker)
        news = fmp_client.get_news(ticker)
        filings = sec_client.get_latest_filings(ticker)

        reclassified_cash_flow = analysis_engine.calculate_reclassified_cash_flow(
            financials.get("income_statement", []),
            financials.get("balance_sheet", []),
            financials.get("cash_flow_statement", []),
        )
        news_sentiment = analysis_engine.analyze_sentiment(news)
        valuation_analysis = analysis_engine.calculate_valuation_metrics(
            reclassified_cash_flow,
            profile_data.get("enterprise_value", {}),
            financials.get("income_statement", []),
        )
        catalyst_guideposts = analysis_engine.find_catalysts(filings)

        pillar1_data = {
            "reclassified_cash_flow_analysis": reclassified_cash_flow,
            "key_metrics": metrics,
            "company_profile": profile_data.get("profile", {}),
            "sec_filings": {
                "10-K": filings.get("10-K", [{}])[0].get("link", "#"),
                "10-Q": filings.get("10-Q", [{}])[0].get("link", "#"),
            },
        }
        pillar2_data = {
            "market_data": profile_data.get("quote", {}),
            "news_sentiment": news_sentiment,
            "munger_checklist": analysis_engine.get_munger_checklist(),
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
                "catalysts": pillar4_data,
            },
        }
        return jsonify(response_data)

    except Exception as e:
        print(f"An unexpected error occurred for ticker {ticker}: {e}")
        return jsonify({"error": f"A server error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
