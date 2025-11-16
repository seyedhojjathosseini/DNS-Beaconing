#!/usr/bin/env python3
"""
dns_beacon.py
Simple, configurable DNS beacon simulator for detection exercises.

USAGE:
  python dns_beacon.py --domain mytest.example --min-interval 10 --max-interval 20 --sub-len 12

IMPORTANT: Use only on networks/domains you are authorized to test.
"""

import argparse
import random
import string
import time
import signal
import sys
import logging
from datetime import datetime

import dns.resolver    # dnspython

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("dns_beacon.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

stop_requested = False

def signal_handler(sig, frame):
    global stop_requested
    logging.info("SIGINT received — stopping beacon gracefully...")
    stop_requested = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def rand_subdomain(length: int, charset: str = None) -> str:
    if charset is None:
        # mix of lowercase letters and digits to mimic DGA-like names
        charset = string.ascii_lowercase + string.digits
    return ''.join(random.choice(charset) for _ in range(length))

def perform_query(resolver: dns.resolver.Resolver, fqdn: str, qtype: str = "A"):
    """Perform DNS query and return (rcode, answer_count, rdata_summary)"""
    try:
        # note: dns.resolver.resolve raises exceptions on NXDOMAIN/noanswer
        ans = resolver.resolve(fqdn, qtype, lifetime=5)
        # collect a brief summary of returned IPs/names
        rdata = ", ".join([r.to_text() for r in ans])
        rcode = "NOERROR"
        return (rcode, len(ans), rdata)
    except dns.resolver.NXDOMAIN:
        return ("NXDOMAIN", 0, "")
    except dns.resolver.NoAnswer:
        return ("NOANSWER", 0, "")
    except dns.exception.Timeout:
        return ("TIMEOUT", 0, "")
    except Exception as e:
        return ("ERROR", 0, str(e))

def main():
    parser = argparse.ArgumentParser(description="DNS Beacon simulator for SOC detection exercises")
    parser.add_argument("--domain", required=True,
                        help="Base domain to query against (e.g. testlab.local or soc-test.example)")
    parser.add_argument("--min-interval", type=float, default=10.0,
                        help="Minimum interval between queries (seconds)")
    parser.add_argument("--max-interval", type=float, default=20.0,
                        help="Maximum interval between queries (seconds). If equal to min -> fixed interval")
    parser.add_argument("--sub-len", type=int, default=12,
                        help="Length of random subdomain part")
    parser.add_argument("--qtype", choices=["A","AAAA","TXT","MX"], default="A",
                        help="DNS record type to query")
    parser.add_argument("--jitter", action="store_true",
                        help="Add small random jitter to each sleep (±10%%)")
    parser.add_argument("--resolver", default=None,
                        help="Custom DNS server IP (optional). If omitted system resolver is used.")
    parser.add_argument("--log-every", type=int, default=1,
                        help="Number of queries between INFO logs to stdout (keeps noise down).")
    args = parser.parse_args()

    resolver = dns.resolver.Resolver()
    if args.resolver:
        resolver.nameservers = [args.resolver]
        logging.info(f"Using custom resolver {args.resolver}")
    else:
        logging.info("Using system resolver")

    counter = 0
    logging.info(f"Starting DNS beaconing to domain '{args.domain}' (sub-len={args.sub_len}, qtype={args.qtype})")
    logging.info("Press Ctrl+C to stop")

    while not stop_requested:
        sub = rand_subdomain(args.sub_len)
        fqdn = f"{sub}.{args.domain}".rstrip('.')
        timestamp = datetime.utcnow().isoformat() + "Z"
        rcode, count, rdata = perform_query(resolver, fqdn, qtype=args.qtype)

        # Log format: timestamp, fqdn, qtype, rcode, answer_count, rdata
        log_line = f"{timestamp} {fqdn} {args.qtype} {rcode} answers={count}"
        if rdata:
            log_line += f" rdata={rdata}"
        logging.info(log_line) if (counter % args.log_every == 0) else logging.debug(log_line)

        counter += 1

        # compute sleep interval
        if args.min_interval == args.max_interval:
            interval = args.min_interval
        else:
            interval = random.uniform(args.min_interval, args.max_interval)

        if args.jitter:
            jitter_amount = interval * 0.10
            interval = max(0.1, random.uniform(interval - jitter_amount, interval + jitter_amount))

        # sleep but wake early if stopping requested
        slept = 0.0
        step = 0.2
        while slept < interval:
            if stop_requested:
                break
            time.sleep(step)
            slept += step

    logging.info("Beacon stopped. Finalizing...")

if __name__ == "__main__":
    main()
