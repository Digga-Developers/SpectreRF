import os
import sys
import time
import signal

from scapy.all import sniff, Packet
from scapy.layers.dot11 import Dot11, RadioTap, Dot11ProbeReq, Dot11Elt


# TODO: implement full functionality
# - for now this is a test script to ensure functionality of packet monitoring

interface = os.getenv("WIRELESS_INTERFACE", "mon0")

def proc_packet(packet: Packet):
    """
    Processes passively captured packets collected via virtual monitor.
    Data is pulled from 802.11 layer and attempts to parse the MAC address
    MAC addresses are routinely randomized for anonymity, but can be tracked across a space

    Parameters
    ----------
    packet : Packet
        Incoming packet collected by user device
    """

    # check for 802.11 layer in the incoming packet
    if packet.haslayer(Dot11):
        dot11_layer = packet.getlayer(Dot11)

        # pull source MAC address from packet
        client_mac = getattr(dot11_layer, "addr2", None)
        if not client_mac:
            return
        
        # pull received signal strength indicator (RSSI) 
        # - measured in decibels relative to 1 milliwatt
        # - negative nums on log scale
        # - vals closer to 0 -> stronger signal
        rssi = "N/A" 
        if packet.haslayer(RadioTap):
            radio_tap = packet.getlayer(RadioTap)
            rssi = getattr(radio_tap, "dBm_AntSignal", "N/A")

        # Method 1: Capture Probe Requests
        if packet.haslayer(Dot11ProbeReq) and packet.haslayer(Dot11Elt):
            try:
                # attempt to collect target ssid foreign device is searching for
                elt_layer = packet.getlayer(Dot11Elt)
                ssid = elt_layer.info.decode("utf-8", errors='ignore')
            except Exception:
                ssid = "<hidden/empty>"
            print(f"[PROBE] MAC: {client_mac} | RSSI: {rssi} dBm | Searching for: '{ssid}'")

        # Method 2: Capturing from data frames
        elif dot11_layer.type == 2: # 2 == dataframe
            # On enterprise networks payloads are encrypted, but Layer 2 should still be visible
            # only print MAC & RSSI
            print(f"[DATA/ACTIVE] MAC: {client_mac} | RSSI: {rssi} dBm")

def signal_handler():
    print("\nShutting down sniffer cleanly...", flush=True)
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"Starting continuous telemetry stream on: {interface}", flush=True)
    
    # Continuous sniffing loop
    try:
        sniff(iface=interface, prn=proc_packet, store=False)
    except Exception as e:
        print(f"Capture error: {e}", file=sys.stderr, flush=True)
        sys.exit(1)