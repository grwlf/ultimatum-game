from ultimatum import runI, run1

from pylightnix import ( Config, Manager, Build, DRef, RRef, ConfigAttrs,
    mkdrv, instantiate, realizeMany, build_cattrs, build_wrapper, match_all,
    build_outpaths, Path, config_dict, build_config, store_initialize,
    match_only, build_paths, build_outpath, realize )
import matplotlib.pyplot as plt
from multiprocessing.pool import Pool
from typing import List, Optional
from json import loads as json_loads, dumps as json_dumps
from os import chdir

store_initialize('/tmp/ultimatum', '/tmp')

def _build_process(a:ConfigAttrs, o:Path):
  run1(cwd=o, nepoch=a.nepoch, n=a.n, nrounds=a.nrounds, cutoff=a.cutoff)

def breed_node(m:Manager)->DRef:
  def _config()->Config:
    name='ultimatum'
    nepoch=30000
    n=300
    nrounds=10*30
    cutoff=0.1
    version=6
    nrunners=10
    return Config(locals())
  def _build(b:Build)->None:
    c=build_cattrs(b)
    p=Pool()
    p.starmap(_build_process,[(c,o) for o in build_outpaths(b,nouts=c.nrunners)],1)
  return mkdrv(m, config=_config(), matcher=match_all(), realizer=build_wrapper(_build))


def analyze_node(m:Manager)->DRef:
  def _config()->Config:
    return Config({
      'name':'analyzer',
      'version':3,
      'history':[breed_node(m), 'history.json']
    })
  def _build(b:Build)->None:
    chdir(build_outpath(b))
    c=build_cattrs(b)

    fig=plt.figure()
    ax=fig.add_subplot(1, 1, 1)
    ax.set_ylabel('mean strategies')
    ax.grid()

    for nhist,histpath in enumerate(build_paths(b, c.history)):
      epoches:List[float]=[]; pmeans:List[float]=[]; rmeans:List[float]=[]
      with open(histpath,'r') as f:
        epoches,pmeans,rmeans=json_loads(f.read())
      ax.plot(epoches,pmeans,label=f'pmeans{nhist}',color='blue')
      ax.plot(epoches,rmeans,label=f'rmeans{nhist}',color='orange')
    plt.savefig('figure.png')
  return mkdrv(m, config=_config(), matcher=match_only(), realizer=build_wrapper(_build))

