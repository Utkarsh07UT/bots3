from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class NetworkFlowBase(BaseModel):
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: Optional[str] = "TCP"
    duration: Optional[float] = 0.0
    bytes_in: Optional[int] = 0
    bytes_out: Optional[int] = 0
    pkts_in: Optional[int] = 0
    pkts_out: Optional[int] = 0
    tcp_flags: Optional[str] = "SYN-ACK"
    flow_rate_bps: Optional[float] = 0.0
    packet_rate_pps: Optional[float] = 0.0
    entropy: Optional[float] = 0.0
    ja3_hash: Optional[str] = None
    is_attack: Optional[bool] = False
    attack_type: Optional[str] = "BENIGN"
    extra_metadata: Optional[Dict[str, Any]] = {}

class NetworkFlowCreate(NetworkFlowBase):
    pass

class NetworkFlowResponse(NetworkFlowBase):
    id: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
