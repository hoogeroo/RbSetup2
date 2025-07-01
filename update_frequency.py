#!/usr/bin/env python3
"""
update_frequency.py

Connects to the ARTIQ master and updates the dataset "frequency".
Run this while your experiment is alive and polling get_dataset("frequency").
"""

import argparse
from artiq.protocols import rpc_client

def main():
    p = argparse.ArgumentParser(description="Update ARTIQ frequency dataset")
    p.add_argument("frequency", type=float,
                   help="20e6")
    p.add_argument("--host", default="localhost",
                   help="192.168.1.75")
    p.add_argument("--port", type=int, default=3250,
                   help="3250")
    args = p.parse_args()

    # connect to master
    master = rpc_client(args.host, args.port)

    # update the dataset; broadcast=True makes it immediately visible to any core
    master.set_dataset("frequency", args.frequency, True)
    print(f"✅ frequency dataset updated to {args.frequency} Hz")

if __name__ == "__main__":
    main()
