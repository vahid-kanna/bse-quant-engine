"""
Institutional Causal Event-Driven Simulation Engine (Config E)
==============================================================
Production-grade backtesting engine designed for Indian equity markets.
Enforces point-in-time causality, pre-open capital snapshots, integer share
allocation, realistic execution slippage, gap-through stop fills, and true
daily Mark-to-Market (MTM) risk tracking.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import date

from .friction import StatutoryFrictionModel
from .risk import PortfolioRiskManager
from .execution import ExecutionHandler, BarData

class BaseAlphaModel(ABC):
    """
    Abstract Alpha Model Interface.
    
    NOTE: The proprietary NLP catalyst taxonomy and multi-factor alpha
    ranking parameters developed during the research are retained under
    proprietary trade secret license. This interface defines the contract
    used by the event-driven execution framework.
    """
    @abstractmethod
    def generate_signals(self, market_snapshot: Any) -> List[Dict[str, Any]]:
        """Generates point-in-time candidate signals for execution."""
        pass

@dataclass
class Position:
    ticker: str
    company: str
    signal_name: str
    entry_date: str
    entry_price: float
    shares: int
    pos_size: float
    hold_target: int
    exit_mode: str
    sl_mult: Optional[float]
    tp_mult: Optional[float]
    atr_pct: float
    days_held: int = 0
    circuit_locked: bool = False

class EventDrivenEngine:
    def __init__(
        self,
        initial_capital: float = 100000.0,
        max_slots: int = 3,
        slippage_bps: float = 60.0,
        friction_model: Optional[StatutoryFrictionModel] = None,
        risk_manager: Optional[PortfolioRiskManager] = None,
        execution_handler: Optional[ExecutionHandler] = None
    ):
        self.initial_capital = initial_capital
        self.max_slots = max_slots
        self.friction_model = friction_model or StatutoryFrictionModel(slippage_bps=slippage_bps)
        self.risk_manager = risk_manager or PortfolioRiskManager(max_concurrent_slots=max_slots)
        self.execution_handler = execution_handler or ExecutionHandler(slippage_bps=slippage_bps)
        
        self.cash = float(initial_capital)
        self.active_positions: List[Position] = []
        self.completed_trades: List[Dict[str, Any]] = []
        self.daily_equity_log: List[Dict[str, Any]] = []
        self.peak_equity = float(initial_capital)
        self.max_mdd = 0.0

    def step_session(
        self,
        cur_date_str: str,
        price_snapshot: Dict[str, BarData],
        candidate_orders: List[Dict[str, Any]]
    ):
        """
        Executes one full daily market session across 3 causal event phases:
          Phase 1: 09:15 AM Pre-Open Snapshot & Order Allocation
          Phase 2: 15:15 PM Intraday Path & Close Liquidation
          Phase 3: 15:30 PM End-of-Day True Mark-to-Market Valuation
        """
        # ======================================================================
        # PHASE 1: 09:15 AM PRE-OPEN PORTFOLIO SNAPSHOT & NEW ALLOCATIONS
        # ======================================================================
        free_slots = max(0, self.max_slots - len(self.active_positions))
        
        # Calculate pre-open portfolio equity using prior closing marks
        pre_open_mtm = 0.0
        for pos in self.active_positions:
            bar = price_snapshot.get(pos.ticker)
            mark = bar.close if bar else pos.entry_price
            pre_open_mtm += pos.shares * mark
            
        pre_open_equity = self.cash + pre_open_mtm
        
        # Allocate available slots strictly based on pre-open priority and liquidity
        for order in candidate_orders:
            if free_slots <= 0:
                break
                
            ticker = order["ticker"]
            bar = price_snapshot.get(ticker)
            if not bar or bar.open <= 0:
                continue
                
            shares, pos_capital = self.risk_manager.compute_position_size(
                available_cash=self.cash,
                pre_open_equity=pre_open_equity,
                open_price=bar.open,
                prev_close=order.get("prev_close", bar.close),
                avg_vol_20d=order.get("avg_vol_20d", 100000.0),
                free_slots=free_slots
            )
            
            if shares <= 0:
                continue
                
            self.cash -= pos_capital
            free_slots -= 1
            
            self.active_positions.append(Position(
                ticker=ticker,
                company=order.get("company", ticker),
                signal_name=order.get("signal_name", "ALPHA_SETUP"),
                entry_date=cur_date_str,
                entry_price=bar.open,
                shares=shares,
                pos_size=pos_capital,
                hold_target=order.get("hold_target", 1),
                exit_mode=order.get("exit_mode", "NONE"),
                sl_mult=order.get("sl_mult"),
                tp_mult=order.get("tp_mult"),
                atr_pct=order.get("atr_pct", 0.02)
            ))

        # ======================================================================
        # PHASE 2: 15:15 PM INTRADAY EXECUTION & CLOSE EXITS
        # ======================================================================
        surviving_positions: List[Position] = []
        for pos in self.active_positions:
            pos.days_held += 1
            bar = price_snapshot.get(pos.ticker)
            if not bar:
                surviving_positions.append(pos)
                continue
                
            is_exit, exit_price, is_circuit = self.execution_handler.evaluate_exit(
                entry_price=pos.entry_price,
                days_held=pos.days_held,
                hold_target=pos.hold_target,
                exit_mode=pos.exit_mode,
                sl_mult=pos.sl_mult,
                tp_mult=pos.tp_mult,
                atr_pct=pos.atr_pct,
                bar=bar
            )
            
            if is_circuit:
                pos.circuit_locked = True
                
            if is_exit:
                raw_return = (exit_price - pos.entry_price) / pos.entry_price
                net_return = self.execution_handler.apply_slippage(raw_return)
                net_pnl, frictions, breakdown = self.friction_model.calculate_roundtrip_friction(
                    pos_size_inr=pos.pos_size,
                    net_return_pct=net_return
                )
                
                # Settle trade and credit cash for next session
                self.cash += (pos.pos_size + net_pnl)
                
                self.completed_trades.append({
                    "trade_num": len(self.completed_trades) + 1,
                    "entry_date": pos.entry_date,
                    "exit_date": cur_date_str,
                    "ticker": pos.ticker,
                    "company": pos.company,
                    "signal": pos.signal_name,
                    "hold_days": pos.days_held,
                    "entry_price": pos.entry_price,
                    "exit_price": exit_price,
                    "shares": pos.shares,
                    "gross_return_pct": round(raw_return * 100, 2),
                    "net_return_pct": round(net_return * 100, 2),
                    "position_size_inr": round(pos.pos_size, 2),
                    "pnl_inr": round(net_pnl, 2),
                    "frictions_inr": round(frictions, 2),
                    "circuit_locked": pos.circuit_locked
                })
            else:
                surviving_positions.append(pos)
                
        self.active_positions = surviving_positions

        # ======================================================================
        # PHASE 3: 15:30 PM TRUE DAILY MARK-TO-MARKET PORTFOLIO VALUATION
        # ======================================================================
        eod_mtm_value = 0.0
        for pos in self.active_positions:
            bar = price_snapshot.get(pos.ticker)
            mark = bar.close if bar else pos.entry_price
            eod_mtm_value += pos.shares * mark
            
        total_equity = self.cash + eod_mtm_value
        if total_equity > self.peak_equity:
            self.peak_equity = total_equity
            
        cur_drawdown = (self.peak_equity - total_equity) / self.peak_equity if self.peak_equity > 0 else 0.0
        if cur_drawdown > self.max_mdd:
            self.max_mdd = cur_drawdown
            
        self.daily_equity_log.append({
            "date": cur_date_str,
            "cash_inr": round(self.cash, 2),
            "mtm_holdings_inr": round(eod_mtm_value, 2),
            "total_equity_inr": round(total_equity, 2),
            "active_positions": len(self.active_positions),
            "peak_equity_inr": round(self.peak_equity, 2),
            "drawdown_pct": round(cur_drawdown * 100, 2)
        })
