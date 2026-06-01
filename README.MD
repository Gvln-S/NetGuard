# [EdgeSentinel: Automated Network Defense](https://github.com/Gvln-S/NetGuard/)

An enterprise-grade Active Intrusion Prevention System (IPS) deployed at the edge. This project re-architects a standard home network infrastructure into a segmented, highly monitored environment using a hardware-managed **Cisco Catalyst 2960-X** switch, a production server ecosystem, and an edge computing node powered by a **Raspberry Pi** running **Suricata IDS** compiled natively from source with **Vectorscan** hardware acceleration.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Cisco IOS](https://img.shields.io/badge/Cisco_IOS-15.2-049FD9?style=for-the-badge&logo=cisco&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-4-A22846?style=for-the-badge&logo=raspberrypi&logoColor=white)
![Suricata](https://img.shields.io/badge/Suricata-7.0.3-EF3B2C?style=for-the-badge&logo=linux&logoColor=white)

## Network Architecture & Data Flow

The infrastructure decouples production traffic from network management and orchestration. By leveraging hardware-level port mirroring (SPAN), the edge node monitors traffic passively without introducing network latency or processing bottlenecks.

| Figure 1 |
| :---: | 
| ![Screenshot 1](figure_1.png) | 

## Key Features
* **Passive Port Mirroring (Local SPAN):** Zero performance degradation on production servers by utilizing the Cisco Catalyst hardware backplane to duplicate incoming and outgoing frames.
* **Hardware-Accelerated Pattern Matching:** Custom compilation of Vectorscan (the official ARM-optimized fork of Intel Hyperscan) to enable deep packet inspection (DPI) across over 50,000 rules simultaneously on an ARM Cortex-A72 architecture.
* **Dynamic Layer 2 Perimeter Defense:** Asynchronous Python-based automation handler using Netmiko to inject real-time structural access-list blocks directly into network interfaces upon attack detection.
* **Smart Memory-Cached Mitigation:** Implements an in-memory verification pipeline that eliminates redundant SSH command thrashing and prevents persistent flash memory write-wear on the physical switch.

## Phase 1: Cisco Catalyst 2960-X Provisioning & Hardening
### 1. Serial Console Recovery
* **Issue:** Connecting via a physical serial console cable using PuTTY returned an Access Denied error on COM7.
* **Root Cause:** Zombie background instances of terminal applications locking the hardware interface or insufficient local privilege execution on the management host.
* **Resolution:** Terminated all orphan serial handler processes through Task Manager and forced execution of the serial terminal console with elevated administrative privileges.

### 2. Cryptographic Protocol Modernization
* **Issue:** Modern SSH clients rejected connections to the legacy switch configuration, outputting negotiation errors:
* no matching key exchange method found. Their offer: diffie-hellman-group-exchange-sha1
* no matching host key type found. Their offer: ssh-rsa
* **Root Cause:** The switch was operating with deprecated 512/1024-bit RSA host keys relying on weak SHA-1 signatures.
* **Resolution:** Re-generated modern cryptographic primitives on the switch using an expanded module length:

```ios
switch# configure terminal
switch(config)# ip ssh version 2
switch(config)# crypto key generate rsa general-keys modulus 2048
! Confirm overwrite of previous legacy keys when prompted
switch(config)# ip name-server 192.168.1.200
switch(config)# write memory
```

### 3. Loop Mitigation & Multicast Layer-2 Optimizations
Issue: Connecting the production server restored external TCP web traffic, but local .local mDNS/Bonjour network resolution failed completely, causing internal DNS queries through the local Pi-hole to drop silently.

#### Root Cause:
* The upstream gateway router negotiated at a-100 (100 Mbps) while the server ran at a-1000 (1 Gbps).
* Default Spanning Tree Protocol (STP) listening/learning cycles delayed port activation for up to 50 seconds, dropping unacknowledged UDP bursts.
* Strict ip igmp snooping on the switch dropped local link-local multicast registration packets.

* Resolution: Enabled instant transition states for edge infrastructure and removed aggressive multicast pruning filters:
```ios
switch(config)# interface gigabitEthernet 1/0/1
switch(config-if)# spanning-tree portfast
switch(config-if)# exit
switch(config)# interface gigabitEthernet 1/0/23
switch(config-if)# spanning-tree portfast
switch(config-if)# exit
```ios

### 4. Local SPAN Mirroring Execution
Configured the physical hardware backplane to clone full duplex streams from the production server (Gi1/0/23) directly into the analyzer interface (Gi1/0/24):

```ios
Cisco CLI
switch(config)# monitor session 1 source interface gigabitEthernet 1/0/23 both
switch(config)# monitor session 1 destination interface gigabitEthernet 1/0/24
```

[!WARNING]
Once configured as a SPAN destination, Gi1/0/24 ceases normal Layer 3 behaviors. It will not process DHCP requests, handle an IP stack, or route internet data. It operates purely as a raw packet injection port.

## Phase 2: Gateway Router Integration & DHCP Constraints
Discovery: The ISP upstream gateway router deployed remote TR-069 firmware configurations containing competitive parallel DHCP servers on the single broadcast domain:

* Primary Server (Highest Priority): Enforced standard corporate DNS routing (200.21.200.80), auto-reverting any persistent administrative modifications within minutes.
* Secondary Server: Configured to point towards the local Pi-hole instance (192.168.1.200) but was consistently starved out by the primary engine.

IPTV Restrictions: The primary DHCP engine could not be completely disabled due to local IPTV decoders requiring unique manufacturer initialization tags (DHCP Option 240) injected at the gateway.
Architectural Fix: Left the ISP gateway DHCP active to sustain IPTV functionality and manually bound static DNS maps to management workstations, forcing critical routing records through local /etc/hosts tables.

## Phase 3: Edge Node Preparation & Source Compilations
### 1. Dual-Interface Network Isolation
To resolve the IP isolation of the passive SPAN port, the Raspberry Pi network parameters were decoupled across physical boundaries:

* **wlan0 (Wireless):** Assigned to the main network zone for internet access, rule database updates, and outbound orchestration communication.
* **eth0 (Wired):** Connected to the passive SPAN interface. The IP layer was stripped from this link to eliminate hanging DHCP timeouts, and the driver was forced into Promiscuous Mode to read all incoming transit frames.

```bash
# Disable IPv4 and IPv6 stacks on the physical wire via NetworkManager
sudo nmcli connection modify "Wired connection 1" ipv4.method disabled ipv6.method ignore
sudo nmcli connection up "Wired connection 1"

# Force promiscuous mode at the interface driver level
sudo ip link set eth0 promisc on
```

### 2. Compiling Vectorscan from Source
Standard Debian packages lack compilation hooks for high-performance regular expression scanning on ARM architectures. Vectorscan acts as a drop-in acceleration replacement for Hyperscan on ARM processors.

```bash
# Install core build dependencies
sudo apt update
sudo apt install -y build-essential cmake gcc g++ libpcap-dev libpcre2-dev \
python3 ragel libsqlite3-dev libboost-dev git pkg-config

# Clone and construct the Vectorscan binary tree
cd ~/documents/compile
git clone [https://github.com/VectorCamp/vectorscan.git](https://github.com/VectorCamp/vectorscan.git)
cd vectorscan && mkdir build && cd build

# Explicitly isolate builds and remove non-critical unit tests to prevent linking faults
cmake -DBUILD_STATIC_LIBS=OFF -DBUILD_SHARED_LIBS=ON -DBUILD_BENCHMARKS=OFF -DBUILD_EXAMPLES=OFF -DBUILD_UNIT_TESTS=OFF ..
make -j4
sudo make install

# Register newly installed libraries within the dynamic linker cache
sudo sh -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/local.conf'
sudo ldconfig
```

### 3. Natively Building Suricata 7.0.3

```bash
# Fetch mandatory engine dependencies and Rust compiler tools
sudo apt install -y rustc cargo libyaml-dev libjansson-dev libmagic-dev \
liblz4-dev zlib1g-dev libpcre3 libpcre3-dbg libpcre3-dev \
libnet1-dev libnfnetlink-dev libnetfilter-queue-dev libssl-dev libnuma-dev \
libnspr4-dev libnss3-dev make

# Downlod and unpack target engine distribution
cd ~/documents/compile
wget [https://www.openinfosecfoundation.org/download/suricata-7.0.3.tar.gz](https://www.openinfosecfoundation.org/download/suricata-7.0.3.tar.gz)
tar -xvzf suricata-7.0.3.tar.gz
cd suricata-7.0.3

# Configure compilation targets mapping the exact source directories of Vectorscan
./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --enable-geoip --enable-rust \
--with-libhs-includes=/usr/local/include/hs --with-libhs-libraries=/usr/local/lib

make -j4
sudo make install
sudo make install-conf
```

### 4. Engine Initialization & Verification
Update the target operational engine parameters to map onto the passive listening card:

```bash
# Run signature sync updates to fetch latest community rules
sudo suricata-update
```
Verify the integration of Vectorscan engine acceleration using the build signature utility:


```bash
suricata --build-info | grep Hyperscan
# Expected Output: Hyperscan support: yes
```
Performance Metrics: Upon initial production tests, the engine successfully launched 50,250 signatures into system memory. Over an active verification monitoring window of 174 seconds, it analyzed 5,027 real-time transit packets with zero dropped frames (drops: 0.00%).

## Phase 4: Automated Edge Orchestrator Implementation
### 1. Handling Python PEP 668 Environment Restrictions
When deploying standard automation drivers on modern Debian-based OS wrappers, standard package management tools trigger an externally-managed-environment error blocks. To install the requisite multi-vendor communication libraries, explicitly bypass the OS manager block safely:

```bash
sudo pip3 install netmiko --break-system-packages
```
### 2. Core Operational Mechanics & Edge Logic
The automation suite tracks the Suricata performance ledger using an optimized Python generator mapping file pointers natively, mirroring the asynchronous efficiency of a system tail -f process.

#### Structural Architectural Adaptations for Layer-2 Hardware:
* **Inbound Inspection Constraints:** True Layer 2 switches (such as the Cisco 2960-X series) cannot process outbound ACL definitions across standard physical interfaces (ip access-group out is invalid). The ASIC hardware architecture strictly evaluates incoming packets. Thus, the Python orchestrator targets and isolates the primary internet ingress node (Gi1/0/1) in the IN direction.

* **State Machine Guardrails:** To maximize processing speed, generic permit ip any any rules are initialized manually once at the base of the physical switch rule stack. The Python engine injects high-priority sequential deny ip host {ATTACKER_IP} any log blocks above the allow threshold.

* **Write Lag Eradication:** Persistent NVRAM saving (write memory) introduces a blocking 4-second delay on the switch firmware. The script isolates blocks inside volatile RAM for instantaneous sub-millisecond execution, leveraging scheduled environment reboots or administrative manual cleanups for state persistence management.

---
*Developed as a high-performance framework bridging bare-metal hardware network engineering with dynamic automation at the edge.*





