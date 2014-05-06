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
  loss_a = {}
  loss_d = {}

  print "%d: %d, %d" % (0, len(attackers), len(defenders))
  for r in range(6):
    for a in attackers:
      attack(a, defenders)

    for d in defenders:
      attack(d, attackers)

    for a in attackers:
      if a.hull <= 0.0:
        if not loss_a.has_key(a.shortname):
          loss_a[a.shortname] = 0
        loss_a[a.shortname] += 1

    for d in defenders:
      if d.hull <= 0.0:
        if not loss_d.has_key(d.shortname):
          loss_d[d.shortname] = 0
        loss_d[d.shortname] += 1

    attackers = filter(lambda x: x.hull > 0.0, attackers)
    defenders = filter(lambda x: x.hull > 0.0, defenders)

    for a in attackers:
      restore(a)

    for d in defenders:
      restore(d)

    print "%d: %d, %d" % (r+1, len(attackers), len(defenders))
    if len(attackers) == 0 or len(defenders) == 0:
      break

  return loss_a, loss_d


if __name__ == "__main__":
  config = get_configuration()

  attackers = []
  defenders = []

  w, s, h = map(int, config.combat_attacker)
  for ut in config.unit_attacker:
    for u in range(int(ut[1])):
      unit = copy.deepcopy(UNITS[ut[0]])
      unit.setcombat(w, s, h)
      attackers.append(unit)

  w, s, h = map(int, config.combat_defender)
  for ut in config.unit_defender:
    for u in range(int(ut[1])):
      unit = copy.deepcopy(UNITS[ut[0]])
      unit.setcombat(w, s, h)
      defenders.append(unit)

  for i in range(config.iterations):
    simulate(copy.deepcopy(attackers), copy.deepcopy(defenders))
