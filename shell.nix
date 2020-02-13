{ pkgs ?  import <nixpkgs> {}
, stdenv ? pkgs.stdenv
} :
let

  py = pkgs.python37;
  pyls = py.pkgs.python-language-server.override { providers=["pyflakes"]; };
  pyls-mypy = py.pkgs.pyls-mypy.override { python-language-server=pyls; };

  pylightnix_dev = import ../stagedml/3rdparty/pylightnix {
    inherit pkgs;
    python = py;
    doCheck = false;
  };

  pylightnix_head = py.pkgs.buildPythonPackage rec {
    pname = "pylightinx";
    version = "0.0.3";

    preConfigure = with pkgs; ''
      export PATH=${wget}/bin:${atool}/bin:$PATH
    '';

    checkInputs = with py; [ pytest pytest-mypy hypothesis ];

    checkPhase = "pytest";

    src = pkgs.fetchgit {
      url = "https://github.com/stagedml/pylightnix";
      sha256 = "sha256:0xqrmg9786yhk2if4fcmw4snw6cd6rk7hj28dz1s7idalip0wc71";
    };
  };

  my-python-packages = python-packages: with python-packages; [
    ipython
    hypothesis
    pytest
    pytest-mypy
    Pweave
    coverage

    jupyter
    matplotlib
    numpy
    tqdm
    scipy
    pylightnix_dev
    # pylightnix_head
  ];

  python-with-my-packages = py.withPackages my-python-packages;

  env = stdenv.mkDerivation {
    name = "buildenv";
    buildInputs =
      [
        pyls-mypy
        pyls
        python-with-my-packages
      ] ++ (with pkgs;[ gnumake ]);

    shellHook = with pkgs; ''
      export CWD=`pwd`
      export PYTHONPATH=`pwd`/src:$PYTHONPATH
      alias ipython=`pwd`/ipython.sh
      export QT_QPA_PLATFORM_PLUGIN_PATH=`echo ${pkgs.qt5.qtbase.bin}/lib/qt-*/plugins/platforms/`
    '';
  };

in
  env

