#!/usr/bin/env python3
import argparse
from artiq.experiment import *
from sipyco.pc_rpc import Client
from sipyco.pc_rpc import simple_server_loop
#from sipyco.common_args import simple_network_args
#import argparse
from sipyco.common_args import simple_network_args, bind_address_from_args
class Hello:
    def message(self, msg):
        print("message: " + msg)

def get_argparser():
    parser = argparse.ArgumentParser(description="Hello world controller")
    # Add network arguments with a default TCP port (e.g., 3249)
    simple_network_args(parser, 3249)  
    return parser

def main():
    # Parse the arguments
    args = get_argparser().parse_args()
    
    # Use the processed bind address and port for the server
    bind_address = bind_address_from_args(args)
    prin(args)
    # Start the server loop (assuming you have defined `simple_server_loop` and `Hello` classes)
    simple_server_loop(Hello(), bind_address, args.port)

if __name__ == "__main__":
    main()
