# BEC ARTIQ Experiment Controller

## Setup

For the initial setup follow <https://m-labs.hk/artiq/manual/installing.html>. In summary, install nix and activate the artiq flake. This repo includes a `flake.nix` that sets up artiq as well as installing the required python packages.

To connect to the core device connect the ethernet cable and make sure the routing is set up correctly. We use the defualt ip `192.168.1.75`. If `ping 192.168.1.75` doesn't work go to network configuration and set a static ip to something like `192.168.1.2` with a netmask of `255.255.255.0` on the artiq network interface. See <https://m-labs.hk/artiq/manual/configuring.html> for more info.

If pinging the core device works but communication with the core device doesn't it may be due to different artiq versions on the host and the device.

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
* It seems you can't make more than 2 hops between host and device, i.e host -> device -> host works fine but host -> device -> host -> device won't work
* 32 bit floats dont work
* To add a new tab of stages uncomment the line in the `__init__` function in `src/gui/gui.py` and set the name and index for the new tab

## Compiling Artiq

Follow the instructions on the [ARTIQ wiki](https://m-labs.hk/artiq/manual/building_developing.html) for compiling `artiq-zynq`. The main steps are as follows:

* Installing the correct version of Vivado
* Installing Nix in single-user mode
* Enabling flakes by adding `experimental-features = nix-command flakes` to `nix.conf`
* Add `/opt` (or your Vivado location) as a Nix sandbox, for example by adding `extra-sandbox-paths = /opt` to `nix.conf`
* If on Ubuntu follow the instructions from the [forum](https://forum.m-labs.hk/d/903-can-not-access-to-vivado-when-building-the-artiq/6) to disable Apparmor for Nix to allow Nix to access Vivado
* Run the following command with appropriate paths to compile ARTIQ:

```bash
nix build --option extra-sandbox-paths /opt --print-build-logs --impure --expr 'let fl = builtins.getFlake "git+https://git.m-labs.hk/m-labs/artiq-zynq?ref=release-8"; in (fl.makeArtiqZynqPackage {target="kasli_soc"; variant="standalone"; json=/home/lab/Documents/brian/auckland.json;}).kasli_soc-standalone-sd'
```

* Generate a new `device_db.py` file using `artiq_ddb_template` for the new configuration

> [!IMPORTANT]  
> The disabling Apparmor for Ubuntu step is not in the wiki

## Resources

* <https://github.com/Hanros94/IonTrap-WIPM/blob/master/Manual%20for%20Developers(English%20Version).md>
* <https://github.com/whichislovely/Hosten-group-Quantrol-Control-system>
