{
  description = "Sample Zig development environment, see https://github.com/mitchellh/zig-overlay";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    # Used for shell.nix
    flake-compat = {
      url = github:edolstra/flake-compat;
      flake = false;
    };

    flake-utils.url = "github:numtide/flake-utils";
    flake-utils.inputs.nixpkgs.follows = "nixpkgs";


    zig.url = "github:/mitchellh/zig-overlay";
    zig.inputs.nixpkgs.follows = "nixpkgs";
    zig.inputs.flake-compat.follows = "flake-compat";
    zig.inputs.flake-utils.follows = "flake-utils";

  };

  outputs =
    { self
    , nixpkgs
    , flake-utils
    , ...
    } @ inputs:
    let
      overlays = [
        # Other overlays
        (final: prev: {
          zigpkgs = inputs.zig.packages.${prev.system};
        })
      ];

      # target the same systems as our inputs
      systems = builtins.attrNames inputs.zig.packages;
    in
    flake-utils.lib.eachSystem systems (
      system: let
        pkgs = import nixpkgs {inherit overlays system;};
      in rec {
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = with pkgs; [
            zigpkgs.master
            zls
          ];
        };

        # for compatibility
        devShell = self.devShells.${system}.default;
      }
    );
}
