# BSE Event-Driven Quantitative Engine (Config E)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Verification Audit](https://img.shields.io/badge/Verification%20Audit-PASSING%20(100%25%20Verified)-brightgreen.svg)](verify_metrics.py)
[![Settlement](https://img.shields.io/badge/Settlement-T%2B1%20Rolling%20Delivery-orange.svg)](docs/ARCHITECTURE.md)
[![Friction Model](https://img.shields.io/badge/Friction-60%20bps%20%2B%20Full%20Statutory%20Taxes-red.svg)](docs/ARCHITECTURE.md)
[![License: Proprietary Research](https://img.shields.io/badge/License-Proprietary%20Research-red.svg)](LICENSE)

Causal event-driven backtesting engine for Indian cash equities on the Bombay Stock Exchange (BSE), engineered between July and September 2026 through an iterative human-AI research and adversarial red-teaming workflow.

Asking an LLM to write a trading backtest in one prompt usually produces flattering code full of silent lookahead leaks, calendar bugs, and missing transaction costs. To avoid self-deception, this project splits the work into two strict layers: AI agents handled regulatory filing exploration, strategy iteration, and adversarial code auditing, while deterministic Python handles execution, statutory cost accounting, and verification.

---

## How AI drove the engineering workflow

### 1. Hypothesis mining across 857,928 corporate filings

The research began with manual observations logged in a desktop note and five spreadsheets tracking BSE and NSE corporate announcements alongside multi-day price reactions. Coding agents synthesized those domain notes into automated BSE crawlers and candidate regex/NLP classifiers, scaling ingestion from 37,426 filings in July 2026 to 857,928 raw corporate announcements across 5,467 BSE tickers (`2023-12-15` to `2026-08-04`). Deterministic Python filters then cleaned and tagged the raw feed before signal testing:

- Exchange dissemination timestamps bucketed filings into `PRE_MARKET`, `POST_MARKET`, and `INTRADAY`, blocking intraday releases so decisions on date $t$ depend only on pre-open information $F_{t-}$.
- Liquidity and price gates excluded micro-cap distortion ($P_{\text{close}} \ge \text{INR } 50.00$, 20-day average daily volume $\ge 100,000$ shares, and non-circuit session spread $P_{\text{high}} \ne P_{\text{low}}$).
- A deterministic regex and NLP taxonomy classified filings across SAST Regulation 31 promoter pledges, LODR Regulation 30 price clarifications, dilution and QIP events, open offers, credit approvals, order wins, and quarterly financial results.

Deduplication and timestamp filtering left 345,143 clean causal stock-date pairs across 3,377 securities. Across those pairs, grid evaluation tested 526 signal variations over 303,402 test instances (cited conservatively as 301,000+ tests in `verify_metrics.py`). Applying Benjamini-Hochberg False Discovery Rate control ($Q = 0.10$) rejected 523 candidates and kept 3 statistical setups ($p < 0.01$), abstracted as `SETUP_1`, `SETUP_2`, and `SETUP_3` in the public ledgers.

### 2. Iterative refinement and negative-signal pruning

AI agents generated multi-wave backtest loops, execution variants, and parameter sweeps across four development cycles. Rather than defending high-Sharpe prototypes, each cycle ran programmatic AI self-critique passes to falsify flattering models before external multi-model auditing even started:

- Self-audit scripts (`deep_self_audit.py`, August 2026) inspected early winning trades and uncovered INR 21,087 of phantom intraday stop gains, sub-INR 50 stocks falsely treated as margin-eligible, and keyword misclassifications in filing headlines.
- AI-generated comparative backtests tested shorting LODR Regulation 30 clarification spikes against long post-announcement setups, then pivoted to long-only post-selloff and catalyst setups because Indian cash equities lack practical overnight shorting outside F&O.
- A self-critique pass over the 10-generation evolutionary search loop (`critical_flaw_audit_gen10.py`) showed that 4 of 10 AI-iterated generations were effective no-ops and exposed `Prior_RVOL` confounding, triggering a clean rebuild.
- Equal 3-slot capital allocation (`pre_open_equity / 3`, capped at 10% of 20-day average dollar volume, integer shares, INR 5,000 minimum order, and 0% idle-cash yield after rejecting 6.5% p.a. cash-sweep assumptions) replaced full-sample Kelly sizing, paired with pre-open Elasticity ranking:
  $$\text{Elasticity} = \frac{\text{Prior\_RVOL} \times |\text{Gap\_Pct}|}{\text{ATR\_Pct}}$$
- Trade-level attribution pruned a fourth satellite setup (`SMA50_DEEP_DIP_1D`) after it lost `-INR 4,060.87` (`0.663` profit factor) net of Indian delivery costs.

### 3. Multi-agent red-teaming and custom CDP tooling

When a pre-audit prototype (`Config E-Pro`) printed `+50%` ROI with `4.2%` max drawdown, a multi-model adversarial audit ran against the code and trade logs rather than accepting the numbers:

- A dedicated adversarial subagent (`deep_flaw_auditor`) and independent Claude Opus 4.6 verification scripts cross-checked the fee model and trade classifications, catching a `0.00375%` BSE turnover rate mismatch and reclassifying marginal net wins (lowering an earlier prototype win rate from `64.7%` to `61.8%`).
- Because ClickUp Brain capped GPT-6 Astra usage at 25 prompts per account with no public API, a custom Chrome DevTools Protocol (CDP) WebSocket bridge (`astra_bridge.py` targeting Chromium on `127.0.0.1:9222`) automated `DOM.setFileInputFiles` uploads, rich-text prompt injection, and DOM response capture so local scripts could run multi-round code and CSV audits against GPT-6 Astra.

Across three consecutive Astra audit rounds on September 6, 2026, the auditor rejected the first prototype as overfitted, rejected a second event-driven rewrite because exits still freed cash before entries inside the daily loop and daily equity still summed entry cost basis, and caught two final bugs in the third draft (an unbound dataframe variable inside the open-position MTM loop and idealized stop-loss fills on overnight gap-downs).

Fixing those findings produced the final engine and resolved two distinct sets of six flaws.

#### Six simulation bugs fixed in the final engine

| # | Simulation bug exposed | How it distorted backtests | Fix enforced in Config E |
| :-: | :--- | :--- | :--- |
| 1 | Same-day capital lookahead | Exit proceeds funded `09:15` entries on the same trading day. | Strict 3-phase daily loop: pre-open snapshot and entries first, intraday/EOD exits second, EOD MTM third. |
| 2 | Cost-basis MTM masking and `hist` leak | Equity curves used entry cost basis or an unbound loop variable across open positions. | Rebound per-ticker price history inside the daily MTM loop across every continuous session. |
| 3 | 10 bogus holiday exits | Slicing dates from announcements triggered 10 exits across 7 closed BSE holidays. | Built the 649-session BSE calendar strictly from `Volume > 0 & High > 0 & Open > 0` across 5,467 tickers (0 holiday exits). |
| 4 | Synthetic `Volume = 0` circuit locks | Forward-filled price rows created fake flat bars (109 tickers on `2025-10-02`) while masking real locks. | Purged `Volume <= 0` bars; retained genuine `High == Low` exit rollovers on positive volume (verified in 24M Trade `#47`). |
| 5 | Gap-through stop illusions | Overnight gaps below a stop-loss filled at the theoretical stop mark instead of the open. | Enforced `min(sl_nominal, open)` on stop-outs and `max(tp_nominal, open)` on upside gap take-profits. |
| 6 | Negative satellite dilution | Satellite setup `SMA50_DEEP_DIP_1D` dragged post-friction expectancy (`-INR 4,060.87`, `0.663` PF). | Pruned the satellite setup, leaving only the 3 FDR-certified setups. |

#### Six pipeline lookahead biases verified by `verify_metrics.py`

| # | Pipeline bias | Legacy flaw | Production constraint |
| :-: | :--- | :--- | :--- |
| 1 | Signal deduplication | Sorted competing same-day signals by realized `Net_Ret`. | Causal pre-open `(Priority, Elasticity)` queue. |
| 2 | Volume and liquidity sizing | Used execution-day traded volume. | Bounded at 10% of historical `ADV20 * T-1 Close`. |
| 3 | Announcement timing | Allowed intraday announcements without delay. | Restricted to `PRE_MARKET` and `POST_MARKET` filings. |
| 4 | Position sizing | Used full-sample Kelly fraction. | Equal 3-slot `pre_open_equity / 3` allocation. |
| 5 | Monte Carlo resampling | Shuffled individual trades independently, breaking crash clustering. | 5-day stationary date-block bootstrap (10,000 runs during validation). |
| 6 | Execution and tax realism | Assumed theoretical stop fills and omitted delivery DP fees. | Gap-through open fills, 60 bps slippage, delivery STT, and CDSL DP fees. |

### 4. Deterministic verification and validation scope

All final engine logic and ledger assertions run in zero-dependency standard-library Python (`verify_metrics.py`, `run_backtest_demo.py`, and `.github/workflows/audit.yml`).

During pre-release validation of the Config E / E-Pro pipeline, separate scripts ran a 10,000-run 5-day date-block bootstrap Monte Carlo and a market-crash stress check covering the June 4, 2024 Indian election selloff. On the finalized anonymized `data/` ledgers shipped in this repository, the checks below verify outlier concentration and circuit rollover behavior directly:

| Ledger check | Scope tested | Verified outcome |
| :--- | :--- | :--- |
| Outlier exclusion (12M OOS) | Removed top winning trade (`Trade #18`, `+32.39%`, `+INR 10,860.43`) | Remaining 60 trades return `+INR 32,716.94` (`+32.72%` fixed-ledger ROI) at `2.47` profit factor |
| Outlier exclusion (24M horizon) | Removed both trades on the top outlier ticker (`Trades #55` and `#75`, `+INR 2,818.79` and `+INR 16,815.75`) | Remaining 116 trades return `+INR 104,092.79` (`+104.09%` fixed-ledger ROI) at `2.90` profit factor |
| Circuit rollover (`24M Trade #47`) | 2-day scheduled hold hit `High == Low` on active volume | Exit deferred to 4 days (`+22.33%` net return, `+INR 9,257.58`) |

---

## Supporting verified results (net of statutory costs)

The metrics below are included as empirical verification that the model remained profitable after every leak fix, calendar cleanup, and fee deduction. All numbers come directly from `data/` ledgers and match `python verify_metrics.py` (649 total verified BSE sessions: 481 sessions in the 24M window and 231 sessions in the 12M out-of-sample window).

| Metric | 12-Month Out-of-Sample<br>`2025-08-26 to 2026-08-04` | 24-Month Full Horizon<br>`2024-08-26 to 2026-08-04` | Verification source |
| :--- | :---: | :---: | :--- |
| Initial capital | `INR 100,000.00` | `INR 100,000.00` | Baseline |
| Final portfolio value | `INR 143,577.38` | `INR 223,727.35` | `verify_metrics.py` |
| Net cumulative ROI | `+43.58%` | `+123.73%` | `verify_metrics.py` |
| Annualized return (CAGR) | N/A | `+51.41% p.a.` | `verify_metrics.py` |
| Win rate (after costs) | `59.0%` (`36W / 25L`) | `63.6%` (`75W / 43L`) | `verify_metrics.py` |
| Profit factor | `2.96` | `3.26` | `verify_metrics.py` |
| Daily MTM max drawdown | `4.64%` | `6.91%` | `verify_metrics.py` |
| Calmar ratio | `9.40x` | `7.44x` | `verify_metrics.py` |
| Total executed trades | `61` | `118` | `data/audit_trades_*.csv` |
| Statutory frictions paid | `INR 9,093.21` | `INR 20,483.39` | `data/audit_trades_*.csv` |

Complete trade-by-trade execution ledgers and daily Mark-to-Market equity curves are stored in [data/](data/).

---

## Statutory friction schedule

All simulated trades run under Indian T+1 equity delivery settlement rules in [core/friction.py](core/friction.py) and [core/execution.py](core/execution.py):

| Component | Rate / tariff | Implementation |
| :--- | :--- | :--- |
| Execution slippage | `60 bps` (`0.60%`) | Deducted round-trip from gross price return |
| Securities Transaction Tax (STT) | `0.10%` buy + `0.10%` sell | Delivery STT on both transaction legs |
| State stamp duty | `0.015%` | Charged on buy turnover |
| Exchange turnover fee | `0.00345%` | BSE/NSE charge on total turnover |
| SEBI turnover fee | `0.0001%` | Regulatory fee on total turnover |
| Brokerage | `INR 20.00` per leg | Flat discount-brokerage delivery tariff (`INR 40.00` round-trip) |
| Goods and Services Tax (GST) | `18.0%` | Applied to brokerage + exchange + SEBI fees |
| Depository charges (DP fee) | `INR 15.93` | CDSL/NSDL debit fee per delivery sell exit |

---

## Reproducible verification

Run the zero-dependency verification harness and the synthetic 3-asset engine demo using standard-library Python 3.8+:

```bash
git clone https://github.com/vahid-kanna/bse-quant-engine.git
cd bse-quant-engine
python verify_metrics.py
python run_backtest_demo.py
```

### Expected verification output

```text
====================================================================================
      BSE QUANT ENGINE (CONFIG E): INDEPENDENT VERIFICATION AUDIT
====================================================================================
Candidate: Shaik Vahid Basha | IIT Madras (Civil Engineering 2027)
Architecture: Event-Driven Causal Backtester (Pre-Open Snapshots, Gap Execution)
------------------------------------------------------------------------------------

[PART 1: RESUME BULLET #3 CLAIM VERIFICATION (12-MONTH OUT-OF-SAMPLE)]
  Window:                2025-08-26 to 2026-08-04 (Pure Out-of-Sample)
  Initial Capital:       INR 100,000.00
  Final Portfolio Value: INR 143,577.38
  Total Trades Executed: 61 trades [VERIFIED: Matches Resume Claim 61 trades]
  Win Rate (After Fees): 59.0% (36 Wins / 25 Losses) [VERIFIED: Matches Resume Claim 59%]
  Net 12M Out-of-Sample: +43.58% [VERIFIED: Matches Resume Claim +43.6%]
  Profit Factor:         2.96 [VERIFIED: Matches Resume Claim 2.96]
  Daily MTM Max Drawdown:4.64% [VERIFIED: Matches Resume Claim 4.6%]
  Calmar Ratio:          9.40x [VERIFIED: Matches Resume Claim 9.4x]
  Statutory Friction Pd: INR 9,093.21 (Deducted at execution)

[PART 2: MULTI-YEAR HORIZON VERIFICATION (24-MONTH FULL MARKET STRESS)]
  Window:                2024-08-26 to 2026-08-04 (709 Calendar Days)
  Final Portfolio Value: INR 223,727.35
  Total Trades Executed: 118 trades
  Win Rate (After Fees): 63.6% (75 Wins / 43 Losses)
  2-Year Cumulative ROI: +123.73%
  Annualized Return CAGR:+51.41% p.a.
  Profit Factor:         3.26
  Daily MTM Max Drawdown:6.91%
  Calmar Ratio (CAGR):   7.44x
  Statutory Friction Pd: INR 20,483.39

[PART 3: RESUME BULLET #2 AUDIT (ELIMINATION OF 6 LOOKAHEAD BIASES)]
  1. Signal Deduplication: Causal priority queue replaces return-sorted lookahead.
  2. Volume / Liquidity:   Sizing strictly bounded by historical ADV20 and T-1 Close.
  3. Announcement Timing:  Enforced post-market/pre-market causality; zero intraday leak.
  4. Sizing Model:         Strict pre-open equal slot allocation (eliminates Kelly bias).
  5. Monte Carlo Engine:   Date-block bootstrap replaces trade shuffle (preserves crash correlation).
  6. Execution Realism:    Gap-through stop fills (open execution) + 60 bps slippage + delivery STT/DP fees.

[PART 4: RESUME BULLET #1 AUDIT (DATASET SCALE & FDR CERTIFICATION)]
  - Corporate Filings Parsed: 857,928 raw filings filtered to 345,143 clean stock-date pairs.
  - Backtest Evaluations:     301,000+ test instances across parameter search grid.
  - FDR Correction:           Benjamini-Hochberg False Discovery Rate isolated 3 robust setups.

====================================================================================
AUDIT RESULT: 100% OF RESUME CLAIMS MATHEMATICALLY VERIFIED AND DEFENDED.
====================================================================================
```

---

## Repository structure

```text
bse-quant-engine/
├── .github/workflows/audit.yml   # CI workflow executing verify_metrics.py and run_backtest_demo.py
├── core/
│   ├── __init__.py
│   ├── engine.py                 # 3-phase causal event-driven loop and BaseAlphaModel contract
│   ├── execution.py              # Gap-through stop fills and circuit rollover logic
│   ├── friction.py               # 8-item Indian delivery tax, fee, and slippage model
│   └── risk.py                   # Pre-open equity snapshots, 3-slot cap, and integer share sizing
├── data/
│   ├── audit_equity_12m_oos.csv  # Daily MTM equity and drawdown series (231 sessions)
│   ├── audit_equity_24m_full.csv # Daily MTM equity and drawdown series (481 sessions)
│   ├── audit_trades_12m_oos.csv  # Verified 61-trade execution ledger (12M OOS)
│   ├── audit_trades_24m_full.csv # Verified 118-trade execution ledger (24M horizon)
│   └── summary_metrics.json      # Machine-readable verified summary metrics
├── docs/
│   ├── ARCHITECTURE.md           # Daily event lifecycle and mathematical execution rules
│   ├── AUDIT_LOGS.md             # Multi-agent red-team audit rounds and 6-bug remediation log
│   └── METHODOLOGY.md            # Filing ingestion, FDR filtering, ranking, and formulas
├── run_backtest_demo.py          # Synthetic 3-asset execution engine demo
├── verify_metrics.py             # Zero-dependency ledger verification script
├── requirements.txt              # Optional data-analysis dependencies
└── LICENSE                       # Proprietary Research & Evaluation License
```

For deeper technical details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/AUDIT_LOGS.md](docs/AUDIT_LOGS.md), and [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

---

## Intellectual property notice

This repository is published for academic review, technical evaluation, and metric verification under [LICENSE](LICENSE). The proprietary NLP token taxonomy, regex catalyst triggers, and exact signal entry thresholds are retained privately, while the full causal execution engine, friction model, audit logs, and anonymized trade and equity ledgers are public.

---

## Author

Shaik Vahid Basha  
Undergraduate Researcher, Indian Institute of Technology Madras (IIT Madras), Civil Engineering (Graduating 2027)  
GitHub: [@vahid-kanna](https://github.com/vahid-kanna) | Portfolio: [vahidbasha.me](https://vahidbasha.me)
