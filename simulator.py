#!/usr/bin/env python

import argparse
import copy
import random
import math
from unit import *

def get_configuration():
  """Returns a populated configuration"""
  parser = argparse.ArgumentParser(description='Simulate an ogame battle')

  parser.add_argument("--combat-attacker", type=lambda x: x.split(' ')[0], nargs=3,
    required=False, metavar=('w','s','a'), 
    help="attacker combat research (weapons, shielding, armor)")
  parser.add_argument("--combat-defender", type=lambda x: x.split(' ')[0], nargs=3,
    required=False, metavar=('w','s','a'), 
    help="defender combat research (weapons, shielding, armor)")
  parser.add_argument("--unit-attacker", type=lambda x: x.split(':'), nargs="+",
    required=True, metavar=('u'), help="define a unit: <name>:<amount>") 
  parser.add_argument("--unit-defender", type=lambda x: x.split(':'), nargs="+",
    required=True, metavar=('u'), help="define a unit: <name>:<amount>") 

  return parser.parse_args()

def attack(a, targets):
    # select target
    t = random.choice(targets)

    if a.attack > t.shield/100.0:
      # update shield and hull plating
      t.shield -= a.attack
      if t.shield < 0.0:
        t.hp += t.shield
        t.shield = 0.0

    # if hp < 70% there's a chance of exploding
    if t.hp < t.init_hp*0.7:
      p = 1.0 - (t.hp / float(t.init_hp))
      if random.random() < p:
        t.hp = 0.0

    # perform rapid fire
    if a.rfto.has_key(t.shortname):
      r = float(a.rfto[t.shortname])
      p = (r - 1.0) / r
      if random.random() < p:
        attack(a, targets)


def restore(attacker):
  attacker.shield = attacker.init_shield

def simulate(attackers, defenders):
  at_lost = [0.0, 0.0, 0.0]
  df_lost = [0.0, 0.0, 0.0]

  print "%d: %d, %d" % (0, len(attackers), len(defenders))
  for r in range(6):
    for a in attackers:
      attack(a, defenders)

    for d in defenders:
      attack(d, attackers)

    for a in attackers:
      if a.hp <= 0.0:
        at_lost[0] += a.metal
        at_lost[1] += a.crystal
        at_lost[2] += a.deuterium

    for d in defenders:
      if d.hp <= 0.0:
        df_lost[0] += d.metal
        df_lost[1] += d.crystal
        df_lost[2] += d.deuterium

    attackers = filter(lambda x: x.hp > 0.0, attackers)
    defenders = filter(lambda x: x.hp > 0.0, defenders)

    for a in attackers:
      restore(a)

    for d in defenders:
      restore(d)

    print "%d: %d, %d" % (r+1, len(attackers), len(defenders))
    if len(attackers) == 0 or len(defenders) == 0:
      break

  print at_lost,df_lost


if __name__ == "__main__":
  config = get_configuration()

  attackers = []
  defenders = []
  for ut in config.unit_attacker:
    for u in range(int(ut[1])):
      attackers.append(copy.deepcopy(UNITS[ut[0]]))

  for ut in config.unit_defender:
    for u in range(int(ut[1])):
      defenders.append(copy.deepcopy(UNITS[ut[0]]))

  simulate(attackers, defenders)
