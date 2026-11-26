# Methodology and empirical framework

## 1. AI-assisted discovery and dataset construction

The research universe covers equities actively listed on the Bombay Stock Exchange (BSE) between `2023-12-15` and `2026-08-04`. Initial hypotheses came from manual observations in a desktop log and five spreadsheets tracking corporate disclosures and multi-day price behavior.

### Ingestion and causality pipeline

| Stage | Rule applied | Scale impact |
| :-: | :--- | :--- |
| Announcement crawling | Automated ingestion of BSE corporate filings | Scaled from 37,426 initial filings (July 2026) to 857,928 raw announcements across 5,467 tickers |
| Timestamp filtering | Bucketed dissemination timestamps into `PRE_MARKET`, `POST_MARKET`, and `INTRADAY`; dropped `INTRADAY` releases | Prevents same-session leaks so session $t$ depends strictly on pre-open data $F_{t-}$ |
| Exchange calendar | Built active dates solely from price bars where `Volume > 0 & High > 0 & Open > 0` across all 5,467 tickers | Produced 649 verified BSE sessions (481 in 24M, 231 in 12M OOS) and 0 holiday exits |
| Liquidity and price gates | Enforced $\text{ADV}_{20} \ge 100,000$ shares, $P_{\text{close}} \ge \text{INR } 50.00$, $P_{\text{high}} \ne P_{\text{low}}$, and no restructuring/delisting halts | Filtered the feed to 345,143 clean, causal stock-date pairs across 3,377 listed BSE securities |

---

## 2. Catalyst taxonomy, strategy pivot, and ranking

### Deterministic NLP classification and structural pivot

A rule-based regex and NLP taxonomy tagged regulatory filings across SAST Regulation 31 (promoter pledge creation, invocation, and release), LODR Regulation 30 (price-movement clarifications and material disclosures), equity dilution and QIP announcements, open offers, credit approvals/ratings, order wins, and quarterly financial results.

Early research evaluated shorting LODR Regulation 30 clarification spikes against long post-selloff setups. Because Indian cash equities lack practical overnight shorting outside F&O, the strategy pivoted to long-only event-driven setups combining gap dislocations, prior relative volume, and technical or catalyst alignment.

### Multiple-testing control and signal pruning

Across the clean dataset, 526 signal variations were tested over 303,402 evaluations (reported conservatively as 301,000+ tests in `verify_metrics.py`). Benjamini-Hochberg False Discovery Rate control ($Q = 0.10$) filtered out 523 snooped rules and retained 3 setups ($p < 0.01$), kept abstracted as `SETUP_1`, `SETUP_2`, and `SETUP_3` in the public ledgers. A fourth satellite signal (`SMA50_DEEP_DIP_1D`) was later pruned after trade attribution showed `-INR 4,060.87` net PnL (`0.663` profit factor).

### Pre-open priority and Elasticity ranking

To replace post-hoc `Net_Ret` deduplication, competing signals on the same morning are sorted by setup priority and a purely pre-open Elasticity score (defaulting `ATR_Pct` to `0.02` when missing or non-positive):

$$\text{Elasticity} = \frac{\text{Prior\_RVOL} \times |\text{Gap\_Pct}|}{\text{ATR\_Pct}}$$

Capital is split across at most 3 concurrent slots (`pre_open_equity / 3`), bounded by `10%` of 20-day dollar volume (`ADV20 * T-1 Close * 0.10`), truncated to integer shares, gated at a minimum `INR 5,000.00` order size, and kept at `0%` yield when sitting in idle cash.

---

## 3. Mathematical performance formulas

All performance metrics reported in the verification ledgers follow these definitions:

### Net return on investment (Net ROI)

$$\text{Net ROI} = \left(\frac{\text{Ending Portfolio Equity}}{\text{Starting Capital}} - 1\right) \times 100\%$$

### Annualized compound growth rate (CAGR)

$$\text{CAGR} = \left[\left(\frac{\text{Ending Portfolio Equity}}{\text{Starting Capital}}\right)^{\frac{365.25}{D}} - 1\right] \times 100\%$$

Where $D = 709$ calendar days across the 24-month horizon.

### Profit factor (PF)

$$\text{Profit Factor} = \frac{\sum \text{Gains}_{\text{net positive}}}{\left|\sum \text{Losses}_{\text{net negative}}\right|}$$

Gains and losses are evaluated strictly after `60 bps` slippage, statutory taxes, brokerage, and CDSL DP fees.

### True daily mark-to-market drawdown (MTM MDD)

$$\text{Drawdown}_t = \frac{\max_{\tau \le t}(\text{Equity}_\tau) - \text{Equity}_t}{\max_{\tau \le t}(\text{Equity}_\tau)}$$

$$\text{Max Drawdown} = \max_{t \in [0, T]}(\text{Drawdown}_t)$$

Evaluated daily at 15:30 IST across all open positions using live closing prices.

### Calmar ratio

$$\text{Calmar Ratio} = \frac{\text{Net ROI}}{\text{Max Drawdown}}$$

(Uses CAGR divided by Max Drawdown for the 24-month multi-year horizon.)

---

## 4. Intellectual property notice

The proprietary NLP catalyst regex triggers, token rules, and exact entry thresholds remain private under [LICENSE](../LICENSE). The full causal execution engine, friction schedules, anonymized trade and equity ledgers in `data/`, and verification scripts are published so every reported metric can be checked independently.
