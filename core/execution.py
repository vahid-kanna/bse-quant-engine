"""
Execution Microstructure & Realistic Order Fill Engine
======================================================
Models discrete order execution mechanics, realistic gap-through stop fills,
circuit lock rollover constraints, and exchange trading sessions.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class BarData:
    open: float
    high: float
    low: float
    close: float
    volume: float

class ExecutionHandler:
    def __init__(self, slippage_bps: float = 60.0):
        self.slippage_rate = slippage_bps / 10000.0  # 60 bps = 0.0060

    def evaluate_exit(
        self,
        entry_price: float,
        days_held: int,
        hold_target: int,
        exit_mode: str,
        sl_mult: Optional[float],
        tp_mult: Optional[float],
        atr_pct: float,
        bar: BarData
    ) -> Tuple[bool, float, bool]:
        """
        Evaluates intraday order execution and realistic gap-through fills.
        
        Returns:
            Tuple of (is_exit_triggered, raw_execution_price, is_circuit_locked)
        """
        is_circuit = (bar.high == bar.low)
        is_exit = False
        exit_price = bar.close
        
        # 1. Evaluate Dynamic ATR-based Stop-Loss & Take-Profit with Gap-Through Fills
        if exit_mode == "TP" and sl_mult is not None and tp_mult is not None:
            es_dist = sl_mult * atr_pct
            sl_nominal = entry_price * (1.0 - es_dist)
            tp_nominal = entry_price * (1.0 + tp_mult * es_dist)
            
            # Gap-Down Stop Execution: If market opens below stop, fill at Open (worse fill)
            if bar.low <= sl_nominal:
                is_exit = True
                exit_price = min(sl_nominal, bar.open)
            # Gap-Up Profit Execution: If market opens above target, fill at Open (favorable fill)
            elif bar.high >= tp_nominal:
                is_exit = True
                exit_price = max(tp_nominal, bar.open)
                
        # 2. Evaluate Scheduled Holding Period Exit
        if not is_exit and days_held >= hold_target:
            # If stock is locked in circuit on exit date (High == Low), position cannot liquidate
            if is_circuit:
                return False, 0.0, True
            else:
                is_exit = True
                exit_price = bar.close
                
        return is_exit, exit_price, is_circuit

    def apply_slippage(self, raw_ret: float) -> float:
        """Applies round-trip execution slippage penalty."""
        return raw_ret - self.slippage_rate
