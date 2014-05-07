#!/usr/bin/env python

import argparse
import copy
import random
import numpy as np
from unit import *

def get_configuration():
  """Returns a populated configuration"""
  parser = argparse.ArgumentParser(description='Simulate an ogame battle')

  parser.add_argument("--combat-attacker", type=lambda x: x.split(' ')[0], nargs=3,
    required=False, default=('0','0','0'), metavar=('w','s','h'), 
    help="attacker combat research (weapons, shielding, hull)")
  parser.add_argument("--combat-defender", type=lambda x: x.split(' ')[0], nargs=3,
    required=False, default=('0','0','0'), metavar=('w','s','h'), 
    help="defender combat research (weapons, shielding, hull)")
  parser.add_argument("--unit-attacker", type=lambda x: x.split(':'), nargs="+",
    required=True, metavar=('u'), help="define a unit: <name>:<amount>") 
  parser.add_argument("--unit-defender", type=lambda x: x.split(':'), nargs="+",
    required=True, metavar=('u'), help="define a unit: <name>:<amount>") 
  parser.add_argument("--iterations", type=int, default=1,
    help="number of simulations")

  return parser.parse_args()

def attack(a, targets):
    # select target
    t = random.choice(targets)

    # check if the shot bounces
    if a.attack > t.shield/100.0:
      # update shield and hull plating
      t.shield -= a.attack
      if t.shield < 0.0:
        t.hull += t.shield
        t.shield = 0.0

    # if hull < 70% there's a chance of exploding
    p = t.hull / t.init_hull
    if p < 0.7:
      if random.random() < 1.0 - p:
        t.hull = 0.0

    # perform rapid fire
    if random.random() < a.rapidfire(t):
      attack(a, targets)


def simulate(attackers, defenders):
  for r in range(6):
    for a in attackers:
      a.restore_shield()
      attack(a, defenders)

    for d in defenders:
      d.restore_shield()
      attack(d, attackers)

    attackers = filter(lambda x: x.hull > 0.0, attackers)
    defenders = filter(lambda x: x.hull > 0.0, defenders)

    if len(attackers) == 0 or len(defenders) == 0:
      break

  return attackers, defenders


if __name__ == "__main__":
  config = get_configuration()

  attackers = []
  defenders = []

  w, s, h = map(int, config.combat_attacker)
  for ut in config.unit_attacker:
    unit = copy.copy(UNITS[ut[0]])
    unit.setcombat(w, s, h)
    for u in range(int(ut[1])):
      attackers.append(copy.copy(unit))

  w, s, h = map(int, config.combat_defender)
  for ut in config.unit_defender:
    unit = copy.copy(UNITS[ut[0]])
    unit.setcombat(w, s, h)
    for u in range(int(ut[1])):
      defenders.append(copy.copy(unit))

  res_a = np.array([0.0] * config.iterations)
  res_d = np.array([0.0] * config.iterations)
  for i in range(config.iterations):
    for u in attackers:
      u.restore_all()
    for u in defenders:
      u.restore_all()
    a, d = simulate(attackers, defenders)
    res_a[i] = len(a)
    res_d[i] = len(d)

  print "%0.3f %0.3f %0.3f %0.3f" % (res_a.mean(), res_a.std(), res_d.mean(), res_d.std())
