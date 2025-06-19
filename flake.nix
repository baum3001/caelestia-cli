{
  description = "Caelestia CLI Nix flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python3;
        pythonPackages = python.pkgs;
        caelestia-cli = pythonPackages.buildPythonApplication {
          pname = "caelestia";
          version = "0.0.0";
          src = ./.;
          format = "pyproject";
          nativeBuildInputs = with pythonPackages; [
            hatchling
            hatch-vcs
          ];
          propagatedBuildInputs = with pythonPackages; [
            pillow
            materialyoucolor
          ];
        };
      in {
        packages.default = caelestia-cli;
        apps.default = flake-utils.lib.mkApp {
          drv = caelestia-cli;
          exePath = "/bin/caelestia";
        };
      }
    );
}