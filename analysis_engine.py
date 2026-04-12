import re


class AnalysisEngine:
    POSITIVE_TERMS = {
        'beat', 'growth', 'upside', 'upgrade', 'outperform', 'strong', 'improved', 'buyback', 'accretive'
    }
    NEGATIVE_TERMS = {
        'miss', 'decline', 'downgrade', 'underperform', 'weak', 'cut', 'lawsuit', 'loss', 'risk'
    }

    def calculate_reclassified_cash_flow(self, income_statements, balance_sheets, cash_flow_statements):
        """Calculates NOPAT, Net Investment, and Free Cash Flow."""
        analysis_results = []
        income_map = {item['calendarYear']: item for item in income_statements}
        balance_map = {item['calendarYear']: item for item in balance_sheets}
        cash_flow_map = {item['calendarYear']: item for item in cash_flow_statements}
        sorted_years = sorted(balance_map.keys(), reverse=True)

        for i, year_str in enumerate(sorted_years):
            if i >= len(sorted_years) - 1:
                continue

            current_year, prior_year_str = int(year_str), str(int(year_str) - 1)
            if not all(k in income_map and k in balance_map and k in cash_flow_map for k in [year_str, prior_year_str]):
                continue

            inc = income_map[year_str]
            bs_curr, bs_prior = balance_map[year_str], balance_map[prior_year_str]

            ebit = inc.get('ebitda', 0) - inc.get('depreciationAndAmortization', 0)
            if inc.get('incomeBeforeTax'):
                tax_rate = inc.get('incomeTaxExpense', 0) / inc.get('incomeBeforeTax', 1)
            else:
                tax_rate = 0
            nopat = ebit * (1 - tax_rate)

            op_wc_curr = (bs_curr.get('netReceivables', 0) + bs_curr.get('inventory', 0)) - bs_curr.get('accountPayables', 0)
            op_wc_prior = (bs_prior.get('netReceivables', 0) + bs_prior.get('inventory', 0)) - bs_prior.get('accountPayables', 0)
            change_in_op_wc = op_wc_curr - op_wc_prior
            capex = -cash_flow_map[year_str].get('capitalExpenditure', 0)
            net_investment = change_in_op_wc + capex
            free_cash_flow = nopat - net_investment

            analysis_results.append({
                "year": current_year,
                "nopat": round(nopat),
                "netInvestment": round(net_investment),
                "freeCashFlow": round(free_cash_flow),
            })
        return analysis_results

    def _simple_sentiment_label(self, text):
        tokens = set(re.findall(r"[a-zA-Z']+", text.lower()))
        pos_score = len(tokens & self.POSITIVE_TERMS)
        neg_score = len(tokens & self.NEGATIVE_TERMS)
        if pos_score > neg_score:
            return 'Positive'
        if neg_score > pos_score:
            return 'Negative'
        return 'Neutral'

    def analyze_sentiment(self, news_articles):
        """Performs lightweight headline sentiment analysis without external NLP dependencies."""
        sentiments, pos, neg, neu = [], 0, 0, 0
        for article in news_articles:
            text = article.get('title', '')
            sentiment_label = self._simple_sentiment_label(text)
            if sentiment_label == 'Positive':
                pos += 1
            elif sentiment_label == 'Negative':
                neg += 1
            else:
                neu += 1
            sentiments.append({"text": text, "url": article.get('url'), "sentiment_label": sentiment_label})

        summary = {
            "positive_count": pos,
            "negative_count": neg,
            "neutral_count": neu,
            "total_articles": len(news_articles),
        }
        return {"summary": summary, "articles": sentiments[:10]}

    def get_munger_checklist(self):
        return [
            {
                "bias": "Social Proof & Authority",
                "question": "Is the market's view driven by herd behavior or a few influential analysts?",
            },
            {
                "bias": "Availability & Recency",
                "question": "Is a recent negative event being extrapolated indefinitely into the future?",
            },
        ]

    def calculate_valuation_metrics(self, reclassified_cash_flow, enterprise_value_data, income_statements):
        """Calculates FCF Yield and a simple EPV."""
        fcf_yield = 0
        latest_fcf = reclassified_cash_flow[0].get('freeCashFlow') if reclassified_cash_flow else 0
        enterprise_value = enterprise_value_data.get('enterpriseValue') if enterprise_value_data else 0
        if enterprise_value > 0:
            fcf_yield = (latest_fcf / enterprise_value) * 100

        ebit_values = [inc.get('ebitda', 0) - inc.get('depreciationAndAmortization', 0) for inc in income_statements]
        normalized_ebit = sum(ebit_values) / len(ebit_values) if ebit_values else 0
        cost_of_capital = 0.10
        epv_firm = normalized_ebit / cost_of_capital if cost_of_capital > 0 else 0
        net_debt = enterprise_value_data.get('addTotalDebt', 0) - enterprise_value_data.get('minusCashAndCashEquivalents', 0)
        epv_equity = epv_firm - net_debt

        return {
            "freeCashFlowYield": round(fcf_yield, 2),
            "earningsPowerValue": {
                "epv_equity": round(epv_equity),
                "normalized_ebit": round(normalized_ebit),
                "net_debt": round(net_debt),
            },
        }

    def find_catalysts(self, filings):
        """Scans SEC filings to identify potential catalysts."""
        guideposts = []

        for filing in filings.get("SC 13D", []):
            filer_name = filing.get('companyName', 'An activist')
            if filer_name:
                guideposts.append({
                    "id": filing.get("id"),
                    "type": "Activism",
                    "status": "pending",
                    "evidence": f"{filer_name} filed an SC 13D on {filing.get('filedAt', 'N/A')}. [View Filing]",
                    "link": filing.get('linkToFilingDetails', '#'),
                })

        for filing in filings.get("4", []):
            description = filing.get('description', '')
            if 'purchase' in description.lower() or 'buy' in description.lower():
                guideposts.append({
                    "id": filing.get("id"),
                    "type": "Insider",
                    "status": "pending",
                    "evidence": f"Insider transaction (purchase) reported on {filing.get('filedAt', 'N/A')}. [View Filing]",
                    "link": filing.get('linkToFilingDetails', '#'),
                })

        guideposts.append({
            "id": "op1",
            "type": "Operational",
            "status": "pending",
            "evidence": "Potential for margin expansion if input costs normalize.",
        })
        guideposts.append({
            "id": "fin1",
            "type": "Financial",
            "status": "pending",
            "evidence": "Company has a history of opportunistic share repurchases.",
        })

        return guideposts
