#!/usr/bin/env python3
"""
from sipyco.pc_rpc import Client


def main():
    remote = Client("::1", 3249, "hello")
    try:
        remote.message("Hello World!")
    finally:
        remote.close_rpc()

if __name__ == "__main__":
    main()"""
    
from sipyco.pc_rpc import Server
#from sipyco.asyncio_tools import wait_for_interrupt
import signal
import argparse

class FrequencyServer:
    def __init__(self):
        self.frequency = 80.0  # Default frequency in MHz

    def set_frequency(self, value):
        """Set the frequency."""
        self.frequency = value
        print(f"Frequency updated to: {self.frequency} MHz")

    def get_frequency(self):
        """Get the current frequency."""
        return self.frequency



def main():
    parser = argparse.ArgumentParser(description="AOM Frequency Controller")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port for the server")
    args = parser.parse_args()

    server = Server({"frequency_server": FrequencyServer()}, args.port)
    server.run()
    
    # Use signal.pause() for waiting indefinitely
    try:
        signal.pause()
    except KeyboardInterrupt:
        print("Server interrupted, shutting down...")


if __name__ == "__main__":
    main()