from dataclasses import dataclass
from datetime import datetime
from typing import Literal

# Allowed values for frame_type; type checkers flag any other value
FrameType = Literal["beacon", "probe_req", "deauth", "disassoc"]


@dataclass(frozen=True, slots=True)
class FrameEvent:
    """
    Represents one captured 802.11 management frame
    Note: time is in timezone aware UTC established by parse()
    """

    time: datetime
    sensor_id: str
    frame_type: FrameType
    src_mac: str
    dst_mac: str
    bssid: str
    ssid: str | None
    channel: int | None
    rssi_dbm: int | None
    reason_code: int | None
