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
    unit = copy.copy(UNITS[ut[0]])
    unit.setcombat(w, s, h)
    A[unit.shortname] = []
    for u in range(int(ut[1])):
      attackers.append(copy.copy(unit))

  w, s, h = map(int, config.combat_defender)
  for ut in config.unit_defender:
    unit = copy.copy(UNITS[ut[0]])
    unit.setcombat(w, s, h)
    D[unit.shortname] = []
    for u in range(int(ut[1])):
      defenders.append(copy.copy(unit))
  
  for i in range(config.iterations):
    for u in attackers:
      u.restore_all()
    for u in defenders:
      u.restore_all()
    a, d = simulate(attackers, defenders)
    ta, td = {}, {}
    for u in a:
      if not ta.has_key(u.shortname):
        ta[u.shortname] = 0
      ta[u.shortname] += 1
    for u in d:
      if not td.has_key(u.shortname):
        td[u.shortname] = 0
      td[u.shortname] += 1
    for k, v in ta.iteritems():
      A[k].append(v)
    for k, v in td.iteritems():
      D[k].append(v)

  report([A, D])
