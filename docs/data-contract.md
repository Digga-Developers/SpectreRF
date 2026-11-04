# Frame data contract

> **Status:** Draft for discussion (SRF-3). Becomes v1 once all three of us approve the PR.

This document defines the one record that flows through SpectreRF: the **`FrameEvent`**. The parser (`src/models.py`) creates it, the writer (`src/db.py`) stores it in the `frames` table, and the Grafana dashboards query it.

If code and this document disagree, the code is wrong. To change the contract, see [Changing this contract](#changing-this-contract).

---

## What gets stored

One row per captured 802.11 **management frame** of these four types. Everything else (data frames, control frames, other management subtypes) is ignored by the parser.

| `frame_type` | 802.11 subtype | What it is |
|---|---|---|
| `beacon` | 8 | An access point announcing its network |
| `probe_req` | 4 | A device asking which networks are nearby |
| `deauth` | 12 | A "you're disconnected" message |
| `disassoc` | 10 | A "you're disconnected" message (close cousin of deauth) |

Metrics such as device counts, top probed SSIDs and deauth floods are **not** stored. They are calculated from these rows with SQL (see [Metrics built on this contract](#metrics-built-on-this-contract)).

---

## Fields

| Field | Python type | Postgres type | Nullable | Description | Source (Scapy) |
|---|---|---|---|---|---|
| `time` | `datetime` (UTC, timezone-aware) | `TIMESTAMPTZ` | No | When the frame was captured | `pkt.time` |
| `sensor_id` | `str` | `TEXT` | No | Which capture machine recorded the frame | `SENSOR_ID` env var |
| `frame_type` | `str` | `TEXT` with `CHECK` | No | One of `beacon`, `probe_req`, `deauth`, `disassoc` | `Dot11.subtype` |
| `src_mac` | `str` | `MACADDR` | No | Transmitter of the frame | `Dot11.addr2` |
| `dst_mac` | `str` | `MACADDR` | No | Receiver of the frame. `ff:ff:ff:ff:ff:ff` means everyone | `Dot11.addr1` |
| `bssid` | `str` | `MACADDR` | No | The access point the frame relates to | `Dot11.addr3` |
| `ssid` | `str \| None` | `TEXT` | Yes, see rules | Network name | `Dot11Elt` with `ID == 0` |
| `channel` | `int \| None` | `SMALLINT` | Yes | Channel number: 1–14 (2.4 GHz), 32–177 (5 GHz) | `Dot11Elt` with `ID == 3`, else RadioTap `ChannelFrequency` |
| `rssi_dbm` | `int \| None` | `SMALLINT` | Yes | Received signal strength in dBm, a negative number | RadioTap `dBm_AntSignal` |
| `reason_code` | `int \| None` | `SMALLINT` | Yes, see rules | Reason given for the disconnection | `Dot11Deauth.reason` / `Dot11Disas.reason` |

---

## Which fields are filled for each frame type

| Field | `beacon` | `probe_req` | `deauth` | `disassoc` |
|---|---|---|---|---|
| `time`, `sensor_id`, `frame_type` | always | always | always | always |
| `src_mac`, `dst_mac`, `bssid` | always | always | always | always |
| `ssid` | network name, or `""` if hidden | requested name, or `""` for a wildcard probe | `NULL` | `NULL` |
| `channel` | from the beacon's DS Parameter Set | from RadioTap, else `NULL` | from RadioTap, else `NULL` | from RadioTap, else `NULL` |
| `rssi_dbm` | if the card reports it, else `NULL` | same | same | same |
| `reason_code` | `NULL` | `NULL` | always | always |

**`ssid` meanings:**

- `NULL`: this frame type never carries a network name.
- `""` (empty string): the frame has an SSID field, but it is blank. For a beacon, the network is hidden. For a probe request, the device is asking "any network?".
- Any other value: the actual name.

---

## Normalisation rules

The parser must apply these before a `FrameEvent` is created, so every consumer can rely on them.

1. **Time is always UTC and timezone-aware.** Convert with `datetime.fromtimestamp(pkt.time, tz=timezone.utc)`. In pcap replay with timestamp rebasing (SRF-11), `time` is the rebased time, not the original.
2. **MAC addresses are lowercase, colon-separated**, e.g. `a4:83:e7:12:9f:01`.
3. **SSIDs are decoded as UTF-8 with `errors="replace"`.** Invalid bytes become `�` instead of raising an error.
4. **An SSID made entirely of `\x00` bytes becomes `""`.** Hidden networks often send zero bytes, and Postgres `TEXT` cannot store them.
5. **Leading and trailing whitespace in SSIDs is kept.** `"Home "` and `"Home"` are different networks.
6. **Malformed frames are dropped.** If a required field cannot be read, `parse()` returns `None` and the frame is not stored. It never raises.

---

## Example records

```text
time                        sensor_id      frame_type  src_mac            dst_mac            bssid              ssid          channel  rssi_dbm  reason_code
2026-11-01 14:02:11.384+00  pi-livingroom  beacon      a4:83:e7:12:9f:01  ff:ff:ff:ff:ff:ff  a4:83:e7:12:9f:01  CoffeeShop    6        -58       NULL
2026-11-01 14:02:11.902+00  pi-livingroom  probe_req   3e:91:0c:aa:41:7d  ff:ff:ff:ff:ff:ff  ff:ff:ff:ff:ff:ff  ""            6        -71       NULL
2026-11-01 14:02:12.015+00  pi-livingroom  probe_req   3e:91:0c:aa:41:7d  ff:ff:ff:ff:ff:ff  ff:ff:ff:ff:ff:ff  HomeWiFi      6        -70       NULL
2026-11-01 14:02:13.550+00  pi-livingroom  deauth      a4:83:e7:12:9f:01  ff:ff:ff:ff:ff:ff  a4:83:e7:12:9f:01  NULL          6        -60       7
```

---

## Configuration

| Env var | Required | Default | Used for |
|---|---|---|---|
| `SENSOR_ID` | No | the machine's hostname | `sensor_id` on every row |

Add it to `.env.example`.

---

## Metrics built on this contract

For reference only. These are queries and continuous aggregates, not columns.

| Use case | Metric | Based on |
|---|---|---|
| Occupancy | Frames per second by type | count by `frame_type` |
| Occupancy | Unique client MACs | distinct `src_mac` where `frame_type = 'probe_req'` |
| Occupancy | Unique access points | distinct `bssid` where `frame_type = 'beacon'` |
| Occupancy | Devices by distance | `rssi_dbm` bands: near > −60, mid −60 to −75, far < −75 |
| Occupancy | Dwell time | last minus first `time` per `src_mac` |
| Probe tracking | Top probed SSIDs | count by `ssid` where `frame_type = 'probe_req' AND ssid <> ''` |
| Probe tracking | Wildcard vs directed probes | share of probes where `ssid = ''` |
| Probe tracking | Sticky clients | `src_mac` seen in N or more distinct hours |
| Security | Deauth rate per access point | count of deauths per `bssid` per 10 s |
| Security | Deauth flood | that count ≥ 30 (configurable) |
| Security | Broadcast deauths | deauths where `dst_mac = 'ff:ff:ff:ff:ff:ff'` |
| Security | Reason code breakdown | count by `reason_code` |

**Caveat:** phones use randomized MAC addresses, so "unique MACs" overcounts real devices. Label panels as MACs, not people, until SRF-20 adds a randomized-MAC flag.

---

## Changing this contract

The contract affects everyone's code, so changes follow a stricter process than normal PRs:

1. Open a PR that changes **this file first**, explaining why.
2. It needs approval from **all three** of us.
3. After it merges, update `src/models.py`, `database/init.sql` and any affected dashboards, in follow-up PRs or the same one.
4. Tell everyone to run `docker compose down -v` so their local database picks up the new schema.

Planned change: SRF-20 adds an `is_random_mac` column (and optional MAC hashing).

---

## Open questions for the SRF-3 call

Delete this section once decided.

- [ ] Are we happy with `time` instead of `ts`? (Grafana expects a column named `time`.)
- [ ] Should we also capture `probe_resp` (subtype 5), access points answering probes?
- [ ] Is `SENSOR_ID` defaulting to the hostname good enough, or should it be required?
- [ ] Should we add `freq_mhz` alongside `channel`? It removes the ambiguity between 2.4 GHz and 5 GHz/6 GHz channel numbers.
- [ ] Is 30 deauths in 10 seconds a sensible starting threshold?
