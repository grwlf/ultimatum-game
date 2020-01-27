import numpy as np

from numpy import linspace, array, arange, clip
from numpy.random import choice, uniform
from typing import Any, Optional, List, Dict, Union, Tuple
from math import gcd
from copy import deepcopy
from scipy.stats import norm

DISCR=100
OFFERS=linspace(0.0,1.0,num=DISCR+1)

Float=float
Offer=float
Money=float
Strategy=List[Float]


def assert_valid_offer(o:Offer)->None:
  assert o>=0.0 and o<=1.0, f"Invalid offer {o}"

def normalized(x):
  p=array(x)
  p=p/sum(p)
  return p


def mknorm()->Strategy:
  mu=uniform(0,100)
  sigma=uniform(0.5,10)
  return normalized([norm.pdf(x,mu,sigma) for x in OFFERS])

def mkuniform()->Strategy:
  return normalized([1.0 for x in OFFERS])



class Individ:
  def __init__(self, ps:Strategy, rs:Strategy):
    self.pstrategy=ps
    self.rstrategy=rs


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
  # print(int(nids*e.cutoff))

  ids2=sorted(comp.ids, key=lambda i:comp.pscores[i]+comp.rscores[i])[int(nids*e.cutoff):]
  inds2=[pop.individs[i] for i in ids2]
  # print('passed',ids2)

  while len(inds2)<nids:
    i=choice(range(len(inds2)))
    ind=inds2[i]
    inds2.append(Individ(mutate(e,ind.pstrategy),mutate(e,ind.rstrategy)))

  return Population(inds2)








