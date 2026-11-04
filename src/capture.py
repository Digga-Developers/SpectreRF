import os
import signal
import sys

from scapy.all import Dot11, sniff

# TODO: implement full functionality
# - for now this is a test script to ensure functionality of packet monitoring

interface = os.getenv("WIRELESS_INTERFACE", "mon0")


def handle_packet(packet):
    if packet.haslayer(Dot11):
        # Extract basic telemetry metrics
        bssid = packet.addr3
        rssi = getattr(packet, "dBm_AntSignal", None)
        print(
            f"[+] Captured 802.11 Frame | BSSID: {bssid} | Signal: {rssi} dBm",
            flush=True,
        )


def signal_handler(signum, frame):
    print("\nShutting down sniffer cleanly...", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"Starting continuous telemetry stream on: {interface}", flush=True)

    # Continuous sniffing loop
    try:
        sniff(iface=interface, prn=handle_packet, store=False)
    except (OSError, ValueError) as e:
        print(f"Capture error on {interface}: {e}", file=sys.stderr, flush=True)
        sys.exit(1)
