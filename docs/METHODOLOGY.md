# Methodology & Empirical Framework

## 1. Dataset & Universe Construction

The empirical universe comprises equities actively listed on the **Bombay Stock Exchange (BSE)** over a 24-month horizon (649 verified continuous market trading sessions).

### Data Ingestion & Sanitization Pipeline
1. **Raw Filings Ingestion:** 857,928 corporate regulatory announcements, board meeting outcomes, quarterly disclosures, and structural corporate events.
2. **Causal Deduplication:** Filtered to 345,143 clean stock-date pairs by enforcing point-in-time publication timestamps.
3. **Institutional Liquidity Filters:**
   - Historical 20-Day Average Daily Volume: $\text{ADV}_{20} \ge 100,000$ shares.
   - Minimum Share Price: $P_{\text{close}} \ge \text{INR } 50.00$ (eliminates micro-penny stocks and extreme tick distortions).
   - Non-Circuit Auction Spread: $P_{\text{high}} \ne P_{\text{low}}$ on event evaluation date.
   - Gap Anomaly Guard: $|\text{Gap Pct}| \le 15.0\%$ (prevents extreme corporate restructuring artifacts).
   - Execution Causality: Announcements strictly released post-market ($\ge 16:00\text{ IST}$) or pre-market ($< 09:00\text{ IST}$).

---

## 2. Mathematical Performance Formulas

All performance metrics reported in the verification tear sheets are calculated as follows:

### Net Return on Investment (Net ROI)
$$\text{Net ROI} = \left(\frac{\text{Ending Portfolio Equity}}{\text{Starting Capital}} - 1\right) \times 100\%$$

### Annualized Compound Growth Rate (CAGR)
$$\text{CAGR} = \left[\left(\frac{\text{Ending Portfolio Equity}}{\text{Starting Capital}}\right)^{\frac{365.25}{D}} - 1\right] \times 100\%$$
Where $D = 709$ calendar days across the 24-month horizon.

### Profit Factor (PF)
$$\text{Profit Factor} = \frac{\sum \text{Gains}_{\text{net positive}}}{\left|\sum \text{Losses}_{\text{net negative}}\right|}$$
Where gains and losses are evaluated **strictly after all statutory taxes, brokerage, and depository charges**.

### True Daily Mark-to-Market Drawdown (MTM MDD)
$$\text{Drawdown}_t = \frac{\max_{\tau \le t}(\text{Equity}_\tau) - \text{Equity}_t}{\max_{\tau \le t}(\text{Equity}_\tau)}$$
$$\text{Max Drawdown} = \max_{t \in [0, T]}(\text{Drawdown}_t)$$
Evaluated daily at 15:30 IST across all open active positions.

### Calmar Ratio
$$\text{Calmar Ratio} = \frac{\text{Net ROI}}{\text{Max Drawdown}}$$
*(Or $\text{CAGR} / \text{Max Drawdown}$ for multi-year horizons).*

---

## 3. Intellectual Property Notice
The proprietary natural language processing (NLP) catalyst taxonomy, feature weighting matrices, and alpha parameters are retained as proprietary intellectual property. 

All execution logs, daily equity curves, and performance verification artifacts are published in the `data/` directory to enable 100% independent verification of all cited metrics.
