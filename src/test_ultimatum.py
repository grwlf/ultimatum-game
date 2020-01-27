import numpy as np
import matplotlib.pyplot as plt

from numpy import linspace, array, arange
from numpy.random import choice, uniform
from collections import defaultdict
from typing import Dict,List

from ultimatum.base import (normalized, mutate, Evolution, mkuniform,
    mknorm, Strategy, OFFERS, assert_valid_offer, propose, respond, Individ,
    mutate_ )

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



def plotstrategy(s:Strategy)->None:
  plt.bar(arange(len(s)), height=s)


def demo_mutate():
  e=Evolution()
  s=mknorm()
  s2,nbin=mutate_(e, s)
  plotstrategy(s)
  plotstrategy(s2)
  plt.show()



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



