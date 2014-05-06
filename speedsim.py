#!/usr/bin/env python

import argparse
import copy
import random
import math
import numpy as np
from unit import *

def get_configuration():
  """Returns a populated configuration"""
  parser = argparse.ArgumentParser(description='Simulate an ogame battle')

  parser.add_argument("--combat-attacker", type=lambda x: x.split(' ')[0], nargs=3,
    required=False, default=('0','0','0'), metavar=('w','s','a'), 
    help="attacker combat research (weapons, shielding, armor)")
  parser.add_argument("--combat-defender", type=lambda x: x.split(' ')[0], nargs=3,
    required=False, default=('0','0','0'), metavar=('w','s','a'), 
    help="defender combat research (weapons, shielding, armor)")
  parser.add_argument("--unit-attacker", type=lambda x: x.split(':'), nargs="+",
    required=True, metavar=('u'), help="define a unit: <name>:<amount>") 
  parser.add_argument("--unit-defender", type=lambda x: x.split(':'), nargs="+",
    required=True, metavar=('u'), help="define a unit: <name>:<amount>") 
  parser.add_argument("--iterations", type=int, default=1,
    help="number of simulations")

  return parser.parse_args()


def attack(a, D, W):
  t = random.randint(0, len(D)-1)
  W[t] += (a.attack > D[t].shield / 100.0) * a.attack
  r = a.rapidfire(D[t])
  if (random.random() < r):
    attack(a, D, W)


def init_defense(D):
  S, H = [], []

  for d in D:
    S.append(d.shield)
    H.append(d.hull)

  return np.array(H), np.array(S)


def init_attack(A, D):
  W = [0.0] * len(D)

  for a in A:
    attack(a, D, W)

  return np.array(W)


def battle(W, S, H, Hi):
  S -= W
  I = S < 0.0
  H[I] += S[I]
  H[H<0.0] = 0.0
  P = H / Hi
  I = P < 0.7
  H[I] = (np.random.random(len(P[I])) >= P[I]) * H[I]


def update(S, H, Hi, D):
  I = H > 0.0
  H = H[I]
  S = S[I]
  Hi = Hi[I]
  D = [x for i,x in enumerate(D) if I[i]]
  return S, H, Hi, D


def simulate(A, D):
  aS, aH = init_defense(D)
  aHi = aH.copy()
  dS, dH = init_defense(A)
  dHi = dH.copy()

  print "%d: %d %d" % (0, len(A), len(D))
  for i in range(6):
    aW = init_attack(A, D)
    dW = init_attack(D, A)
    battle(aW, aS, aH, aHi)
    battle(dW, dS, dH, dHi)
    aS, aH, aHi, D = update(aS, aH, aHi, D)
    dS, dH, dHi, A = update(dS, dH, dHi, A)
    if len(A) == 0 or len(D) == 0:
      break
    print "%d: %d %d" % (i+1, len(A), len(D))


if __name__ == "__main__":
  config = get_configuration()

  attackers = []
  defenders = []

  w, s, h = map(int, config.combat_attacker)
  for ut in config.unit_attacker:
    unit, num = copy.deepcopy(UNITS[ut[0]]), int(ut[1])
    unit.setcombat(w, s, h)
    attackers += [unit] * num

  w, s, h = map(int, config.combat_defender)
  for ut in config.unit_defender:
    unit, num = copy.deepcopy(UNITS[ut[0]]), int(ut[1])
    unit.setcombat(w, s, h)
    defenders += [unit] * num

  for i in range(config.iterations):
    simulate(copy.deepcopy(attackers), copy.deepcopy(defenders))
