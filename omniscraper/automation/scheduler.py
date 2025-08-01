"""
Scheduler module for OmniScraper
"""

import schedule
import threading
import time
from typing import Callable, List

class Scheduler:
    """Handles scheduling of scraping tasks using 'schedule' library"""

    def __init__(self):
        self.jobs = []
        self._stop_event = threading.Event()

    def schedule_task(self, func: Callable, interval: int, unit: str = 'seconds'):
        """
        Schedule a task to run at a specified interval
        :param func: Function to run
        :param interval: Time interval
        :param unit: Time unit (seconds, minutes, hours, days)
        """
        if unit == 'seconds':
            job = schedule.every(interval).seconds.do(func)
        elif unit == 'minutes':
            job = schedule.every(interval).minutes.do(func)
        elif unit == 'hours':
            job = schedule.every(interval).hours.do(func)
        elif unit == 'days':
            job = schedule.every(interval).days.do(func)
        else:
            raise ValueError("Unsupported time unit")

        self.jobs.append(job)

    def run_pending(self):
        """Run all scheduled tasks that are pending"""
        schedule.run_pending()

    def start(self):
        """Start running the scheduler in a separate thread"""
        self._stop_event.clear()
        thread = threading.Thread(target=self._run_scheduler)
        thread.start()

    def _run_scheduler(self):
        """Internal method responsible for continuously running the scheduler"""
        while not self._stop_event.is_set():
            self.run_pending()
            time.sleep(1)

    def stop(self):
        """Stop the scheduler"""
        self._stop_event.set()

    def list_jobs(self) -> List[str]:
        """Return a list of currently scheduled jobs"""
        return [str(job) for job in self.jobs]

