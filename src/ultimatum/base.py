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



class Proposer:
  def __init__(self, s:Strategy):
    self.strategy=s

class Responder:
  def __init__(self, s:Strategy):
    self.strategy=s


def propose(p:Proposer)->Offer:
  r=choice(OFFERS,p=p.strategy)
  return r

def respond(r:Responder, to_proposer:Offer)->bool:
  assert_valid_offer(to_proposer)
  to_responder=1.0-to_proposer
  demand=choice(OFFERS,p=r.strategy)
  return to_responder>=demand


class Population:
  def __init__(self, proposers:List[Proposer], responders:List[Responder]):
    self.proposers=proposers
    self.responders=responders

def lcm(a:int,b:int)->int:
  return abs(a*b) // gcd(a, b)


class Competition:
  def __init__(self, pop:Population):
    pop_lcm=lcm(len(pop.proposers),len(pop.responders))
    self.nrounds=int(pop_lcm)
    self.award=Money(100)
    self.pids=list(range(len(pop.proposers)))
    self.rids=list(range(len(pop.responders)))
    self.pscores:Dict[int,Money]={x:0 for x in self.pids}
    self.rscores:Dict[int,Money]={x:0 for x in self.rids}


def compete(comp:Competition, pop:Population)->None:
  ps=choice(pop.proposers, size=comp.nrounds, replace=False)
  rs=choice(pop.responders, size=comp.nrounds, replace=False)
  for p,r in zip(ps,rs):
    offer=propose(pop.proposers[p])
    response=respond(pop.responders[r],offer)
    if response is True:
      comp.pscores[p]+=comp.award*offer
      comp.rscores[r]+=comp.award*(1.0-offer)


class Evolution:
  def __init__(self):
    self.cutoff:Float=0.1

def mutate(e:Evolution, ind:Union[Proposer,Responder])->Tuple[Any,int]:
  ind2=deepcopy(ind)
  nbin=choice(range(len(ind2.strategy)))
  ind2.strategy[nbin]+=choice([-1.0/(DISCR+1),1.0/(DISCR+1)])
  ind2.strategy[nbin]=clip(ind2.strategy[nbin],0,1.0)
  ind2.strategy=normalized(ind2.strategy)
  return ind2,nbin

def evolve(e:Evolution, comp:Competition, pop:Population)->Population:

  def _mutate(ids:List[int], individuals:list, scores:dict):
    ids2=sorted(ids, key=lambda xid:scores[xid])
    ids2=ids2[int(len(ids2)*e.cutoff):]
    p2=[individuals[xid] for xid in ids2]
    while len(p2)<len(ids):
      xid=choice(ids,p=normalized(map(lambda xid:scores[xid],ids)))
      ind,_=mutate(e, individuals[xid])
      p2.append(ind)
    return p2

  ps2=_mutate(comp.pids, pop.proposers, comp.pscores)
  rs2=_mutate(comp.rids, pop.responders, comp.rscores)

  assert len(ps2)==len(pop.proposers)
  assert len(rs2)==len(pop.responders)

  return Population(ps2, rs2)








