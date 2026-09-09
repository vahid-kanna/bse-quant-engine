"""
Portfolio Risk & Capacity Sizing Manager
========================================
Manages pre-open capital snapshots, slot allocation concurrency,
integer share sizing constraints, and liquidity participation ceilings.
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class PortfolioRiskManager:
    max_concurrent_slots: int = 3
    min_position_size_inr: float = 5000.0
    max_adv_participation_rate: float = 0.10  # Max 10% of historical 20-day ADV
    
    def compute_position_size(
        self,
        available_cash: float,
        pre_open_equity: float,
        open_price: float,
        prev_close: float,
        avg_vol_20d: float,
        free_slots: int
    ) -> Tuple[int, float]:
        """
        Computes discrete integer shares and capital allocation per slot.
        Enforces:
          1. Point-in-time pre-open equity partition (Pre-Open Equity / Max Slots).
          2. Hard cash constraint (cannot exceed available uncommitted cash).
          3. Historical ADV participation ceiling (strictly using T-1 metrics).
          4. Discrete integer share truncation (no fractional shares).
          5. Minimum viable order threshold.
          
        Returns:
            Tuple of (shares_to_buy, actual_position_capital_inr)
        """
        if free_slots <= 0 or available_cash < self.min_position_size_inr or open_price <= 0:
            return 0, 0.0
            
        target_slot_size = pre_open_equity / self.max_concurrent_slots
        liquidity_cap = avg_vol_20d * prev_close * self.max_adv_participation_rate
        
        desired_capital = min(target_slot_size, liquidity_cap)
        if desired_capital > available_cash:
            desired_capital = available_cash
            
        if desired_capital < self.min_position_size_inr:
            return 0, 0.0
            
        shares = int(desired_capital / open_price)
        if shares <= 0:
            return 0, 0.0
            
        actual_pos_size = shares * open_price
        if actual_pos_size > available_cash:
            return 0, 0.0
            
        return shares, actual_pos_size
