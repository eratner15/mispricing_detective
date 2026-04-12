from analysis_engine import AnalysisEngine


def test_reclassified_cash_flow_calculation_returns_recent_years():
    engine = AnalysisEngine()
    income_statements = [
        {
            "calendarYear": "2024",
            "ebitda": 200,
            "depreciationAndAmortization": 50,
            "incomeTaxExpense": 20,
            "incomeBeforeTax": 100,
        },
        {
            "calendarYear": "2023",
            "ebitda": 160,
            "depreciationAndAmortization": 40,
            "incomeTaxExpense": 16,
            "incomeBeforeTax": 80,
        },
    ]
    balance_sheets = [
        {
            "calendarYear": "2024",
            "netReceivables": 120,
            "inventory": 80,
            "accountPayables": 100,
        },
        {
            "calendarYear": "2023",
            "netReceivables": 100,
            "inventory": 70,
            "accountPayables": 90,
        },
    ]
    cash_flow_statements = [
        {"calendarYear": "2024", "capitalExpenditure": -30},
        {"calendarYear": "2023", "capitalExpenditure": -25},
    ]

    result = engine.calculate_reclassified_cash_flow(
        income_statements,
        balance_sheets,
        cash_flow_statements,
    )

    assert result == [
        {"year": 2024, "nopat": 120, "netInvestment": 50, "freeCashFlow": 70}
    ]


def test_valuation_metrics_uses_latest_fcf_and_enterprise_value():
    engine = AnalysisEngine()
    reclassified_cash_flow = [{"freeCashFlow": 100}, {"freeCashFlow": 90}]
    enterprise_value_data = {
        "enterpriseValue": 1000,
        "addTotalDebt": 200,
        "minusCashAndCashEquivalents": 50,
    }
    income_statements = [
        {"ebitda": 200, "depreciationAndAmortization": 50},
        {"ebitda": 180, "depreciationAndAmortization": 40},
    ]

    result = engine.calculate_valuation_metrics(
        reclassified_cash_flow,
        enterprise_value_data,
        income_statements,
    )

    assert result["freeCashFlowYield"] == 10.0
    assert result["earningsPowerValue"]["normalized_ebit"] == 145
    assert result["earningsPowerValue"]["net_debt"] == 150
    assert result["earningsPowerValue"]["epv_equity"] == 1300


def test_find_catalysts_detects_activism_and_insider_buy_language():
    engine = AnalysisEngine()
    filings = {
        "SC 13D": [
            {
                "id": "a1",
                "companyName": "Alpha Capital",
                "filedAt": "2026-03-01",
                "linkToFilingDetails": "https://sec.example/13d",
            }
        ],
        "4": [
            {
                "id": "i1",
                "description": "Open market purchase by CEO",
                "filedAt": "2026-03-05",
                "linkToFilingDetails": "https://sec.example/form4",
            }
        ],
    }

    result = engine.find_catalysts(filings)

    assert any(r["type"] == "Activism" for r in result)
    assert any(r["type"] == "Insider" for r in result)
    assert any(r["type"] == "Operational" for r in result)
    assert any(r["type"] == "Financial" for r in result)
