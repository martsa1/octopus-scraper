{
  pkgsSrc ? <nixpkgs>,
  pkgs ? import pkgsSrc {},
}:

with pkgs;

pkgs.mkShell {
  name = "octopus_energy_scraper-dev-env";
  buildInputs = [
    gnumake
    python3
    gcc
    #python3Packages.poetry
    poetry
  ];

  shellHook = ''
  export LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib/
  '';
}
