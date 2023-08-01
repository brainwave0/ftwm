{ pkgs ? import <nixpkgs> {} }:
(pkgs.buildFHSUserEnv {
  name = "pipzone";
  targetPkgs = pkgs: (with pkgs;[
    python310Full
    python310Packages.pip
    python310Packages.virtualenv
    gcc
    zlib
    libGL
    glib
    mypy
    xorg.libxcb
  ]);
  profile = ''
    source venv/bin/activate
  '';
  runScript = "bash";
}).env
