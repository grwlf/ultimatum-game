import numpy as np
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt

from numpy import linspace, array, arange, clip, isclose
from numpy.random import choice, uniform, seed
from typing import ( Any, Optional, List, Dict, Union, Tuple, NamedTuple,
    Iterator, Callable )
from math import gcd, sqrt
from copy import deepcopy
from scipy.stats import norm

from json import dumps as json_dumps, loads as json_loads

from os import chdir

DISCR=100
OFFERS=linspace(0.0,1.0,num=DISCR+1)

Float=float
Offer=float
Money=float
# Strategy=List[Float]

class Strategy(list):
  pass

def assert_valid_offer(o:Offer)->None:
  assert o>=0.0 and o<=1.0, f"Invalid offer {o}"

def normalized(x:List[Float])->Strategy:
  p=array(x)
  assert sum(p)>0
  p=p/sum(p)
  return Strategy(p)

def mknorm()->Strategy:
  mu=uniform(0.0,1.0)
  sigma=uniform(0.05,0.3)
  return normalized([norm.pdf(x,mu,sigma) for x in OFFERS])

def mkuniform()->Strategy:
  return normalized([1.0 for x in OFFERS])

def strat_mean(s:Strategy)->Float:
  """ Mean value of astrategy """
  acc:Float=0.0
  for o,prob in zip(OFFERS,s):
    acc+=o*prob
  return acc

def strat_std(s:Strategy)->Float:
  """ Mean value of astrategy """
  acc:Float=0.0
  mean=strat_mean(s)
  for o,prob in zip(OFFERS,s):
    acc+=(prob-mean)**2
  return sqrt(acc/len(OFFERS))

def strat_stat(s:Strategy):
  return strat_mean(s),strat_std(s)

def mean_strategy(ss:List[Strategy])->Strategy:
  """ Mean strategy """
  s=[np.sum([s[i] for s in ss])/len(ss) for (i,o) in enumerate(OFFERS)]
  assert isclose(np.sum(s),1.0)
  return Strategy(s)




class Individ:
  def __init__(self, ps:Strategy, rs:Strategy):
    self.pstrategy=ps
    self.rstrategy=rs

def istat(i:Individ)->Tuple[Float,Float]:
  return strat_mean(i.pstrategy), strat_mean(i.rstrategy)


def propose(p:Individ)->Offer:
  r=choice(OFFERS,p=p.pstrategy)
  return r

def respond(r:Individ, to_proposer:Offer)->bool:
  assert_valid_offer(to_proposer)
  to_responder=1.0-to_proposer
  demand=choice(OFFERS,p=r.rstrategy)
  return to_responder>demand


class Population:
  def __init__(self, individs:List[Individ]):
    self.individs=individs

JSON=Any

def pop_serialize(pop:Population)->JSON:
  return [[list(i.pstrategy),list(i.rstrategy)] for i in pop.individs]

def pop_deserialize(json:JSON)->Population:
  return Population([Individ(Strategy(p),Strategy(r)) for p,r in json])

class PopStat(NamedTuple):
  mean_proposer_strategy:Strategy
  mean_responder_strategy:Strategy

def pstat(pop:Population)->PopStat:
  mps=mean_strategy([i.pstrategy for i in pop.individs])
  mrs=mean_strategy([i.rstrategy for i in pop.individs])
  return PopStat(mps,mrs)

  # ps=[istat for i in pop.individs]
# def lcm(a:int,b:int)->int:
#   return abs(a*b) // gcd(a, b)

class Competition:
  def __init__(self, pop:Population, nrounds:Optional[int]=None):
    self.nrounds=nrounds or 10*int(len(pop.individs))
    self.award=Money(100)
    self.ids=list(range(len(pop.individs)))
    self.pscores:Dict[int,Money]={x:0 for x in self.ids}
    self.rscores:Dict[int,Money]={x:0 for x in self.ids}
    self.log:list=[]

def scores(comp:Competition, i:int)->Float:
  return float(comp.pscores[i]+comp.rscores[i])

def compete(comp:Competition, pop:Population)->None:
  ps=choice(comp.ids, size=comp.nrounds, replace=True)
  rs=choice(comp.ids, size=comp.nrounds, replace=True)
  for p,r in zip(ps,rs):
    offer=propose(pop.individs[p])
    response=respond(pop.individs[r],offer)
    if response:
      comp.pscores[p]+=comp.award*offer
      comp.rscores[r]+=comp.award*(1.0-offer)
    comp.log.append((p,r,offer,response))

class Evolution:
  def __init__(self, cutoff:Float=0.1):
    self.cutoff:Float=cutoff

def mutate_(e:Evolution, s:Strategy)->Tuple[Strategy,int]:
  s2=deepcopy(s)
  nbin=choice(range(len(s2)))
  s2[nbin]+=choice([-1.0/(DISCR+1),1.0/(DISCR+1)])
  s2[nbin]=clip(s2[nbin],0,1.0)
  s2=normalized(s2)
  return s2,nbin

def mutate(e,s):
  return mutate_(e,s)[0]

def evolve(e:Evolution, comp:Competition, pop:Population)->Population:
  nids=len(pop.individs)
  ids2=sorted(comp.ids, key=lambda i:comp.pscores[i]+comp.rscores[i])[int(nids*e.cutoff):]
  inds2=[pop.individs[i] for i in ids2]
  while len(inds2)<nids:
    i=choice(range(len(inds2)))
    ind=inds2[i]
    inds2.append(Individ(mutate(e,ind.pstrategy),mutate(e,ind.rstrategy)))
  return Population(inds2)



# def plot_runtime(
#     name:str,
#     save_png:bool=True
#     )->Callable[[List[Float],Dict[str,Dict[str,Any]]],None]:
#   """ Generic runtime plotter. Take name, return updater function to feed the
#   plot with updated data """
#   fig=plt.figure()
#   ax=fig.add_subplot(1, 1, 1)
#   ax.set_ylabel(name)
#   ax.grid()
#   pl:dict={}

#   def updater(x,ys):
#     nonlocal pl
#     ax.collections.clear()
#     for nm,y in ys.items():
#       ymean=np.array(y['mean'])
#       if (nm+'-mean') not in pl:
#         pl[nm+'-mean']=ax.plot(x,ymean,label=nm,color=y['color'])[0]
#         if 'std' in y:
#           ystd=np.array(y['std'])
#           pl[nm+'-std']=ax.fill_between(x, ymean-ystd, ymean+ystd, facecolor=y['color'], alpha=0.3)
#       else:
#         pl[nm+'-mean'].set_data(x,ymean)
#         # pl[nm+'-std'].set_data(x,ymean-ystd, ymean+ystd)
#         if 'std' in y:
#           ystd=np.array(y['std'])
#           pl[nm+'-std']=ax.fill_between(x, ymean-ystd, ymean+ystd, facecolor=y['color'], alpha=0.3)

#     ax.relim()
#     ax.autoscale_view()
#     ax.legend()
#     fig.canvas.draw()
#     plt.pause(0.00001)  # http://stackoverflow.com/a/24228275
#     if save_png:
#       plt.savefig(name+'.png')

#   return updater



#  ____
# |  _ \ _   _ _ __
# | |_) | | | | '_ \
# |  _ <| |_| | | | |
# |_| \_\\__,_|_| |_|

def runI(nepoch=30000, n=300, nrounds=10*30, cutoff=0.1)->Iterator[Tuple[int,Population]]:
  pop=Population([Individ(mknorm(),mknorm()) for _ in range(n)])
  for epoch in range(nepoch):
    yield epoch,pop
    comp=Competition(pop,nrounds)
    compete(comp,pop)
    e=Evolution(cutoff=cutoff)
    pop2=evolve(e,comp,pop)
    pop=pop2
  yield nepoch,pop


def run1(cwd:Optional[str]=None, *args, **kwargs):
  seed(abs(hash(cwd)) % 2**32)
  if cwd:
    print(f'Building in {cwd}')
    chdir(cwd)

  epoches=[];
  pmeans=[]; rmeans=[]
  # updater=plot_runtime('evolution', save_png=True)
  for i,pop in runI(*args,**kwargs):
    pmean,pstd=strat_stat(pstat(pop).mean_proposer_strategy)
    rmean,rstd=strat_stat(pstat(pop).mean_responder_strategy)
    epoches.append(float(i))
    pmeans.append(pmean); rmeans.append(rmean)
    if i%10 == 0:
      print(i,pmean,pstd,rmean,rstd)
      # updater(epoches,{"Proposer's mean":{'mean':pmeans,'color':'blue'},
      #                  "Responder's mean":{'mean':rmeans,'color':'orange'}})

  with open('history.json','w') as f:
    f.write(json_dumps([epoches, pmeans, rmeans], indent=4))








