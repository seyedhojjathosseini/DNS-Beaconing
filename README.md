# DNS Beacon Simulator

A lightweight, safe, and configurable **DNS Beaconing simulator** written in Python.  
This tool is designed for **SOC teams, Threat Hunting units, Red Teams, and DFIR analysts** to test their DNS monitoring, detection capabilities, and rule effectiveness.

It generates DNS queries at controlled intervals with **random DGA-like subdomains**, allowing detection of:
- Periodic beaconing behavior  
- High NXDOMAIN rates  
- DGA-like domain entropy  
- Suspicious repeated outbound DNS traffic  
- Abnormal DNS patterns from internal hosts  

> **⚠️ Legal Notice:**  
> Use this tool **only** in networks and for domains that you have explicit authorization to test.  
> Misuse of this tool may be illegal.

---

## 🔥 Features
- Continuous DNS beaconing until manually stopped  
- Random DGA-style subdomain generation  
- Configurable intervals (fixed or random)  
- Optional jitter (+/−10%)  
- Custom DNS resolver support  
- Supports A / AAAA / TXT / MX queries  
- Logs both to console and `dns_beacon.log`  
- Graceful shutdown with `Ctrl + C`  
- Fully cross-platform (Windows / Linux / macOS)

---

## 📦 Requirements

Install dependencies:

pip install dnspython

🚀 Usage
Basic usage
python dns_beacon.py --domain test.local

Recommended professional setup
python dns_beacon.py --domain test.local --min-interval 10 --max-interval 20 --sub-len 12 --jitter

Full example
python dns_beacon.py \
    --domain soc-test.xyz \
    --min-interval 8 \
    --max-interval 15 \
    --sub-len 10 \
    --qtype A \
    --jitter \
    --resolver 10.10.10.10 \
    --log-every 1

📌 Parameters
| Parameter        | Description                                             | Default        |
| ---------------- | ------------------------------------------------------- | -------------- |
| `--domain`       | Base domain for generating random subdomains (required) | —              |
| `--min-interval` | Minimum time between queries (sec)                      | 10             |
| `--max-interval` | Maximum time between queries (sec)                      | 20             |
| `--sub-len`      | Length of random subdomain                              | 12             |
| `--qtype`        | DNS record type: `A`, `AAAA`, `TXT`, `MX`               | A              |
| `--jitter`       | Add jitter (+/−10%) to intervals                        | off            |
| `--resolver`     | Custom DNS server IP                                    | system default |
| `--log-every`    | Log every N queries                                     | 1              |

📝 Logs
dns_beacon.log

Example log entry:
2025-11-15T12:34:56Z x9a2f3q1.test.local A NXDOMAIN answers=0


🧩 Use Cases
SOC visibility testing
DNS detection rule validation
Training analysts on DNS threat hunting
Red Team OpSec-safe beacon simulation
Testing SIEM queries and dashboards
