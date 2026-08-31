import time
from collections import defaultdict
from typing import Dict, Any, List

class SlidingWindowManager:
    """
    Manages sliding windows of network events to detect patterns
    over time (like port scanning or DDoS).
    """
    def __init__(self, window_size_seconds: int = 10):
        self.window_size = window_size_seconds
        # Stores flows grouped by source IP
        self.windows: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def add_event(self, event: Dict[str, Any]):
        src_ip = event.get("src_ip")
        if not src_ip:
            return
            
        current_time = time.time()
        event['_ts'] = current_time
        
        self.windows[src_ip].append(event)
        self._cleanup(current_time)

    def _cleanup(self, current_time: float):
        """Remove events outside the sliding window"""
        cutoff = current_time - self.window_size
        for ip in list(self.windows.keys()):
            self.windows[ip] = [e for e in self.windows[ip] if e['_ts'] >= cutoff]
            if not self.windows[ip]:
                del self.windows[ip]

    def get_aggregated_stats(self, src_ip: str) -> Dict[str, Any]:
        """Returns stats for a specific IP over the current window"""
        events = self.windows.get(src_ip, [])
        
        if not events:
            return {"count": 0, "unique_ports": 0, "total_bytes": 0}
            
        unique_ports = len(set(e.get("dst_port") for e in events if "dst_port" in e))
        total_bytes = sum(e.get("bytes_out", 0) for e in events)
        
        return {
            "count": len(events),
            "unique_ports": unique_ports,
            "total_bytes": total_bytes
        }

window_manager = SlidingWindowManager(window_size_seconds=10)
