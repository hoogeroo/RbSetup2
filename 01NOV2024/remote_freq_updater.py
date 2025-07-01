from sipyco.pc_rpc import Client

def main():
    client = Client("::1", 3249)  # Connect to the frequency server
    try:
        while True:
            # Input frequency dynamically
            new_frequency = float(input("Enter new frequency (MHz): "))
            client.call("frequency_server.set_frequency", new_frequency)
            print(f"Sent new frequency: {new_frequency} MHz")
    except KeyboardInterrupt:
        print("Exiting frequency update client.")

if __name__ == "__main__":
    main()