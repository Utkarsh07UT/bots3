import time
from typing import Dict

class MetricsRegistry:
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.start_time = time.time()

    def increment(self, metric_name: str, amount: int = 1):
        if metric_name not in self.counters:
            self.counters[metric_name] = 0
        self.counters[metric_name] += amount

    def set_gauge(self, metric_name: str, value: float):
        self.gauges[metric_name] = value

    def get_throughput(self) -> float:
        """Returns overall flows per second since startup"""
        total_flows = self.counters.get("flows_ingested", 0)
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            return round(total_flows / elapsed, 2)
        return 0.0

    def summary(self) -> dict:
        return {
            "counters": self.counters,
            "gauges": self.gauges,
            "throughput_fps": self.get_throughput(),
            "uptime_seconds": round(time.time() - self.start_time, 2)
        }

metrics = MetricsRegistry()
