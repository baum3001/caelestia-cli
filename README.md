# caelestia-cli

This forked verison _only_ contains the essentials required for the shell: wallpaper management and scheme generation.

After installing with the instructions below, you should just seamlessly be able to use the shell, wihtout ever having to run this cli tool directly.

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

## Issues:
 - Changing the wallpaper changes the scheme of some completly unrelated (currently running) programs, in my case 'ghostty'

## Future Plans:
 - Make it also generate a [tinted-theming](https://github.com/tinted-theming/schemes) scheme for use with [stylix](https://github.com/nix-community/stylix)
