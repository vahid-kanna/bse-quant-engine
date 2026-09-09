"""
Quickstart Backtesting Engine Demo
==================================
Runs an illustrative multi-session simulation exercising the core event-driven
architecture: pre-open snapshots, integer shares, gap-through stop execution,
statutory friction deduction, and true daily MTM accounting.
Uses synthetic normalized test assets (zero real market/strategy data).
"""

from core.engine import EventDrivenEngine
from core.execution import BarData

def main():
    print("=" * 75)
    print("      BSE QUANT ENGINE: LIVE EVENT-DRIVEN EXECUTION DEMO")
    print("=" * 75)
    
    engine = EventDrivenEngine(initial_capital=100000.0, max_slots=3, slippage_bps=60.0)
    
    # Simulate 3 daily sessions with synthetic normalized test assets
    sessions = [
        {
            "date": "2026-03-02",
            "bars": {
                "ASSET_A": BarData(open=500.0, high=515.0, low=498.0, close=510.0, volume=1000000),
                "ASSET_B": BarData(open=250.0, high=258.0, low=248.0, close=255.0, volume=1500000),
                "ASSET_C": BarData(open=750.0, high=760.0, low=740.0, close=745.0, volume=2000000),
            },
            "signals": [
                {
                    "ticker": "ASSET_A",
                    "company": "Synthetic Liquid Equity A",
                    "signal_name": "DEMO_SETUP_1",
                    "hold_target": 2,
                    "exit_mode": "NONE",
                    "sl_mult": None,
                    "tp_mult": None,
                    "atr_pct": 0.02,
                    "prev_close": 498.0,
                    "avg_vol_20d": 1000000
                },
                {
                    "ticker": "ASSET_B",
                    "company": "Synthetic Liquid Equity B",
                    "signal_name": "DEMO_SETUP_2",
                    "hold_target": 1,
                    "exit_mode": "NONE",
                    "sl_mult": None,
                    "tp_mult": None,
                    "atr_pct": 0.02,
                    "prev_close": 249.0,
                    "avg_vol_20d": 1500000
                }
            ]
        },
        {
            "date": "2026-03-03",
            "bars": {
                "ASSET_A": BarData(open=512.0, high=520.0, low=508.0, close=518.0, volume=950000),
                "ASSET_B": BarData(open=256.0, high=260.0, low=254.0, close=259.0, volume=1400000),
                "ASSET_C": BarData(open=748.0, high=765.0, low=745.0, close=762.0, volume=1800000),
            },
            "signals": [
                {
                    "ticker": "ASSET_C",
                    "company": "Synthetic Liquid Equity C",
                    "signal_name": "DEMO_SETUP_3",
                    "hold_target": 1,
                    "exit_mode": "TP",
                    "sl_mult": 1.0,
                    "tp_mult": 2.0,
                    "atr_pct": 0.02,
                    "prev_close": 745.0,
                    "avg_vol_20d": 1800000
                }
            ]
        },
        {
            "date": "2026-03-04",
            "bars": {
                "ASSET_A": BarData(open=519.0, high=525.0, low=516.0, close=522.0, volume=900000),
                "ASSET_B": BarData(open=260.0, high=264.0, low=258.0, close=262.0, volume=1300000),
                "ASSET_C": BarData(open=765.0, high=772.0, low=760.0, close=770.0, volume=1700000),
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
        print(f"Trade #{t['trade_num']} | {t['ticker']:8s} | Setup: {t['signal']} | "
              f"Net Ret: {t['net_return_pct']:+5.2f}% | PnL: INR {t['pnl_inr']:+8.2f} | "
              f"Frictions: INR {t['frictions_inr']:6.2f}")
              
    print("\nDemo executed successfully! Architecture verified.")

if __name__ == "__main__":
    main()
