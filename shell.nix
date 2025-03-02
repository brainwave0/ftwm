let
  pkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/41bc1723c8789e9c46a1bb4897022f80d2cf147d.tar.gz") {};
  packageOverrides = self: super: { opencv4 = super.opencv4.override { enableGtk2 = true; }; };  
  python = pkgs.python3.override { inherit packageOverrides; self = python; };
in
pkgs.mkShell {
  nativeBuildInputs = with pkgs; [autoflake black mypy (python.withPackages (ps: with ps; [pytest pywlroots numpy opencv-python xdg-base-dirs dbus-next]))];
  shellHook = ''
    export SUBSHELL_NAME="nix-shell"
  '';
}
