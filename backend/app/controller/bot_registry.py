import requests
import os
from typing import Dict, Any, List
from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)

class BotRegistry:
    def __init__(self):
        self.ai_service_url = os.getenv("AI_SERVICE_URL", "https://bots3-a8ta.onrender.com")
        self.active_bots = [
            "ddos_bot",
            "beaconing_bot", 
            "dga_dns_bot",
            "encrypted_malware_bot",
            "scanning_bot",
            "exfiltration_bot"
        ]

    def dispatch_to_bots(self, flow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Send a flow or aggregated window to all registered bots for inference.
        Returns a list of predictions.
        """
        import concurrent.futures
        predictions = []

        def call_single_bot(bot_name: str):
            try:
                response = requests.post(
                    f"{self.ai_service_url}/predict/{bot_name}", 
                    json=flow_data,
                    timeout=5.0
                )
                if response.status_code == 200:
                    res = response.json()
                    res["bot_name"] = bot_name
                    return res
                else:
                    logger.error(f"Failed to get prediction for {bot_name}: {response.status_code}")
            except Exception as e:
                logger.error(f"Error dispatching to {bot_name}: {e}")
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.active_bots)) as executor:
            results = executor.map(call_single_bot, self.active_bots)
            for res in results:
                if res:
                    predictions.append(res)
                    
        return predictions

bot_registry = BotRegistry()
