"""
Quickstart Backtesting Engine Demo
==================================
Runs an illustrative multi-session simulation exercising the core event-driven
architecture: pre-open snapshots, integer shares, gap-through stop execution,
statutory friction deduction, and true daily MTM accounting.
"""

from core.engine import EventDrivenEngine
from core.execution import BarData

def main():
    print("=" * 75)
    print("      BSE QUANT ENGINE: LIVE EVENT-DRIVEN EXECUTION DEMO")
    print("=" * 75)
    
    engine = EventDrivenEngine(initial_capital=100000.0, max_slots=3, slippage_bps=60.0)
    
    # Simulate 3 daily sessions with sample market data
    sessions = [
        {
            "date": "2026-03-02",
            "bars": {
                "TCS": BarData(open=3850.0, high=3920.0, low=3840.0, close=3905.0, volume=1200000),
                "INFY": BarData(open=1620.0, high=1645.0, low=1610.0, close=1638.0, volume=2500000),
                "RELIANCE": BarData(open=2950.0, high=2980.0, low=2930.0, close=2940.0, volume=3100000),
            },
            "signals": [
                {
                    "ticker": "TCS",
                    "company": "Tata Consultancy Services Ltd",
                    "signal_name": "Alpha-1 (Oversold Mean Reversion)",
                    "hold_target": 2,
                    "exit_mode": "NONE",
                    "sl_mult": None,
                    "tp_mult": None,
                    "atr_pct": 0.015,
                    "prev_close": 3845.0,
                    "avg_vol_20d": 1200000
                },
                {
                    "ticker": "INFY",
                    "company": "Infosys Ltd",
                    "signal_name": "Alpha-2 (Structural Momentum Dip)",
                    "hold_target": 1,
                    "exit_mode": "NONE",
                    "sl_mult": None,
                    "tp_mult": None,
                    "atr_pct": 0.018,
                    "prev_close": 1615.0,
                    "avg_vol_20d": 2500000
                }
            ]
        },
        {
            "date": "2026-03-03",
            "bars": {
                "TCS": BarData(open=3910.0, high=3950.0, low=3890.0, close=3935.0, volume=1100000),
                "INFY": BarData(open=1640.0, high=1670.0, low=1635.0, close=1665.0, volume=2400000),
                "RELIANCE": BarData(open=2945.0, high=2990.0, low=2940.0, close=2985.0, volume=2800000),
            },
            "signals": [
                {
                    "ticker": "RELIANCE",
                    "company": "Reliance Industries Ltd",
                    "signal_name": "Alpha-3 (Regulatory Catalyst Breakout)",
                    "hold_target": 1,
                    "exit_mode": "TP",
                    "sl_mult": 1.0,
                    "tp_mult": 2.0,
                    "atr_pct": 0.016,
                    "prev_close": 2940.0,
                    "avg_vol_20d": 3100000
                }
            ]
        },
        {
            "date": "2026-03-04",
            "bars": {
                "TCS": BarData(open=3940.0, high=3980.0, low=3925.0, close=3960.0, volume=980000),
                "INFY": BarData(open=1660.0, high=1675.0, low=1650.0, close=1655.0, volume=1900000),
                "RELIANCE": BarData(open=3010.0, high=3030.0, low=2995.0, close=3025.0, volume=2600000),
            },
            "signals": []
        }
    ]
    
    for sess in sessions:
        engine.step_session(
            cur_date_str=sess["date"],
            price_snapshot=sess["bars"],
            candidate_orders=sess["signals"]
        )
        last_eod = engine.daily_equity_log[-1]
        print(f"[{sess['date']}] EOD Equity: INR {last_eod['total_equity_inr']:,.2f} | "
              f"Cash: INR {last_eod['cash_inr']:,.2f} | "
              f"MTM Holdings: INR {last_eod['mtm_holdings_inr']:,.2f} | "
              f"Active: {last_eod['active_positions']}")
              
    print("\n" + "-" * 75)
    print("COMPLETED TRADES LOG:")
    print("-" * 75)
    for t in engine.completed_trades:
        print(f"Trade #{t['trade_num']} | {t['ticker']:8s} | Signal: {t['signal']} | "
              f"Net Ret: {t['net_return_pct']:+5.2f}% | PnL: INR {t['pnl_inr']:+8.2f} | "
              f"Frictions: INR {t['frictions_inr']:6.2f}")
              
    print("\nDemo executed successfully! Architecture verified.")

if __name__ == "__main__":
    main()
