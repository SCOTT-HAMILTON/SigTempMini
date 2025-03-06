{ pkgs ? import <nixpkgs> {} }:

let
  customPython = pkgs.python3.buildEnv.override {
    extraLibs = with pkgs.python3Packages; [
      numpy
      matplotlib
      tabulate
      pip
      pyserial
      scipy
    ];
  };
in

pkgs.mkShell {
  buildInputs = [ customPython ];
  shellHook = ''
    export PIP_PREFIX=$(pwd)/_build/pip_packages
    export PYTHONPATH="$PIP_PREFIX/${customPython.sitePackages}:$PYTHONPATH"
    export PATH="$PIP_PREFIX/bin:$PATH"
    unset SOURCE_DATE_EPOCH
  '';
}

