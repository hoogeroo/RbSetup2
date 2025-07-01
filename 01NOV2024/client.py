"""import argparse
from sipyco.common_args import simple_network_args

def get_argparser():
    parser = argparse.ArgumentParser(description="Hello world client")
    # Add network arguments with a default TCP port (e.g., 3249)
    simple_network_args(parser, 3249)  
    return parser

def main():
    args = get_argparser().parse_args()
    
    # Use the server address and port (args.server and args.port) to connect to the server
    # You would need to implement the client loop or connection code

if __name__ == "__main__":
    main()"""
    
    
#!/usr/bin/env python3

from sipyco.pc_rpc import Client


def main():
    remote = Client("::1", 3249, "hello")
    try:
        remote.message("Hello World!")
    finally:
        remote.close_rpc()

if __name__ == "__main__":
    main()
"""import argparse
from sipyco.common_args import simple_network_args
from sipyco.pc_rpc import Client
def get_argparser():
    parser = argparse.ArgumentParser(description="Hello world client")
    # Add network arguments with a default TCP port (e.g., 3249)
    simple_network_args(parser, 3249)  
    return parser

def main():
    args = get_argparser().parse_args()
    
    # Use the server address and port (args.server and args.port) to connect to the server
    # You would need to implement the client loop or connection code
    remote = Client("::1", 3249, "hello")
    try:
        remote.message("Hello World!")
    finally:
        remote.close_rpc()
    #connect_to_server(args.server, args.port)

if __name__ == "__main__":
    main()
"""