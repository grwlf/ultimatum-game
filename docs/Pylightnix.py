
from json import loads as json_loads, dumps as json_dumps
from os import getcwd, chdir
from os.path import join
from typing import List, Optional

from pylightnix import (
  Config, Manager, Build, DRef, RRef, ConfigAttrs, Closure, Path, mkdrv,
  instantiate, build_cattrs, build_wrapper, build_outpaths, store_initialize,
  match_latest, build_paths, build_outpath, realize, rref2path, mkconfig )

store_initialize('/tmp/ultimatum', '/tmp')

from ultimatum.base import run1
from multiprocessing.pool import Pool

def evolution_config()->Config:
  name = 'ultimatum'
  nepoch = 30000
  n = 300
  nrounds = 10*30
  cutoff = 0.1
  version = 6
  nrunners = 10
  return mkconfig(locals())

def _run_process(a:ConfigAttrs, o:Path):
  run1(cwd=o, nepoch=a.nepoch, n=a.n, nrounds=a.nrounds, cutoff=a.cutoff)

def evolution_realize(b:Build)->None:
  c = build_cattrs(b)
  p = Pool()
  p.starmap(_run_process,[(c,o) for o in build_outpaths(b,nouts=c.nrunners)],1)

def evolution_stage(m:Manager)->DRef:
  return mkdrv(m, config=evolution_config(),
                  matcher=match_latest(top=10),
                  realizer=build_wrapper(evolution_realize))

import matplotlib.pyplot as plt

def summary_config(evolution:DRef)->Config:
  name = 'summary'
  history_refpath = [evolution, 'history.json']
  return mkconfig(locals())

def summary_realize(b:Build)->None:
  cwd = getcwd()
  try:
    chdir(build_outpath(b))
    c = build_cattrs(b)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_ylabel('mean strategies')
    ax.grid()

    for nhist,histpath in enumerate(build_paths(b, c.history_refpath)):
      epoches:List[float]=[]; pmeans:List[float]=[]; rmeans:List[float]=[]
      with open(histpath,'r') as f:
        epoches,pmeans,rmeans=json_loads(f.read())
      if nhist==0:
        pargs = {'label':'Proposer mean'}
        rargs = {'label':'Responder mean'}
      else:
        pargs = {}; rargs = {}
      ax.plot(epoches,pmeans,color='blue',**pargs)
      ax.plot(epoches,rmeans,color='orange',**rargs)
    plt.savefig('figure.png')

    ax.legend(loc='upper right')
  finally:
    chdir(cwd)

def summary_stage(m:Manager)->DRef:
  return mkdrv(m, config=summary_config(evolution_stage(m)),
                  matcher=match_latest(),
                  realizer=build_wrapper(summary_realize))

clo:Closure = instantiate(summary_stage)

rref:RRef = realize(clo)

print(rref)

print(rref2path(rref))

from pylightnix import lsref

print(lsref(rref))

realize(clo, force_rebuild=[clo.dref])
plt.show()
