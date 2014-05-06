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

    if a.attack > t.shield/100.0:
      # update shield and hull plating
      t.shield -= a.attack
      if t.shield < 0.0:
        t.hull += t.shield
        t.shield = 0.0

    # if hull < 70% there's a chance of exploding
    if t.hull < t.init_hull*0.7:
      p = 1.0 - (t.hull / float(t.init_hull))
      if random.random() < p:
        t.hull = 0.0

    # perform rapid fire
    if a.rfto.has_key(t.shortname):
      r = float(a.rfto[t.shortname])
      p = (r - 1.0) / r
      if random.random() < p:
        attack(a, targets)


def restore(attacker):
  attacker.shield = attacker.init_shield

def simulate(attackers, defenders):
  #print "%d: %d, %d" % (0, len(attackers), len(defenders))
  for r in range(6):
    for a in attackers:
      restore(a)
      attack(a, defenders)

    for d in defenders:
      restore(d)
      attack(d, attackers)

    attackers = filter(lambda x: x.hull > 0.0, attackers)
    defenders = filter(lambda x: x.hull > 0.0, defenders)

    #print "%d: %d, %d" % (r+1, len(attackers), len(defenders))
    if len(attackers) == 0 or len(defenders) == 0:
      break

  return len(attackers), len(defenders)


if __name__ == "__main__":
  config = get_configuration()

  attackers = []
  defenders = []

  w, s, h = map(int, config.combat_attacker)
  for ut in config.unit_attacker:
    unit = copy.deepcopy(UNITS[ut[0]])
    unit.setcombat(w, s, h)
    for u in range(int(ut[1])):
      attackers.append(copy.deepcopy(unit))

  w, s, h = map(int, config.combat_defender)
  for ut in config.unit_defender:
    unit = copy.deepcopy(UNITS[ut[0]])
    unit.setcombat(w, s, h)
    for u in range(int(ut[1])):
      defenders.append(copy.deepcopy(unit))

  for i in range(config.iterations):
    a, d = simulate(copy.deepcopy(attackers), copy.deepcopy(defenders))
    print a, d
