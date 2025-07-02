# BEC ARTIQ Experiment Controller

## Setup

For the initial setup follow <https://m-labs.hk/artiq/manual/installing.html>. In summary, install nix and activate the artiq flake. This repo includes a `flake.nix` that sets up artiq as well as installing the required python packages.

To connect to the core device connect the ethernet cable and make sure the routing is set up correctly. We use the defualt ip `192.168.1.75`. If `ping 192.168.1.75` doesn't work go to network configuration and set a static ip to something like `192.168.1.2` with a netmask of `255.255.255.0` on the artiq network interface. See <https://m-labs.hk/artiq/manual/configuring.html> for more info.


