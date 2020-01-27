{ pkgs ?  import <nixpkgs> {}
, stdenv ? pkgs.stdenv
} :
let

  py = pkgs.python36Packages;
  pyls = py.python-language-server.override { providers=["pyflakes"]; };
  pyls-mypy = py.pyls-mypy.override { python-language-server=pyls; };

  env = stdenv.mkDerivation {
    name = "buildenv";
    buildInputs =
      (with py;[
        ipython
        pyls-mypy
        pyls
        hypothesis
        pytest
        pytest-mypy
        Pweave
        coverage

        ipython
        jupyter
        matplotlib
        numpy
        tqdm
        # scipy
      ]) ++ (with pkgs;[ gnumake ]);

    shellHook = with pkgs; ''
      export CWD=`pwd`
      export PYTHONPATH=`pwd`/src:$PYTHONPATH
      alias ipython=`pwd`/ipython.sh
      export QT_QPA_PLATFORM_PLUGIN_PATH=`echo ${pkgs.qt5.qtbase.bin}/lib/qt-*/plugins/platforms/`
    '';
  };

in
  env

