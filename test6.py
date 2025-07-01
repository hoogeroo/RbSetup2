from artiq.protocols.pc_rpc import Client

class GUIController:
    def __init__(self):
        self.client = Client("192.168.1.75", 3251)  # Replace with the actual IP and port
        self.experiment = self.client.get_experiment("PersistentAOMController")

    def update_aom_frequency(self, frequency):
        self.experiment.get_frequency_update(frequency)