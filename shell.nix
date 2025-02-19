let pkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/41bc1723c8789e9c46a1bb4897022f80d2cf147d.tar.gz") {}; in
pkgs.mkShell {
  nativeBuildInputs = with pkgs; [mypy (python3.withPackages (ps: with ps; [pywlroots numpy opencv-python xdg-base-dirs dbus-next]))];
  shellHook = ''
    export SUBSHELL_NAME="nix-shell"
  '';
}
