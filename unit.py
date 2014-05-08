import locale

class Unit:
  """
  Ogame unit, both defense or offense
  """
  def __init__(self, name, shortname, cost, combat):
    locale.setlocale(locale.LC_ALL, 'en_GB.utf8')
    self.name = name
    self.shortname = shortname
    self.metal, self.crystal, self.deuterium = cost
    self.attack, self.shield = combat
    self.init_shield = self.shield
    self.shield_unit = self.shield / 100.0
    self.hull = (self.metal + self.crystal) / 10.0
    self.init_hull = self.hull
    self.rfto = {}
    self.rffrom = {}

  @property
  def cost(self):
    return [self.metal, self.crystal, self.deuterium]

  def setcombat(self, w, s, a):
    self.hull = (1.0 + a/10.0) * ((self.metal + self.crystal) / 10.0)
    self.init_hull = self.hull
    self.attack = self.attack * (1.0 + 0.1*w)
    self.shield = self.shield * (1.0 + 0.1*s)
    self.init_shield = self.shield
    self.shield_unit = self.shield / 100.0

  def restore_shield(self):
    self.shield = self.init_shield

  def restore_all(self):
    self.shield = self.init_shield
    self.hull = self.init_hull

  def rapidfire(self, t):
    if self.rfto.has_key(t.shortname):
      r = self.rfto[t.shortname]
      return (r - 1.0) / r
    else:
      return 0.0

  def __repr__(self):
    return self.shortname
    
  def __str__(self):
    s = "%s (%s)\n" % (self.name, self.shortname)
    s += "  cost:   %sm %sc %sd\n" % (locale.format("%d", self.metal, grouping=True),
                                      locale.format("%d", self.crystal, grouping=True),
                                      locale.format("%d", self.deuterium, grouping=True))
    s += "  hull:   %s\n" % (locale.format("%d", self.hull, grouping=True))
    s += "  shield: %s\n" % (locale.format("%d", self.shield, grouping=True))
    s += "  attack: %s\n" % (locale.format("%d", self.attack, grouping=True))
    s += "  rf frm: %s\n" % (self.rffrom)
    s += "  rf to:  %s\n" % (self.rfto)
    return s

  def setrf(self, units):
    for u,r in units.iteritems():
      self.rfto[u.shortname] = r
      u.rffrom[self.shortname] = r


UNITS = {
  'lf':Unit('Light Fighter',   'lf', (3.0e3, 1.0e3, 0.0e0), (5.0e1, 1.0e1)),
  'hf':Unit('Heavy Fighter',   'hf', (6.0e3, 4.0e3, 0.0e0), (1.5e2, 2.5e1)),
  'cr':Unit('Cruiser',         'cr', (2.0e4, 7.0e3, 2.0e3), (4.0e2, 5.0e1)),
  'bs':Unit('Battleship',      'bs', (4.5e4, 1.5e4, 0.0e0), (1.0e3, 2.0e2)),
  'bc':Unit('Battlecruiser',   'bc', (3.0e4, 4.0e4, 1.5e4), (7.0e2, 4.0e2)),
  'bo':Unit('Bomber',          'bo', (5.0e4, 2.5e4, 1.5e4), (1.0e3, 5.0e2)),
  'ds':Unit('Destroyer',       'ds', (6.0e4, 5.0e4, 1.5e4), (2.0e3, 5.0e2)),
  'dt':Unit('Deathstar',       'dt', (5.0e6, 4.0e6, 1.0e6), (2.0e5, 5.0e4)),
  'sc':Unit('Small Cargo',     'sc', (2.0e3, 2.0e3, 0.0e0), (5.0e0, 1.0e1)),
  'lc':Unit('Large Cargo',     'lc', (6.0e3, 6.0e3, 0.0e0), (5.0e0, 2.5e1)),
  'cs':Unit('Colony Ship',     'cs', (1.0e4, 2.0e4, 1.0e4), (5.0e1, 1.0e2)),
  're':Unit('Recycler',        're', (1.0e4, 6.0e3, 2.0e3), (1.0e0, 1.0e1)),
  'ep':Unit('Espionage Probe', 'ep', (0.0e0, 1.0e3, 0.0e0), (1e-3,  1e-3)),
  'ss':Unit('Solar Satellite', 'ss', (0.0e0, 2.0e3, 0.5e3), (1.0e0, 1.0e0)),

  'rl':Unit('Rocket Launcher',   'rl', (2.0e3, 0.0e0, 0.0e0), (8.0e1, 2.0e1)),
  'll':Unit('Light Laser',       'll', (1.5e3, 5.0e2, 0.0e0), (1.0e2, 2.5e1)),
  'hl':Unit('Heavy Laser',       'hl', (6.0e3, 2.0e3, 0.0e0), (2.5e2, 1.0e2)),
  'ic':Unit('Ion Cannon',        'ic', (2.0e3, 6.0e3, 0.0e0), (1.5e2, 5.0e2)),
  'gc':Unit('Gauss Cannon',      'gc', (2.0e4, 1.5e4, 2.0e3), (1.1e3, 2.0e2)),
  'pt':Unit('Plasma Turret',     'pt', (5.0e4, 5.0e4, 3.0e4), (3.0e3, 3.0e2)),
  'sd':Unit('Small Shield Dome', 'sd', (1.0e4, 1.0e4, 0.0e0), (1.0e0, 2.0e3)),
  'ld':Unit('Large Shield Dome', 'ld', (5.0e4, 5.0e4, 0.0e0), (1.0e0, 1.0e4))
}

UNITS['lf'].setrf({UNITS['ep']:5, UNITS['ss']:5})
UNITS['sc'].setrf({UNITS['ep']:5, UNITS['ss']:5})
UNITS['lc'].setrf({UNITS['ep']:5, UNITS['ss']:5})
UNITS['cs'].setrf({UNITS['ep']:5, UNITS['ss']:5})
UNITS['re'].setrf({UNITS['ep']:5, UNITS['ss']:5})
UNITS['hf'].setrf({UNITS['ep']:5, UNITS['ss']:5, UNITS['sc']:3})
UNITS['cr'].setrf({UNITS['ep']:5, UNITS['ss']:5, UNITS['lf']:6, UNITS['rl']:10})
UNITS['bs'].setrf({UNITS['ep']:5, UNITS['ss']:5})
UNITS['bo'].setrf({UNITS['ep']:5, UNITS['ss']:5, UNITS['rl']:20, UNITS['ll']:20, UNITS['hl']:10, UNITS['ic']:10})
UNITS['bc'].setrf({UNITS['ep']:5, UNITS['ss']:5, UNITS['sc']:3, UNITS['lc']:3, UNITS['hf']:4, UNITS['cr']:4, UNITS['bs']:7})
UNITS['ds'].setrf({UNITS['ep']:5, UNITS['ss']:5, UNITS['ll']:10, UNITS['bc']:2})
UNITS['dt'].setrf({UNITS['sc']:250, UNITS['lc']:250, UNITS['lf']:200, UNITS['hf']:100, UNITS['cr']:33, UNITS['bs']:30, UNITS['cs']:250, UNITS['re']:250, UNITS['ep']:1250, UNITS['ss']:1250, UNITS['bo']:25, UNITS['ds']:5, UNITS['rl']:200, UNITS['ll']:200, UNITS['hl']:100, UNITS['gc']:50, UNITS['ic']:100, UNITS['bc']:15})
