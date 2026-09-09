"""
Statutory & Institutional Friction Model for Indian Equity Markets
==================================================================
Accurately models the statutory tax structure, exchange fees, depository
charges, and execution slippage for Indian equity delivery transactions.
"""

from dataclasses import dataclass
from typing import Tuple, Dict

@dataclass
class StatutoryFrictionModel:
    slippage_bps: float = 60.0              # 60 bps (0.60%) round-trip execution slippage
    stt_buy: float = 0.0010                 # 0.10% Securities Transaction Tax (Buy Delivery)
    stt_sell: float = 0.0010                # 0.10% Securities Transaction Tax (Sell Delivery)
    stamp_duty_buy: float = 0.00015         # 0.015% State Stamp Duty (Buy Delivery only)
    exchange_turnover: float = 0.0000345    # 0.00345% BSE/NSE Exchange Transaction Fee
    sebi_turnover: float = 0.000001         # 0.0001% SEBI Regulatory Turnover Fee
    brokerage_per_leg: float = 20.0         # INR 20.0 flat brokerage per executed order leg
    gst_rate: float = 0.18                  # 18% GST applicable on (Brokerage + Exchange + SEBI)
    dp_charges: float = 15.93               # CDSL/NSDL Depository Participant charge per sell transaction

    def calculate_roundtrip_friction(self, pos_size_inr: float, net_return_pct: float) -> Tuple[float, float, Dict[str, float]]:
        """
        Calculates post-execution net PnL and statutory friction breakdown.
        
        Args:
            pos_size_inr: Total capital deployed at market entry (INR).
            net_return_pct: Price return after execution slippage (decimal, e.g. 0.02 for +2%).
            
        Returns:
            Tuple of (net_pnl_inr, total_frictions_inr, detailed_fee_breakdown_dict)
        """
        buy_val = pos_size_inr
        sell_val = pos_size_inr * (1.0 + net_return_pct)
        
        stt = (buy_val * self.stt_buy) + (sell_val * self.stt_sell)
        stamp = buy_val * self.stamp_duty_buy
        exchange_fee = (buy_val + sell_val) * self.exchange_turnover
        sebi_fee = (buy_val + sell_val) * self.sebi_turnover
        brokerage = self.brokerage_per_leg * 2.0
        gst = (brokerage + exchange_fee + sebi_fee) * self.gst_rate
        dp_fee = self.dp_charges
        
        total_frictions = stt + stamp + exchange_fee + sebi_fee + brokerage + gst + dp_fee
        gross_pnl = buy_val * net_return_pct
        net_pnl = gross_pnl - total_frictions
        
        breakdown = {
            "stt": stt,
            "stamp_duty": stamp,
            "exchange_turnover": exchange_fee,
            "sebi_turnover": sebi_fee,
            "brokerage": brokerage,
            "gst": gst,
            "dp_charges": dp_fee,
            "total_frictions": total_frictions,
            "gross_pnl": gross_pnl,
            "net_pnl": net_pnl
        }
        return net_pnl, total_frictions, breakdown
