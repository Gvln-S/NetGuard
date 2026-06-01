# [EdgeSentinel: Automated Network Defense](https://github.com/Gvln-S/NetGuard/)

An enterprise-grade Active Intrusion Prevention System (IPS) deployed at the edge. This project re-architects a standard home network infrastructure into a segmented, highly monitored environment using a hardware-managed **Cisco Catalyst 2960-X** switch, a production server ecosystem, and an edge computing node powered by a **Raspberry Pi** running **Suricata IDS** compiled natively from source with **Vectorscan** hardware acceleration.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Cisco IOS](https://img.shields.io/badge/Cisco_IOS-15.2-049FD9?style=for-the-badge&logo=cisco&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-4-A22846?style=for-the-badge&logo=raspberrypi&logoColor=white)
![Suricata](https://img.shields.io/badge/Suricata-7.0.3-EF3B2C?style=for-the-badge&logo=linux&logoColor=white)

## Network Architecture & Data Flow

The infrastructure decouples production traffic from network management and orchestration. By leveraging hardware-level port mirroring (SPAN), the edge node monitors traffic passively without introducing network latency or processing bottlenecks.

```text
       [ External Internet ] 
                 │
         ┌───────▼───────┐
         │Movistar Router│
         └───────┬───────┘
                 │ 
        Gi1/0/1  │ (Clean Traffic / Inbound Attacks)
         ┌───────▼────────────────────────────────────────┐
         │         CISCO CATALYST 2960-X SWITCH           │
         │  [Applied ACL 199 IN]                          │
         └───────┬───────────────────────────────┬────────┘
                 │                               │
                 │ Gi1/0/23                      │ Gi1/0/24 (SPAN Destination)
                 │ (SPAN Source Port)            │ (Passive Packet Copy)
         ┌───────▼───────┐                       │
         │ PROD SERVER   │                       │
         │ (Nginx/Webs)  │                       │
         └───────────────┘               ┌───────▼───────┐
                                         │ RASPBERRY PI  │ ◄───[ wlan0: SSH Management ]
                                         │ (Suricata IDS)│     (Pushes ACL Blocks)
                                         └───────┬───────┘
                                                 │
                                         ┌───────▼───────┐
                                         │  Python Edge  │ (Parses eve.json in real-time)
                                         │  Orchestrator │
                                         └───────────────┘
```

## Key Features
* *Passive Port Mirroring (Local SPAN):* Zero performance degradation on production servers by utilizing the Cisco Catalyst hardware backplane to duplicate incoming and outgoing frames.
* *Hardware-Accelerated Pattern Matching:* Custom compilation of Vectorscan (the official ARM-optimized fork of Intel Hyperscan) to enable deep packet inspection (DPI) across over 50,000 rules simultaneously on an ARM Cortex-A72 architecture.
* *Dynamic Layer 2 Perimeter Defense:* Asynchronous Python-based automation handler using Netmiko to inject real-time structural access-list blocks directly into network interfaces upon attack detection.
* *Smart Memory-Cached Mitigation:* Implements an in-memory verification pipeline that eliminates redundant SSH command thrashing and prevents persistent flash memory write-wear on the physical switch.
