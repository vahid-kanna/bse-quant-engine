# Quantitative Audit Trail & Evolutionary Journey

## Summary of Iterative Generations (Gen 1 – 10 & Config A – E)

The quantitative engine underwent ten evolutionary research phases and five major architectural configurations to reach the **Config E (Flawless Event-Driven)** production state.

```
+-----------------------------------------------------------------------------------------------+
|  GEN 1-3: In-Sample Mining & Initial Anomaly Detection                                        |
|  - 526 initial candidate signals evaluated across 857K+ corporate filings                     |
|  - High apparent Sharpe ratios identified, prompting immediate forensic red-teaming           |
+-----------------------------------------------------------------------------------------------+
                                                │
                                                ▼
+-----------------------------------------------------------------------------------------------+
|  GEN 4-6: Microstructure & Execution Audit                                                    |
|  - Detected Intraday Announcement Leaks: Enforced strict post-market (>=16:00) / pre-market   |
|  - Uncovered Missing DP Charges: Integrated mandatory CDSL INR 15.93 per sell ticket          |
|  - Rectified Intraday vs Delivery STT: Increased tax rate from 0.025% to 0.10% each side      |
+-----------------------------------------------------------------------------------------------+
                                                │
                                                ▼
+-----------------------------------------------------------------------------------------------+
|  GEN 7-9: Multi-Regime & Statistical Correction                                               |
|  - Applied Benjamini-Hochberg False Discovery Rate (FDR): Isolated 3 statistically robust     |
|    setups out of 301,000+ tests                                                               |
|  - Replaced IID Trade Reshuffling with Stationary Date-Block Bootstrapping to preserve        |
|    historical tail-risk clustering                                                            |
+-----------------------------------------------------------------------------------------------+
                                                │
                                                ▼
+-----------------------------------------------------------------------------------------------+
|  GEN 10 -> CONFIG E: Flawless Production Architecture                                         |
|  - Resolved Slot Accounting & Calendar Alignment: Mapped continuous 649 market trading days   |
|  - Implemented True Daily Mark-to-Market (MTM) accounting across all active positions         |
|  - Modeled Realistic Gap-Through Stops and Illiquidity Circuit Rollovers                      |
+-----------------------------------------------------------------------------------------------+
```

---

## The 6 Eliminated Lookahead Biases & Flaws

| # | Bias / Structural Vulnerability | Legacy Implementation Flaw | Config E Production Remedy |
| :-: | :--- | :--- | :--- |
| **1** | **Signal Deduplication Lookahead** | Sorted same-day competing signals by realized net return (`Net_Ret`). | Replaced with causal Priority and pre-market Elasticity ranking before market open. |
| **2** | **Liquidity Sizing Lookahead** | Sized order limits using execution-day traded volume. | Restricted participation ceilings strictly to historical 20-day ADV ($\text{ADV}_{20}$) and $T_{-1}$ close. |
| **3** | **Announcement Timestamp Leak** | Parsed intraday regulatory announcements without execution delay. | Enforced strict post-market ($>16:00$) / pre-market ($<09:00$) filtering; execution shifted to next open. |
| **4** | **In-Sample Dynamic Sizing Bias** | Applied Kelly Criterion sizing derived from full-sample win rates. | Enforced equal-weight discrete slot allocation ($33.3\%$ per slot) with pre-open cash locking. |
| **5** | **Monte Carlo Correlation Distortion**| Reshuffled individual trade returns independently, destroying crash regime correlation. | Implemented stationary 5-day date-block bootstrap resampling to preserve volatility clustering. |
| **6** | **Unrealistic Fill Pricing & Fee Understatement** | Assumed theoretical stop-loss fills during severe gap-downs; omitted DP fees. | Enforced gap-through slippage (fill at open if open < stop), $60\text{ bps}$ friction, and statutory CDSL DP charges. |

---

## Statistical Significance & FDR Control

To control for multi-testing data snooping (family-wise error rate), the **Benjamini-Hochberg False Discovery Rate (FDR)** procedure was applied across the 526 initial candidate signal variations:

$$P_{(i)} \le \frac{i}{m} Q$$

Where:
- $m = 526$ signal specifications evaluated across 301,000+ stock-date tests.
- $Q = 0.10$ FDR significance threshold.
- Exactly **3 structural setups** passed FDR control, exhibiting genuine post-cost alpha decoupled from market beta.
