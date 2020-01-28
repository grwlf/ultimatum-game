import numpy as np
import matplotlib.pyplot as plt

from numpy import linspace, array, arange, isclose
from numpy.random import choice, uniform
from collections import defaultdict
from typing import Dict,List

from ultimatum.base import (normalized, mutate, Evolution, mkuniform, mknorm,
    Strategy, OFFERS, assert_valid_offer, propose, respond, Individ, mutate_,
    Competition, compete, Population, evolve, scores, istat, pstat,
    mean_strategy, strat_mean, strat_std, run1, run )



def pop1(n=30)->Population:
  return Population([Individ(mkuniform(),mkuniform()) for x in range(n)])

def mknoob()->Individ:
  return Individ(normalized([1 if x==0.0 else 0.0 for x in OFFERS]),
                 normalized([1 if x==1.0 else 0.0 for x in OFFERS]))
def isnoob(i:Individ)->bool:
  return i.pstrategy[0]==1.0 and i.rstrategy[-1]==1.0

def plotstrategy(s:Strategy)->None:
  plt.bar(arange(len(s)), height=s)


def demo_random():
  vals=linspace(0,100,num=101)
  # probs=normalized([(5 if (x<10 or x>40) else 20) for x in vals])
  probs=mknorm()

  nsamples:int=3000
  samples:List[np.float32]=[]
  for n in range(nsamples):
    r=choice(vals,p=probs)
    samples.append(r)

  plt.figure()
  plt.subplot(211)
  plt.bar(arange(len(probs)), height=probs)
  plt.subplot(212)
  plt.hist(samples,bins=101)
  plt.show()


def demo_mutate():
  e=Evolution()
  s=mknorm()
  s2,nbin=mutate_(e, s)
  plotstrategy(s)
  plotstrategy(s2)
  plt.show()


def demo_meanstrat():
  ss=[mknorm() for _ in range(30)]
  ms=mean_strategy(ss)
  plotstrategy(ms)
  plt.show()
  print(strat_mean(ms), strat_std(ms))



#  _____         _
# |_   _|__  ___| |_ ___
#   | |/ _ \/ __| __/ __|
#   | |  __/\__ \ |_\__ \
#   |_|\___||___/\__|___/



def test_mutate():
  e=Evolution()
  st=mkuniform()
  s=set(range(len(st)))
  for i in range(1000):
    st2,nbin=mutate_(e, st)
    s-=set([nbin])

  assert s==set([])


def test_propose():
  p=Individ(normalized([(0 if (x<0.1 or x>0.4) else 20) for x in OFFERS]),mkuniform())
  for x in range(1000):
    offer=propose(p)
    assert_valid_offer(offer)
    assert (offer>=0.1 and offer<=0.4)

def test_response():
  r=Individ(mkuniform(), normalized([(0.0 if (x<0.1 or x>0.4) else 20.0) for x in OFFERS]))
  r1s=set(); r2s=set(); r3s=set()
  for x in range(1000):
    r1s.add(respond(r, 1.0-0.05))
    r2s.add(respond(r, 1.0-0.2))
    r3s.add(respond(r, 1.0-0.9))
  assert r1s==set([False]), f"{r1s}"
  assert r2s==set([False,True]), f"{r2s}"
  assert r3s==set([True]), f"{r3s}"

def test_noob():
  assert istat(mknoob()) == (0.0,1.0)
  p=Population([mknoob(),mknoob()])
  assert strat_mean(pstat(p).mean_proposer_strategy)==0.0
  assert strat_mean(pstat(p).mean_responder_strategy)==1.0
  p2=Population([mknoob(),Individ(mkuniform(),mkuniform())])
  assert strat_mean(pstat(p2).mean_proposer_strategy)>0.0

def test_compete():
  for i in range(100):
    pop=Population([mknoob(),Individ(mkuniform(),mkuniform())])
    assert isnoob(pop.individs[0])
    comp=Competition(pop,10)
    compete(comp,pop)
    # print('--->', comp.pscores, comp.rscores)
    assert comp.pscores[0] == 0
    assert comp.rscores[0] == 0, f"{comp.log}"
    assert scores(comp,0) <= scores(comp,1), f"{scores(comp,0)} should be < {scores(comp,1)}"

def test_evolve():
  for i in range(100):
    pop=Population([mknoob(),Individ(mkuniform(),mkuniform())])
    comp=Competition(pop,10)
    compete(comp,pop)
    assert scores(comp,0)==0
    e=Evolution(0.5)
    pop2=evolve(e,comp,pop)
    for i in pop2.individs:
      assert not isnoob(i)

def test_mean_strategy():
  ms=mean_strategy([mkuniform(), mknorm()])
  s=np.sum(ms)
  assert isclose(s,1.0), f"{s}"

