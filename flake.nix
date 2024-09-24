{
  description = "A tool to manage configuration file overrides";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      in
      {
        packages = {
          conf-manager = mkPoetryApplication { projectDir = self; };
          default = self.packages.${system}.conf-manager;
        };

        devShell = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.conf-manager ];
          packages = [ pkgs.poetry ];
        };
      });
}