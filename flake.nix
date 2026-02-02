{
  inputs.extrapkg.url = "git+https://git.m-labs.hk/M-Labs/artiq-extrapkg.git?ref=release-8";
  outputs = { self, extrapkg }:
    let
      pkgs = extrapkg.pkgs;
      artiq = extrapkg.packages.x86_64-linux;
      
      # Custom m-loop package from PyPI
      mloop = pkgs.python312Packages.buildPythonPackage rec {
        pname = "M-LOOP";
        version = "3.3.2";
        format = "setuptools";
        
        src = pkgs.python312Packages.fetchPypi {
          inherit pname version;
          sha256 = "sha256-1CWoN36oyMyhbfba3QSkcICZDNKKsXIC5jqBEcob9ts=";
        };
        
        nativeBuildInputs = with pkgs.python312Packages; [
          setuptools
          wheel
        ];
        
        propagatedBuildInputs = with pkgs.python312Packages; [
          numpy
          scipy
          matplotlib
          h5py
        ];
        
        # Skip tests as they might not be available or might require additional setup
        doCheck = false;
        
        # Disable setup_requires to avoid pytest-runner dependency
        postPatch = ''
          substituteInPlace setup.py \
            --replace "setup_requires=['pytest-runner']," "" \
            --replace "setup_requires=['pytest-runner']" ""
        '';
        
        meta = with pkgs.lib; {
          description = "Machine-learning online optimization package";
          homepage = "https://github.com/michaelhush/M-LOOP";
          license = licenses.mit;
        };
      };
    in {
      defaultPackage.x86_64-linux = pkgs.buildEnv {
        name = "artiq-env";
        paths = [
          (pkgs.python312.withPackages(ps: [
            # List desired Python packages here.
            artiq.artiq
            ps.pyqt6
            ps.pip
            ps.matplotlib
            ps.astropy
            ps.scikit-learn
            mloop
          ]))
          pkgs.qt6.qtwayland
        ];
      };
    };
  # This section configures additional settings to be able to use M-Labs binary caches
  nixConfig = {  # work around https://github.com/NixOS/nix/issues/6771
    extra-trusted-public-keys = "nixbld.m-labs.hk-1:5aSRVA5b320xbNvu30tqxVPXpld73bhtOeH6uAjRyHc=";
    extra-substituters = "https://nixbld.m-labs.hk";
  };
}
