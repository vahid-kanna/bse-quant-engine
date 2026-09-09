"""
BSE Event-Driven Quantitative Engine (Config E)
==============================================
Institutional backtesting and execution engine modeling statutory frictions,
gap-through stop-loss execution, point-in-time causality, and mark-to-market risk.
"""

from .engine import EventDrivenEngine
from .friction import StatutoryFrictionModel
from .risk import PortfolioRiskManager
from .execution import ExecutionHandler

__all__ = [
    "EventDrivenEngine",
    "StatutoryFrictionModel",
    "PortfolioRiskManager",
    "ExecutionHandler",
]
