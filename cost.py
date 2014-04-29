#!/usr/bin/env python

import argparse
import operator
import copy

UNITS = {
  'lf':[3.0e3, 1.0e3,   0e0], # light fighter
  'hf':[6.0e3, 4.0e3,   0e0], # heavy fighter
  'cr':[2.0e4, 7.0e3, 2.0e3], # cruiser
  'bs':[4.5e4, 1.5e4,   0e0], # battleship
  'bc':[3.0e4, 4.0e4, 1.5e4], # battlecruiser
  'bo':[5.0e4, 2.5e4, 1.5e4], # bomber
  'ds':[6.0e4, 5.0e4, 1.5e4], # destroyer
  'dt':[5.0e6, 4.0e6, 1.0e6], # deathstar
  'sc':[2.0e3, 2.0e3,   0e0], # small cargo
  'lc':[6.0e3, 6.0e3,   0e0], # large cargo
  'cs':[1.0e4, 2.0e4, 1.0e4], # colony ship
  're':[1.0e4, 6.0e3, 2.0e3], # recycler
  'es':[  0e0, 1.0e3,   0e0], # espionage probe
  'ss':[  0e0, 2.0e3, 0.5e3]  # solar satellite
}

RES_STR = ['metal', 'crystal', 'deuterium']
RESOURCES = [i[0] for i in RES_STR]

def get_configuration():
  """Returns a populated configuration"""
  parser = argparse.ArgumentParser(
    description='Compute optimal resource configuration'
  )
  parser.add_argument('--unit', type=str, required=True, choices=UNITS.keys(),
    help='select the unit to be built')
  parser.add_argument("--res", type=lambda x: x.split(' ')[0], nargs=3,
    required=True, metavar=tuple(RESOURCES), help="resources in stock")
  parser.add_argument("--ratios", type=lambda x: x.split(':'),
    default="3:2:1", help="trading ratios m:c:d (default %(default)s)")

  return parser.parse_args()


def print_actions(actions, num_units, config):
  """Pretty print the actions to take"""
  if num_units == 0:
    print "\n  Not enough resources\n"
    return

  print "\n  Build %d '%s' (ratio %s)" % (num_units, config.unit, ':'.join(config.ratios))
  for a in actions:
    if a[0] > 0:
      print "    Convert %s to %dK %s" % (RES_STR[a[1]], a[0]/1000, RES_STR[a[2]])
  print ""
  

def get_units_per_res(resources, cost):
  """Compute number of units available per resource"""
  num_units = []
  for i,j in enumerate(resources):
    if i < len(cost) and cost[i] > 0.0:
      num_units.append(int(j / cost[i]))

  return num_units


def convert_res(from_index, to_index, resource, ratios):
  """Convert a resource from a to b using the proper ratios"""
  return (ratios[from_index] / ratios[to_index]) * resource
    

def maximize2(includes, unit_cost, resources, ratios):
  """Maximize the unitcount given a resource to convert from and convert to"""
  unit_list = get_units_per_res(resources, unit_cost)
  best = min(unit_list)

  while True:
    i, num = min(enumerate(unit_list), key=operator.itemgetter(1))
    j, _ = max(enumerate(unit_list), key=operator.itemgetter(1))

    if num >= best:
      best = num
    else:
      break

    if i == j:
      break

    step_size = convert_res(includes[j], includes[i], unit_cost[includes[i]], ratios)
    resources[includes[j]] -= step_size
    resources[includes[i]] += unit_cost[includes[i]]
    unit_list = get_units_per_res(resources, unit_cost)
    #print "%s -> %s\t%s : %s" % (RESOURCES[includes[j]], RESOURCES[includes[i]], unit_list, resources)

  return best
    
def maximize3(exc, inc, unit_cost, resources, ratios):
  """Maximize the unitcount given a resource to convert from and convert to"""
  unit_list = get_units_per_res(resources, unit_cost)
  best = min(unit_list)

  while True:
    i, num = min(enumerate(unit_list), key=operator.itemgetter(1))

    if num >= best:
      best = num

    step_size = convert_res(exc, inc[i], unit_cost[inc[i]], ratios)

    if resources[exc] < step_size:
      break

    resources[exc] -= step_size
    resources[inc[i]] += unit_cost[inc[i]]
    unit_list = get_units_per_res(resources, unit_cost)
    #print "%s -> %s\t%s : %s" % (RESOURCES[exc], RESOURCES[inc[i]], unit_list, resources)

  return best
  

def maximize(from_index, unit_cost, resources, ratios):
  """Maximize the unitcount given a resource to convert from"""
  unit_list = get_units_per_res(resources, unit_cost)
  best = min(unit_list)

  while True:
    i, num = min(enumerate(unit_list), key=operator.itemgetter(1))

    if num >= best:
      best = num
    else:
      break

    if unit_list.count(num) == len(unit_list) or i == from_index:
      break

    step_size = convert_res(from_index, i, unit_cost[i], ratios)
    resources[from_index] -= step_size
    resources[i] += unit_cost[i]
    unit_list = get_units_per_res(resources, unit_cost)
    #print "%s -> %s\t%s : %s" % (RESOURCES[from_index], RESOURCES[i], unit_list, resources)

  return best


if __name__ == "__main__":
  config = get_configuration()

  res = map(float, config.res)
  unit_cost = UNITS[config.unit]
  ratios = map(float, config.ratios)
  
  num_units = get_units_per_res(res, unit_cost)
  size = len(num_units)
  if (size == 1):
    inc, exc = -1, []
    for i in range(0, 3):
      if unit_cost[i] > 0.0:
        inc = i
      else:
        exc.append(i)
    a = convert_res(inc, exc[0], res[exc[0]], ratios)
    b = convert_res(inc, exc[1], res[exc[1]], ratios)
    best = (res[inc] + a + b) / unit_cost[inc]
    actions = [(a, exc[0], inc), (b, exc[1], inc)]
    print_actions(actions, best, config)
  elif (size == 2):
    # 1. convert used resource that has highest number of units to other used
    # resource
    inc, exc = [], -1
    for i in range(0, 3):
      if unit_cost[i] > 0.0:
        inc.append(i)
      else:
        exc = i
    i, _ = max(enumerate(num_units), key=operator.itemgetter(1))
    j = 1 - i
    start_res = copy.deepcopy(res)
    a = maximize2(inc, unit_cost, start_res, ratios)
    ac = a*unit_cost[inc[j]] - res[inc[j]]

    # 2. convert unused resource to one or both used resources
    start_res = copy.deepcopy(res)
    b = maximize3(exc, inc, unit_cost, start_res, ratios)
    bc1 = b*unit_cost[inc[i]] - res[inc[i]]
    bc2 = b*unit_cost[inc[j]] - res[inc[j]]

    # 3. max unitcount of those
    actions = []
    if (a > b):
      actions.append((ac, inc[i], inc[j]))
      best = a
    else:
      actions.append((bc1, exc, inc[i]))
      actions.append((bc2, exc, inc[j]))
      best = b
    print_actions(actions, best, config)
      
  else:
    from_index, _ = max(enumerate(num_units), key=operator.itemgetter(1))
    start_res = copy.deepcopy(res)
    best = maximize(from_index, unit_cost, start_res, ratios)
    res_indices = [i for i in range(0, 3) if i != from_index]
    actions = [(best*unit_cost[i]-res[i], from_index, i) for i in res_indices]
    print_actions(actions, best, config)
