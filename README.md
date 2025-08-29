# BEC ARTIQ Experiment Controller

## Setup

For the initial setup follow <https://m-labs.hk/artiq/manual/installing.html>. In summary, install nix and activate the artiq flake. This repo includes a `flake.nix` that sets up artiq as well as installing the required python packages.

To connect to the core device connect the ethernet cable and make sure the routing is set up correctly. We use the defualt ip `192.168.1.75`. If `ping 192.168.1.75` doesn't work go to network configuration and set a static ip to something like `192.168.1.2` with a netmask of `255.255.255.0` on the artiq network interface. See <https://m-labs.hk/artiq/manual/configuring.html> for more info.

If pinging the core device works but communication with the core device doesn't it may be due to different artiq versions on the host and the device. For compiling artiq refer to [zaviers notes](ZAVIER.txt) and the [official documentation](https://m-labs.hk/artiq/manual/flashing.html).

## Running

First make sure your shell's working directory is this one. Then enter the nix enviroment by running `nix shell`. This will take a while the first time. Then launch the gui:
```bash
artiq_run main.py
```
To run the gui without the artiq fpga handy (good for working on the gui):
```bash
python3 main.py
```
This also works outside the nix enviroment if the right dependencies are installed.

## Developmnet Notes

* To edit the gui open [`gui.ui`](gui.ui) in [qt creator](https://snapcraft.io/qtcreator-ros) or qt designer
* It seems you can't hop between host and device more than once, i.e device -> host -> device won't work. However some functions like `print` seem to be handled specially and do work
* 32 bit floats dont work
* To run the gui without artiq you can run the `device.py` file: `python3 device.py`

## Resources

- <https://github.com/Hanros94/IonTrap-WIPM/blob/master/Manual%20for%20Developers(English%20Version).md>
- <https://github.com/whichislovely/Hosten-group-Quantrol-Control-system>

