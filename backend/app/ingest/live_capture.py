import asyncio
import uuid
from typing import Callable, Any
from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)

class LiveCapture:
    """
    Simulates capturing live network traffic from an interface.
    In a real deployment, this would wrap PyShark or Scapy's sniff().
    """
    def __init__(self, interface: str = settings.CAPTURE_INTERFACE):
        self.interface = interface
        self._is_running = False

    async def start(self, on_packet_callback: Callable[[dict], Any]):
        self._is_running = True
        logger.info(f"Starting live capture on interface {self.interface}")
        
        while self._is_running:
            # Simulate waiting for a packet
            await asyncio.sleep(1.0)
            
            # Simulate a captured packet/flow
            dummy_flow = {
                "flow_id": str(uuid.uuid4()),
                "src_ip": "10.0.0.5",
                "dst_ip": "1.1.1.1",
                "src_port": 44321,
                "dst_port": 443,
                "protocol": "TCP",
                "bytes_out": 512,
                "duration": 0.5
            }
            on_packet_callback(dummy_flow)

    def stop(self):
        self._is_running = False
        logger.info("Stopped live capture.")
