#!/usr/bin/env python
# coding: latin-1

import argparse
import copy
import random
import verbose as vb
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
  p = 1.0
  while random.random() < p:
    # select target
    t = random.choice(targets)

    # update shield and hull plating
    if (a.attack > t.shield):
      t.hull -= (a.attack - t.shield)
      t.shield = 0.0
    else:
      t.shield -= int(int(a.attack/t.shield_unit)*t.shield_unit)

    # if hull < 70% there's a chance of exploding
    p = t.hull / t.init_hull
    if p < 0.7:
      if random.random() < 1.0 - p:
        t.hull = 0.0

    # perform rapid fire
    p = a.rapidfire(t)


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


def report(R):
  print ""

  print "%s%s%s" % (vb.spacing("Name", 20), vb.spacing("Mean", 10), "Sigma")
  print "------------------------------------"
  colors = ['red', 'green']
  for i,x in enumerate(R):
    for k, v in x.iteritems():
      if len(v) == 0:
        v.append(0.)
      V = np.array(v)
      s = vb.colorize(vb.spacing(UNITS[k].name, 20), colors[i])
      s += vb.colorize(vb.spacing("%0.3f" % (V.mean()), 10), colors[i])
      s += vb.colorize("±%0.3f" % (V.std()), colors[i])
      print s

  print ""
  


if __name__ == "__main__":
  config = get_configuration()

  attackers, defenders = [], []
  A, D = {}, {}

  w, s, h = map(int, config.combat_attacker)
  for ut in config.unit_attacker:
    unit, num = copy.copy(UNITS[ut[0]]), int(ut[1])
    unit.setcombat(w, s, h)
    A[unit.shortname] = [0.0] * config.iterations
    print unit.shortname, num
    for u in range(num):
      attackers.append(copy.copy(unit))

  w, s, h = map(int, config.combat_defender)
  for ut in config.unit_defender:
    unit, num = copy.copy(UNITS[ut[0]]), int(ut[1])
    unit.setcombat(w, s, h)
    D[unit.shortname] = [0.0] * config.iterations
    print unit.shortname, num
    for u in range(num):
      defenders.append(copy.copy(unit))
  
  for i in range(config.iterations):
    for u in attackers:
      u.restore_all()
    for u in defenders:
      u.restore_all()
    a, d = simulate(attackers, defenders)
    for u in a:
      A[u.shortname][i] += 1.0
    for u in d:
      D[u.shortname][i] += 1.0

  report([A, D])
