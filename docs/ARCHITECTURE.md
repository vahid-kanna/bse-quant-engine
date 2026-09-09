# Event-Driven Architecture Specification

## Overview
The **BSE Quant Engine (Config E)** is architected to eliminate every vector of lookahead bias, execution ambiguity, and statistical inflation commonly present in academic equity backtests. 

The framework models discrete event dynamics on Indian cash equity markets (BSE/NSE) under strict regulatory settlement constraints ($T+1$ rolling delivery).

```
                      DAILY MARKET EVENT LIFECYCLE
                      
      09:00 AM                        09:15 AM                        15:15 PM                        15:30 PM
  [Pre-Open Auction]             [Market Open Fill]             [Intraday Risk/Exit]             [EOD MTM Audit]
          |                              |                               |                              |
  • Snapshot F_{t-} Marks        • Allocate Slots 1..3           • Evaluate ATR Stops            • Mark All Open Bars
  • Lock Pre-Market Cash         • Apply Discrete Shares         • Gap-Through Fill Check        • Compute Daily MTM
  • Causal Priority Queue        • Cap at 10% 20D-ADV            • Circuit Rollover Logic        • Record Peak & MDD
```

---

## 1. Causal Event Loop Breakdown

### Phase 1: 09:15 AM Pre-Open Allocation & Capital Snapshot
- **Information Set ($F_{t-}$):** Sizing calculations use strictly historical closing marks and prior uncommitted cash balances.
- **Pre-Market Cash Lock:** Any capital tied up in open positions exiting on day $T$ cannot be redeployed on day $T$ morning.
- **Integer Share Allocation:**
  $$\text{Shares} = \left\lfloor \frac{\min\left(\frac{\text{Pre-Open Equity}}{\text{Max Slots}}, \, 0.10 \times \text{ADV}_{20} \times P_{\text{close}, t-1}\right)}{P_{\text{open}, t}} \right\rfloor$$
  Fractional equity shares are strictly disallowed.

### Phase 2: 15:15 PM Intraday Execution & Microstructure Stops
- **Realistic Gap-Through Stop Execution:** If the opening auction gaps below a predetermined stop price, the trade fills at $P_{\text{open}}$ (the actual traded price), not the theoretical stop-loss mark.
- **Illiquidity Circuit Rollover:** If a stock hits a circuit freeze ($P_{\text{high}} = P_{\text{low}}$) on its scheduled liquidation date, liquidation is prohibited in that session and the position rolls forward into subsequent trading days until continuous two-sided liquidity is restored.

### Phase 3: 15:30 PM True Daily Mark-to-Market (MTM) Portfolio Valuation
- Portfolio equity is marked strictly on each constituent's actual session close price:
  $$\text{Equity}_t = \text{Cash}_t + \sum_{i=1}^{K} \left(\text{Shares}_{i, t} \times P_{\text{close}, i, t}\right)$$
- Peak equity and drawdown tracking are evaluated daily across all 649 continuous market trading sessions, preventing trade-exit smoothing.

---

## 2. Institutional Friction Schedule (Indian Equities)

All reported performance numbers are net of full statutory taxes, depository charges, and market impact slippage:

| Friction Component | Regulatory / Exchange Specification | Backtest Implementation |
| :--- | :--- | :--- |
| **Execution Slippage** | Round-trip auction gap & bid-ask spread | $60\text{ bps}$ ($0.60\%$) deducted from gross return |
| **Securities Transaction Tax (STT)** | CBDT Statutory Delivery Rate | $0.10\%$ on Buy + $0.10\%$ on Sell ($0.20\%$ RT) |
| **State Stamp Duty** | Indian Stamp Act (Equity Delivery) | $0.015\%$ on Buy turnover |
| **Exchange Turnover Fee** | BSE / NSE Transaction Charges | $0.00345\%$ on Total turnover |
| **SEBI Turnover Charge** | SEBI Regulatory Fee | $0.0001\%$ ($1\text{ per crore}$) on Total turnover |
| **Brokerage Fee** | Discount Brokerage Delivery Tariff | $\text{INR } 20.00$ flat per executed leg ($\text{INR } 40.00\text{ RT}$) |
| **Goods & Services Tax (GST)** | Ministry of Finance Statutory GST | $18.0\%$ on (Brokerage + Exchange + SEBI fees) |
| **Depository Charges (DP Fee)**| CDSL / NSDL Demat Debit Fee | $\text{INR } 15.93$ per delivery sell transaction |
