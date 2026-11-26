# Quantitative audit trail and red-team history

## Iterative research waves (July to September 2026)

Config E emerged across four development waves. Each phase replaced optimistic approximations with stricter market rules whenever forensic checks exposed a leak.

### Wave 1: Early prototypes and initial self-audit (`2026-07-19` to `2026-08-01`)

Initial BSE crawlers ingested 37,426 announcements and fed early strategy generators (`Option B` / `V5 HQ`). Running `deep_self_audit.py` on August 1, 2026 flagged three flaws: intraday GTT stop assumptions created INR 21,087 of phantom gains, stocks under INR 50 were falsely treated as margin-eligible, and `"Opening"` / `"Closure"` keywords in filing headlines were misclassified. The pipeline subsequently enforced a strict `Close >= INR 50.00` price floor and `Avg_Vol_20D >= 100,000` liquidity gate.

### Wave 2: Causal feature pipeline and block-bootstrap validation (`2026-08-05` to `2026-08-26`)

Crawling scaled to 857,928 raw announcements across 5,467 BSE tickers (`2023-12-15` to `2026-08-04`), enforcing `PRE_MARKET` and `POST_MARKET` timestamp causality to yield 345,143 clean pairs across 3,377 securities. Naive IID trade-reshuffling Monte Carlo (which destroys cross-sectional crash correlation across open slots) was replaced with a 10,000-run 5-day date-level block bootstrap alongside a stress test covering the June 4, 2024 Indian election selloff.

### Wave 3: Systematic pipelines and evolutionary self-critique (`2026-08-28` to `2026-08-31`)

A 10-step research pipeline, 10-generation evolutionary engines (`Gen 1` to `Gen 10`), and 4 goal phases explored broader variations. An internal audit script (`critical_flaw_audit_gen10.py`) proved that 4 out of 10 evolutionary generations produced no-op updates and flagged `Prior_RVOL` confounding, triggering a clean rebuild into `Config E` and `Config E-Pro`.

### Wave 4: Institutional execution modeling and signal pruning (`2026-08-29` to `2026-09-06`)

The engine adopted the full 8-item Indian delivery friction schedule (Zerodha `INR 20.00` per leg brokerage, `0.10%` buy and sell STT, `0.015%` buy stamp duty, `0.00345%` exchange turnover fee, `0.0001%` SEBI fee, `18%` GST, and `INR 15.93` CDSL DP debit fee) plus `60 bps` round-trip slippage. It replaced in-sample `Net_Ret` ranking with pre-open `Elasticity = (Prior_RVOL * |Gap_Pct|) / ATR_Pct`, switched to equal 3-slot sizing (`pre_open_equity / 3`, capped at 10% of 20-day dollar volume, integer shares, INR 5,000 minimum ticket, and 0% idle-cash yield after explicitly rejecting 6.5% p.a. cash-sweep variants), and pruned a 4th satellite setup (`SMA50_DEEP_DIP_1D`) after trade attribution showed `-INR 4,060.87` net PnL (`0.663` profit factor).

---

## Cross-model adversarial auditing and CDP tooling

Three separate verification channels audited the codebase and trade ledgers to catch single-model blind spots:

1. Custom adversarial subagent (`deep_flaw_auditor`) instructed to reject flattering results and inspect lookahead, survivorship, and execution assumptions.
2. Independent Claude Opus 4.6 audits (`2026-08-31`) verifying fee math and Monte Carlo behavior, catching a `0.00375%` BSE turnover rate discrepancy and reclassifying marginal post-friction trades (dropping an earlier prototype win rate from `64.7%` to `61.8%`).
3. A Chrome DevTools Protocol (CDP) WebSocket bridge (`astra_bridge.py` targeting Chromium on `127.0.0.1:9222`) driving ClickUp Brain GPT-6 Astra (`2026-09-06`). Because ClickUp Brain capped GPT-6 Astra at 25 prompts per account with no API, the local bridge automated `DOM.setFileInputFiles` uploads, rich-text prompt injection, and DOM response capture to run three full source-code and CSV audit rounds.

### Three-round GPT-6 Astra audit progression (September 6, 2026)

| Audit round | Target artifact | Auditor verdict | Findings and fixes |
| :-: | :--- | :--- | :--- |
| Round 1 | `Config E-Pro` prototype (`+50%` ROI, `4.2%` MDD) | "Fundamentally Flawed / Overfitted" | Exposed `cap += pnl` same-day future-PnL lookahead, serialized cost-basis drawdown masking, 10 calendar exits on closed BSE holidays, synthetic `Volume = 0` forward-fill bars, negative-expectancy `SMA50_DEEP_DIP_1D`, and fee mismatches. |
| Round 2 | `pure_event_driven_config_e.py` | "Not institutionally sound" | Rebuilt an event-driven loop, but Astra proved exits still ran before entries in the daily loop (allowing exit cash to fund same-day `09:15` buys in an early 2025 trade) and daily MTM still summed entry cost basis instead of live closing prices. |
| Round 3 | `rigorous_event_driven_config_e.py` | Two final state/fill bugs caught | Confirmed pre-open entries ran before exits, then caught an unbound `hist` loop variable in Event 3 MTM (pricing multiple active positions from one ticker's history) and nominal stop-loss fills on overnight gap-downs. |
| Final | `final_flawless_config_e.py` | Clean audit pass | Rebound per-ticker `hist` inside Event 3 MTM, enforced `min(sl_nominal, open)` and `max(tp_nominal, open)` gap fills, rebuilt 649 verified BSE sessions (`Volume > 0 & High > 0 & Open > 0`), and pruned `SMA50_DEEP_DIP_1D`. |

---

## Six simulation bugs eliminated in Config E

| # | Bug fixed | Root cause and remediation |
| :-: | :--- | :--- |
| 1 | Same-day $F_{t-}$ capital lookahead | Enforced a 3-event daily loop (`Event 1` 09:15 pre-open snapshot and slot sizing using prior close `< cur_date` and carried-over cash; `Event 2` 15:15/15:30 exits crediting cash strictly after `Event 1` finishes; `Event 3` 15:30 EOD mark-to-market). |
| 2 | Cost-basis drawdown masking and `hist` leak | Replaced entry cost-basis sums and the unbound dataframe variable with explicit per-position daily closing valuation across every session (`4.64%` 12M MDD, `6.91%` 24M MDD). |
| 3 | 10 bogus exits on 7 closed BSE holidays | Earlier scripts sliced dates from announcement `Trade_Date` columns, forcing 10 exits across 7 holidays (`2025-08-27`, `2025-10-02`, `2025-11-05`, `2026-03-03`, `2026-03-31`, `2026-04-14`, `2026-05-28`). Building the calendar strictly from `Volume > 0 & High > 0 & Open > 0` across 5,467 tickers yielded 649 authentic BSE sessions and 0 holiday exits. |
| 4 | Synthetic circuit locks from price forward-fills | Diagnostics found 109 tickers with `Volume = 0.0` flat OHLC rows on `2025-10-02` and synthetic flat rows on `2026-03-26` and `2026-03-31`. Purging `Volume <= 0` bars removed synthetic locks while preserving genuine circuit-freeze rollovers when `High == Low` occurs on real volume (verified in 24M `Trade #47`, deferred from 2 days to 4 days, `+22.33%` net return, `+INR 9,257.58`). |
| 5 | Gap-through stop illusions | Replaced theoretical stop-loss fills with conservative `min(sl_nominal, open)` fills on downside gaps and `max(tp_nominal, open)` on upside gaps. |
| 6 | Negative-expectancy satellite dilution | Removed `SMA50_DEEP_DIP_1D` (`-INR 4,060.87`, `0.663` PF), leaving only the 3 FDR-certified setups. |

---

## Six pipeline lookahead biases verified by `verify_metrics.py`

| # | Bias category | Legacy pipeline flaw | Config E remedy |
| :-: | :--- | :--- | :--- |
| 1 | Signal deduplication | Sorted competing same-day signals by realized `Net_Ret`. | Causal pre-open `(Priority, Elasticity)` ranking queue. |
| 2 | Liquidity sizing | Sized orders using execution-day traded volume. | Capped position notional at `10%` of historical `ADV20 * T-1 Close`. |
| 3 | Announcement timing | Triggered on intraday releases without execution delay. | Enforced `POST_MARKET` and `PRE_MARKET` filtering only. |
| 4 | Sizing model | Applied full-sample Kelly sizing. | Equal 3-slot `pre_open_equity / 3` allocation with pre-open cash locks. |
| 5 | Monte Carlo correlation | Reshuffled individual trades independently. | 5-day stationary date-block bootstrap preserving crash clustering (10,000 validation runs). |
| 6 | Execution pricing and fees | Assumed theoretical stops and omitted CDSL DP fees. | Gap-through fills, `60 bps` slippage, delivery STT, and `INR 15.93` DP charges. |

---

## Statistical significance and outlier checks

Benjamini-Hochberg FDR control ($P_{(i)} \le \frac{i}{m} Q$) ran across $m = 526$ signal specifications (303,402 evaluations, cited conservatively as 301,000+ tests in `verify_metrics.py`) at $Q = 0.10$, leaving 3 passing setups ($p < 0.01$).

Outlier sensitivity checks on the anonymized trade ledgers show that removing the single largest 12M OOS win (`Trade #18`, `+32.39%`, `+INR 10,860.43`) leaves 60 trades returning `+INR 32,716.94` (`+32.72%` fixed-ledger ROI) at `2.47` profit factor. Removing both 24M trades on the top outlier ticker (`Trades #55` and `#75`, `+INR 2,818.79` and `+INR 16,815.75`) leaves 116 trades returning `+INR 104,092.79` (`+104.09%` fixed-ledger ROI) at `2.90` profit factor.
