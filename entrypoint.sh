#!/bin/sh

# script exits if error is caught in the following code
set -e

# collect physical wireless interface passed from host
HOST_IFACE="${WIRELESS_INTERFACE}"

# define virtual monitor interface
# NOTE: 
# Virtual monitor is needed to avoid causing issues with device wifi card
# - prevents from mismatch in states and hanging when exiting program with primary interface
MON_IFACE="mon0"

# clean up func to close virtual montior interface
cleanup() {
  echo ""
  echo "Tearing down virtual monitor interface $MON_IFACE..."
  ip link set "$MON_IFACE" down 2>/dev/null || true
  iw dev "$MON_IFACE" del 2>/dev/null || true
  echo "Virtual interface removed. $HOST_IFACE was untouched."
}

# trap forced container shutdown and run cleanup script
trap cleanup EXIT INT TERM

echo "Creating virtual monitor interface $MON_IFACE on top of $HOST_IFACE..."

# ensure that no residual monitor interface is leftover (if failure occured with cleanup)
iw dev "$MON_IFACE" del 2>/dev/null || true

# establish virtual monitor interface without modifying primary interface
iw dev "$HOST_IFACE" interface add "$MON_IFACE" type monitor
ip link set "$MON_IFACE" up

# pass the virtual monitor to the app program
export WIRELESS_INTERFACE="$MON_IFACE"

echo "Interface $WIRELESS_INTERFACE is ready. Starting capture process..."

if [ $# -eq 0 ]; then
  set -- python3 src/capture.py
fi

exec "$@"