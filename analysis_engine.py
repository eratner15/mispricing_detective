# --- File: analysis_engine.py ---
# Contains all the financial calculation and analysis logic.

from textblob import TextBlob
import re

class AnalysisEngine:

    def calculate_reclassified_cash_flow(self, income_statements, balance_sheets, cash_flow_statements):
        """Calculates NOPAT, Net Investment, and Free Cash Flow."""
        # This logic remains the same as in the previous version
        analysis_results = []
        income_map = {item['calendarYear']: item for item in income_statements}
        balance_map = {item['calendarYear']: item for item in balance_sheets}
        cash_flow_map = {item['calendarYear']: item for item in cash_flow_statements}
        sorted_years = sorted(balance_map.keys(), reverse=True)

        for i, year_str in enumerate(sorted_years):
            if i >= len(sorted_years) - 1: continue
            current_year, prior_year_str = int(year_str), str(int(year_str) - 1)
            if not all(k in income_map and k in balance_map and k in cash_flow_map for k in [year_str, prior_year_str]):
                continue

            inc = income_map[year_str]
            bs_curr, bs_prior = balance_map[year_str], balance_map[prior_year_str]
            
            ebit = inc.get('ebitda', 0) - inc.get('depreciationAndAmortization', 0)
            tax_rate = inc.get('incomeTaxExpense', 0) / inc.get('incomeBeforeTax', 1) if inc.get('incomeBeforeTax') else 0
            nopat = ebit * (1 - tax_rate)

            op_wc_curr = (bs_curr.get('netReceivables', 0) + bs_curr.get('inventory', 0)) - bs_curr.get('accountPayables', 0)
            op_wc_prior = (bs_prior.get('netReceivables', 0) + bs_prior.get('inventory', 0)) - bs_prior.get('accountPayables', 0)
            change_in_op_wc = op_wc_curr - op_wc_prior
            capex = -cash_flow_map[year_str].get('capitalExpenditure', 0)
            net_investment = change_in_op_wc + capex
            free_cash_flow = nopat - net_investment
            
            analysis_results.append({
                "year": current_year, "nopat": round(nopat),
                "netInvestment": round(net_investment), "freeCashFlow": round(free_cash_flow),
            })
        return analysis_results

    def analyze_sentiment(self, news_articles):
        """Performs basic sentiment analysis on news headlines."""
        # This logic remains the same
        sentiments, pos, neg, neu = [], 0, 0, 0
        for article in news_articles:
            text, blob = article.get('title', ''), TextBlob(text)
            pol = blob.sentiment.polarity
            if pol > 0.1: sentiment_label, pos = "Positive", pos + 1
            elif pol < -0.1: sentiment_label, neg = "Negative", neg + 1
            else: sentiment_label, neu = "Neutral", neu + 1
            sentiments.append({"text": text, "url": article.get('url'), "sentiment_label": sentiment_label})
        summary = {"positive_count": pos, "negative_count": neg, "neutral_count": neu, "total_articles": len(news_articles)}
        return {"summary": summary, "articles": sentiments[:10]} # Return top 10 for UI

    def get_munger_checklist(self):
        """Returns a static Munger-inspired psychological checklist."""
        # This logic remains the same
        return [
            {"bias": "Social Proof & Authority", "question": "Is the market's view driven by herd behavior or a few influential analysts?"},
            {"bias": "Availability & Recency", "question": "Is a recent negative event being extrapolated indefinitely into the future?"},
        ]

    def calculate_valuation_metrics(self, reclassified_cash_flow, enterprise_value_data, income_statements):
        """Calculates FCF Yield and a simple EPV."""
        # This logic remains the same
        fcf_yield = 0
        latest_fcf = reclassified_cash_flow[0].get('freeCashFlow') if reclassified_cash_flow else 0
        enterprise_value = enterprise_value_data.get('enterpriseValue') if enterprise_value_data else 0
        if enterprise_value > 0: fcf_yield = (latest_fcf / enterprise_value) * 100

        ebit_values = [inc.get('ebitda', 0) - inc.get('depreciationAndAmortization', 0) for inc in income_statements]
        normalized_ebit = sum(ebit_values) / len(ebit_values) if ebit_values else 0
        cost_of_capital = 0.10
        epv_firm = normalized_ebit / cost_of_capital if cost_of_capital > 0 else 0
        net_debt = enterprise_value_data.get('addTotalDebt', 0) - enterprise_value_data.get('minusCashAndCashEquivalents', 0)
        epv_equity = epv_firm - net_debt

        return {
            "freeCashFlowYield": round(fcf_yield, 2),
            "earningsPowerValue": {"epv_equity": round(epv_equity), "normalized_ebit": round(normalized_ebit), "net_debt": round(net_debt)}
        }

    def find_catalysts(self, filings):
        """Scans SEC filings to identify potential catalysts."""
        guideposts = []
        
        # Activist Catalyst (SC 13D)
        for f in filings.get("SC 13D", []):
            filer_name = f.get('companyName', 'An activist') # In this API, companyName is the filer
            if filer_name:
                guideposts.append({
                    "id": f.get("id"), "type": "Activism", "status": "pending",
                    "evidence": f"{filer_name} filed an SC 13D on {f.get('filedAt', 'N/A')}. [View Filing]",
                    "link": f.get('linkToFilingDetails', '#')
                })

        # Insider Catalyst (Form 4)
        for f in filings.get("4", []):
            # Form 4 transaction codes: 'P' for Purchase, 'S' for Sale
            # We only care about open market buys.
            # This is a simplification; a real implementation would parse the XML filing.
            # For now, we look for a 'P' in the description.
            description = f.get('description', '')
            if 'purchase' in description.lower() or 'buy' in description.lower():
                 guideposts.append({
                    "id": f.get("id"), "type": "Insider", "status": "pending",
                    "evidence": f"Insider transaction (purchase) reported on {f.get('filedAt', 'N/A')}. [View Filing]",
                    "link": f.get('linkToFilingDetails', '#')
                })

        # Add some placeholder operational catalysts
        guideposts.append({"id": "op1", "type": "Operational", "status": "pending", "evidence": "Potential for margin expansion if input costs normalize."})
        guideposts.append({"id": "fin1", "type": "Financial", "status": "pending", "evidence": "Company has a history of opportunistic share repurchases."})

        return guideposts