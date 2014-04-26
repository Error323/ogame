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
  'ss':[  0e0, 1.0e3, 0.5e3]  # solar satellite
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
  parser.add_argument("--from-res", type=str, choices=RESOURCES,
    help="convert from metal, crystal or deuterium")

  return parser.parse_args()

if __name__ == "__main__":
  # Get commandline config
  config = get_configuration()

  res = map(float, config.res)
  unit_cost = UNITS[config.unit]
  ratios = map(float, config.ratios)
  
  num_units = [0, 0, 0]
  for i in range(0, 3):
    num_units[i] = int(res[i]/unit_cost[i])
  start_res = copy.deepcopy(res)

  max_i, max_v = max(enumerate(num_units), key=operator.itemgetter(1))
  min_i, min_v = min(enumerate(num_units), key=operator.itemgetter(1))

  if config.from_res == None:
    config.from_res = max_i
  else:
    max_i = RESOURCES.index(config.from_res)
    max_v = int(res[max_i]/unit_cost[max_i])

  while True:
    res_to = unit_cost[min_i] - (int(res[min_i]) % unit_cost[min_i])
    res_from = (ratios[max_i]/ratios[min_i]) * res_to

    res[min_i] += res_to
    res[max_i] -= res_from
    
    for i in range(0, 3):
      num_units[i] = int(res[i]/unit_cost[i])
    max_v = num_units[max_i]

    if (res[max_i] - min(num_units)*unit_cost[max_i] < unit_cost[max_i]):
      if (max_v < min_v):
        res[min_i] -= res_to
        res[max_i] += res_from
        
        for i in range(0, 3):
          num_units[i] = int(res[i]/unit_cost[i])
      break

    min_i, min_v = min(enumerate(num_units), key=operator.itemgetter(1))
    
  num_buildable = min(num_units)
  print num_units
  print "\nBuild %d %s as follows (ratio %s)" % (num_buildable, config.unit, ':'.join(config.ratios))
  for i in range(0, 3):
    print "   %dK %s (%dK)" % (num_buildable*unit_cost[i]/1000, RES_STR[i], res[i]/1000)

  others = [i for i in range(0,3) if i != max_i]
  r1 = (num_buildable*unit_cost[others[0]] - start_res[others[0]]) / 1000
  r2 = (num_buildable*unit_cost[others[1]] - start_res[others[1]]) / 1000
  print "\nConvert %s to %dK %s and %dK %s\n" % (RES_STR[max_i], r1, RES_STR[others[0]], r2, RES_STR[others[1]])
