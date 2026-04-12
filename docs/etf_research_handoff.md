# Handoff: move this fixset into `github.com/eratner15/etf-research`

Because this execution environment cannot reach GitHub directly (CONNECT tunnel 403), the changes were committed locally and packaged for transfer.

## Option A (recommended): cherry-pick via temporary remote

From your local clone of `eratner15/etf-research`:

```bash
git remote add mispricing_detective <path-or-url-to-this-repo>
git fetch mispricing_detective
git cherry-pick 9dac384
```

## Option B: apply exported patch file

In this repo:

```bash
./scripts/export_etf_research_patch.sh /tmp/etf-research-fix.patch
```

Then in your `eratner15/etf-research` clone:

```bash
git am /tmp/etf-research-fix.patch
```

If conflicts occur:

```bash
git am --abort
# or manually resolve and continue
```

## What is included in commit `9dac384`

- API key hardening and readiness checks (`main.py`)
- request timeouts and safer client request handling (`fmp_client.py`, `sec_client.py`)
- deterministic sentiment + stable analysis engine behavior (`analysis_engine.py`)
- unit tests (`tests/`)
- quant/investor review memo (`docs/etf_research_review.md`)
