{ pkgs ? import <nixpkgs> {} }:

let
  customPython = pkgs.python3.buildEnv.override {
    extraLibs = with pkgs.python3Packages; [
      pyserial
      numpy
      matplotlib
      scipy
      pandas
    ];
  };
in

pkgs.mkShell {
  buildInputs = [ customPython ];
  shellHook = ''
  '';
}

