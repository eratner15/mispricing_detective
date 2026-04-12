# ETF Research Product Review (Quant Research + Investor Lens)

## Scope and limitation

I could not directly access `github.com/eratner15/etf-research` from this environment due outbound connectivity constraints for `git clone`, so this review focuses on the local implementation in this repository as the actionable baseline for immediate improvements.

## Executive take

The product has a strong conceptual frame (quality, contrarian, valuation, catalysts), but it needs stronger production controls and validation to be investment-grade:

- **Strengths:** coherent analytical narrative, broad data intake (fundamentals/news/filings), useful framing for discretionary idea generation.
- **Key risks:** API-key handling, brittle external calls, and no automated tests for core research calculations.
- **What was improved now:** API-key hygiene, request timeouts, lightweight health endpoint, and unit tests for key analytical functions.

## Product assessment

### 1) Research quality

- The current valuation output relies on a simple EPV heuristic and point-in-time EV snapshot; useful as a first-pass screen but not sufficient for portfolio sizing.
- Catalyst extraction from filings is practical but intentionally heuristic and may over-count false positives (e.g., generic Form 4 text).
- Sentiment analysis is headline-based polarity only, which is directionally useful but fragile to financial language nuance.

### 2) Engineering quality

- Prior state had a hardcoded SEC API key fallback and no explicit key readiness check.
- Network requests lacked explicit timeout controls, which can cause endpoint hangs under provider degradation.
- Test coverage for core financial transformations was missing.

### 3) Investor readiness

Before deploying this for live capital, add:

1. point-in-time data controls and revision-safe datasets;
2. benchmarked backtests (gross/net of slippage and fees);
3. factor exposure and risk decomposition;
4. model confidence intervals and data-quality flags;
5. alerting and observability for data pipeline failures.

## Improvements delivered in this patch

1. Removed permissive API key defaults and added explicit missing-key behavior.
2. Added `/healthz` endpoint to expose key-readiness state.
3. Added per-request HTTP timeouts for FMP and SEC clients.
4. Added deterministic unit tests for cash-flow reclassification, valuation metrics, and catalyst detection.

## Recommended next sprint

- Add ETF-specific analytics: creation/redemption proxy, premium/discount persistence, holdings overlap crowding score.
- Add a reproducible backtest module with walk-forward splits and universe survivorship controls.
- Introduce structured logging + retry budget + circuit breaker on data providers.
- Add contract tests for upstream API schema drift.
