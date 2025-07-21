{
  inputs.extrapkg.url = "git+https://git.m-labs.hk/M-Labs/artiq-extrapkg.git";
  outputs = { self, extrapkg }:
    let
      pkgs = extrapkg.pkgs;
      artiq = extrapkg.packages.x86_64-linux;
    in {
      defaultPackage.x86_64-linux = pkgs.buildEnv {
        name = "artiq-env";
        paths = [
          # ========================================
          # EDIT BELOW
          # ========================================
          (pkgs.python312.withPackages(ps: [
            # List desired Python packages here.
            artiq.artiq
            ps.pyqt6
            ps.pip
            ps.matplotlib
            ps.astropy
            # ps.numba
            # ps.astropy
            # ps.spyder-kernels
            # ps.spyder
            # ps.pandas
            # ps.json
            # ps.scikit-learn
            # ps.pyvisa
            # ps.daqprops
                

            #ps.paramiko  # needed if and only if flashing boards remotely (artiq_flash -H)
            #artiq.flake8-artiq
            #artiq.dax
            #artiq.dax-applets

            # The NixOS package collection contains many other packages that you may find
            # interesting. Here are some examples:
            #ps.pandas
            
            
            
            # or if you need Qt (will recompile):
            #(ps.matplotlib.override { enableQt = true; })
            #ps.bokeh
            #ps.cirq
            #ps.qiskit
            # Note that NixOS also provides packages ps.numpy and ps.scipy, but it is
            # not necessary to explicitly add these, since they are dependencies of
            # ARTIQ and available with an ARTIQ install anyway.
          ]))
          #artiq.korad_ka3005p
          #artiq.novatech409b
          # List desired non-Python packages here
          # Other potentially interesting non-Python packages from the NixOS package collection:
          #pkgs.gtkwave
          #pkgs.libaiousb
          #pkgs.R
          #pkgs.json
          pkgs.glibc
          pkgs.busybox-sandbox-shell
          pkgs.fxload
          #pkgs.sklearn
          #pkgs.julia
          pkgs.qt6.qtwayland
          # ========================================
          # EDIT ABOVE
          # ========================================
        ];
      };
    };
  nixConfig = {  # work around https://github.com/NixOS/nix/issues/6771
    extra-trusted-public-keys = "nixbld.m-labs.hk-1:5aSRVA5b320xbNvu30tqxVPXpld73bhtOeH6uAjRyHc=";
    extra-substituters = "https://nixbld.m-labs.hk";
  };
}
