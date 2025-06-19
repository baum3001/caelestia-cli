# caelestia-cli

The main control script for the Caelestia dotfiles.

## Installation

### NixOS
Add this repo to your system flake:
```nix
{
  inputs = {
    caelestia-cli.url = "github:t7h-dots/cli";
  };
}
```
Then add it to your system configuration:
```nix
{
  environment.systemPackages = with pkgs; [
    inputs.caelestia-cli.packages.${pkgs.system}.default
  ];
}
```
