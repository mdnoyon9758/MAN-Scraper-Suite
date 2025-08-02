"""
Initialize the automation package
"""

from .scheduler import Scheduler
from .notifications import NotificationManager

__all__ = ["Scheduler", "NotificationManager"]
