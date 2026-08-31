import asyncio
from typing import Callable, Any
from app.ingest.pcap_reader import PCAPReader
from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)

class ReplayEngine:
    """
    Replays flows from a PCAP or dataset file at a specified speed.
    """
    def __init__(self, filepath: str, speed_multiplier: float = settings.REPLAY_SPEED_MULTIPLIER):
        self.reader = PCAPReader(filepath)
        self.speed_multiplier = speed_multiplier
        self._is_running = False

    async def start(self, on_flow_callback: Callable[[dict], Any]):
        self._is_running = True
        logger.info(f"Starting replay engine for {self.reader.filepath} at {self.speed_multiplier}x speed")
        
        flows = self.reader.read_flows()
        for flow in flows:
            if not self._is_running:
                break
                
            on_flow_callback(flow)
            
            # Simulate real delays based on duration or timestamp delta
            delay = flow.get("duration", 0.1) / self.speed_multiplier
            await asyncio.sleep(delay)

        logger.info("Replay finished.")
        self._is_running = False

    def stop(self):
        self._is_running = False
        logger.info("Stopped replay engine.")
