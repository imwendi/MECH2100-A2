from helper import *

class A2Designer:
    def __init__(self, file):
        self.r = A2Reader(file)
        self.sheet = self.r.sheet

        get_spec = lambda key, table:\
            self.sheet.range(f'F{self.r.keyrow(key, table)}').value

        self.A = get_spec('A', 1)
        self.B = get_spec('B', 1)
        self.DCHORD = get_spec('DCHORD', 1)
        self.TCHORD = get_spec('TCHORD', 1)
        self.JOINT = get_spec('JOINT', 1)
        self.JOINTTYPE = get_spec('JOINTTYPE', 1)
        self.SG = get_spec('SG', 1)

        self.GRAV = get_spec('GRAV', 3)
        self.MODULUS = get_spec('MODULUS', 3)
        self.DENSITY = get_spec('DENSITY', 3)
        self.POISSON = get_spec('POISSON', 3)
        self.CHSYIELD = get_spec('CHSYIELD', 3)
        self.PINYIELD = get_spec('PINYIELD', 3)
        self.STATICFOS = get_spec('STATICFOS', 3)
        self.CODE = get_spec('CODE', 3)

