from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Numeric, BigInteger, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.types import TypeDecorator
import uuid
import datetime
from app.db.session import Base

class ArrayType(TypeDecorator):
    """Platform-independent Array type that stores list in JSON on SQLite and ARRAY on PostgreSQL."""
    impl = JSON

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(String))
        else:
            return dialect.type_descriptor(JSON)

class NetworkFlow(Base):
    __tablename__ = "network_flows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    flow_id = Column(String(64), nullable=False, unique=True)
    src_ip = Column(String(45), nullable=False)
    dst_ip = Column(String(45), nullable=False)
    src_port = Column(Integer, nullable=False)
    dst_port = Column(Integer, nullable=False)
    protocol = Column(String(10), nullable=False, default="TCP")
    duration = Column(Numeric(10, 4), nullable=False, default=0.0)
    bytes_in = Column(BigInteger, nullable=False, default=0)
    bytes_out = Column(BigInteger, nullable=False, default=0)
    pkts_in = Column(Integer, nullable=False, default=0)
    pkts_out = Column(Integer, nullable=False, default=0)
    tcp_flags = Column(String(32), default="SYN-ACK")
    flow_rate_bps = Column(Numeric(14, 2), default=0.0)
    packet_rate_pps = Column(Numeric(12, 2), default=0.0)
    entropy = Column(Numeric(6, 4), default=0.0)
    ja3_hash = Column(String(64), default=None)
    is_attack = Column(Boolean, nullable=False, default=False)
    attack_type = Column(String(64), default="BENIGN")
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    extra_metadata = Column(JSON, default=dict)


class ThreatAlert(Base):
    __tablename__ = "threat_alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String(64), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=False)
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    attack_type = Column(String(64), nullable=False)
    source_ip = Column(String(45), nullable=False)
    target_ip = Column(String(45), nullable=False)
    target_port = Column(Integer)
    confidence_score = Column(Numeric(5, 4), nullable=False)
    contributing_bots = Column(ArrayType, nullable=False, default=[])
    bot_scores = Column(JSON, nullable=False, default={})
    evidence = Column(JSON, nullable=False, default={})
    status = Column(String(30), nullable=False, default="NEW")  # NEW, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    blockchain_tx_hash = Column(String(66), default=None)
    blockchain_verified = Column(Boolean, nullable=False, default=False)
    blockchain_block_num = Column(BigInteger, default=None)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class BotMetric(Base):
    __tablename__ = "bot_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bot_name = Column(String(64), nullable=False, unique=True)
    display_name = Column(String(128), nullable=False)
    status = Column(String(20), nullable=False, default="HEALTHY")  # HEALTHY, DEGRADED, OFFLINE, INITIALIZING
    version = Column(String(32), nullable=False, default="1.0.0")
    latency_ms = Column(Numeric(8, 2), nullable=False, default=0.0)
    cpu_percent = Column(Numeric(5, 2), nullable=False, default=0.0)
    memory_mb = Column(Numeric(8, 2), nullable=False, default=0.0)
    predictions_count = Column(BigInteger, nullable=False, default=0)
    threats_detected = Column(BigInteger, nullable=False, default=0)
    accuracy_score = Column(Numeric(5, 4), default=0.9850)
    f1_score = Column(Numeric(5, 4), default=0.9820)
    last_heartbeat = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class BlockchainLog(Base):
    __tablename__ = "blockchain_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String(64), ForeignKey("threat_alerts.alert_id", ondelete="CASCADE"), nullable=False)
    alert_hash = Column(String(66), nullable=False, unique=True)
    tx_hash = Column(String(66), nullable=False, unique=True)
    block_number = Column(BigInteger, nullable=False)
    contract_address = Column(String(42), nullable=False)
    sender_address = Column(String(42), nullable=False)
    gas_used = Column(BigInteger, nullable=False, default=45000)
    verified_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class DGADomain(Base):
    __tablename__ = "dga_domains"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String(255), nullable=False, unique=True)
    family = Column(String(64), nullable=False, default="benign")
    entropy = Column(Numeric(6, 4), nullable=False, default=0.0)
    vowel_ratio = Column(Numeric(5, 4), nullable=False, default=0.0)
    length = Column(Integer, nullable=False, default=0)
    is_dga = Column(Boolean, nullable=False, default=False)
    confidence = Column(Numeric(5, 4), nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class DNSQuery(Base):
    __tablename__ = "dns_queries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = Column(String(64), nullable=False, unique=True)
    client_ip = Column(String(45), nullable=False)
    server_ip = Column(String(45), nullable=False, default="8.8.8.8")
    query_name = Column(String(255), nullable=False)
    query_type = Column(String(10), nullable=False, default="A")
    response_code = Column(String(16), nullable=False, default="NOERROR")
    payload_size_bytes = Column(Integer, nullable=False, default=0)
    entropy = Column(Numeric(6, 4), nullable=False, default=0.0)
    is_tunneling = Column(Boolean, nullable=False, default=False)
    tunneling_score = Column(Numeric(5, 4), default=0.0)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(128), nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    min_severity = Column(String(20), nullable=False, default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    notify_critical = Column(Boolean, nullable=False, default=True)
    notify_high = Column(Boolean, nullable=False, default=True)
    notify_medium = Column(Boolean, nullable=False, default=True)
    notify_low = Column(Boolean, nullable=False, default=False)
    quiet_hours_enabled = Column(Boolean, nullable=False, default=False)
    quiet_hours_start_utc = Column(Integer, nullable=False, default=22)  # 22:00 UTC
    quiet_hours_end_utc = Column(Integer, nullable=False, default=6)     # 06:00 UTC
    rate_limit_per_hour = Column(Integer, nullable=False, default=20)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String(64), nullable=True)
    recipient = Column(String(255), nullable=False)
    channel = Column(String(32), nullable=False, default="email")  # email, slack, discord, webhook
    provider = Column(String(32), nullable=False, default="smtp")  # smtp, resend, sendgrid, console
    status = Column(String(32), nullable=False)  # SUCCESS, FAILED, RATE_LIMITED, QUIET_HOURS, SKIPPED
    subject = Column(String(255), nullable=True)
    error_message = Column(String, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    sent_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

