from helper import *
import numpy as np

class A2Designer:
    def __init__(self, file):
        self.r = A2Reader(file)
        self.sheet = self.r.sheet

        get_spec = lambda key, table:\
            self.sheet.range(f'F{self.r.keyrow(key, table)}').value

        # Retrieve specifications...
        # OVERALL GEOMETRY
        self.a = meters(get_spec('A', 1))
        self.b = meters(get_spec('B', 1))
        self.theta = np.arctan(self.b / self.a)

        # CHORD & BRACE GEOMETRY
        self.dchord = meters(get_spec('DCHORD', 1))
        self.tchord = meters(get_spec('TCHORD', 1))
        self.dchord_inner = self.dchord - 2*self.tchord
        # Chord cross-sectional area
        self.chord_area = np.pi / 4 * (self.dchord**2 - self.dchord_inner**2)

        self.dbrace = meters(get_spec('DBRACE', 1))
        self.tbrace = meters(get_spec('TBRACE', 1))
        self.dbrace_inner = self.dbrace - 2*self.tbrace
        # Brace cross-sectional area
        self.brace_area = np.pi / 4 * (self.dbrace**2 - self.dbrace_inner**2)

        self.JOINT = get_spec('JOINT', 1)
        self.JOINTTYPE = get_spec('JOINTTYPE', 1)
        self.SG = get_spec('SG', 1)

        # STRAIN-GAUGE DATA
        strain_row = self.r.keyrow('PEAKSTRAIN', 2)
        self.strains = np.array(self.sheet.range(f'F{strain_row}:H{strain_row}').value) / 10**6
        cycles_row = self.r.keyrow('NPERHOUR', 2)
        self.cycles = np.array(self.sheet.range(f'F{cycles_row}:H{cycles_row}').value)

        self.grav = get_spec('GRAV', 3)
        self.modulus = pa(get_spec('MODULUS', 3))
        self.density = get_spec('DENSITY', 3)
        self.poisson = get_spec('POISSON', 3)
        self.chsyield = get_spec('CHSYIELD', 3)
        self.pinyield = get_spec('PINYIELD', 3)
        self.staticfos = get_spec('STATICFOS', 3)
        self.code = get_spec('CODE', 3)

    def xlwrite(self, rowkey, table, col, val):
        """
        Write to Excel sheet

        Args:
            key: Key of row to write to
            table: Table key appears in
            col: Column to write to
            val: Value to write
        """

        cell = col + self.r.keyrow(rowkey, table)
        self.sheet.range(cell).value = val

    def get_peak_forces(self):
        """
        For Table 2
        """
        load = 1 / 2
        forces_dict = self.get_member_forces(load, return_dict=True)
        sg_force = forces_dict[self.SG]

        return self.strains * self.modulus * self.brace_area / (load / sg_force) * 2

    def get_structure_specs(self):
        """
        For Table 4
        """
        CENTX = mm(5*self.a / 2)
        CENTY = mm(self.b / 2)

        chord_len = 20*self.a
        chord_vol = self.chord_area * chord_len
        brace_len = self.b*12 + np.linalg.norm([self.a, self.b])*10
        brace_vol = self.brace_area * brace_len

        print(self.chord_area)
        print(chord_vol, brace_vol)

        WEIGHT = self.density * (chord_vol + brace_vol)

        grav_force = -WEIGHT * self.grav / 2
        AGRAVY = grav_force
        BGRAVX = 2.5 * self.a * grav_force / self.b
        AGRAVX = -BGRAVX
        BGRAVY = 0 * AGRAVX

        return np.array([CENTX, CENTY, WEIGHT, AGRAVX, AGRAVY, BGRAVX, BGRAVY])


    def get_reactions(self, F):
        """
        Computes all pin loads

        Args:
            F: Total applied load (up is positive)

        Returns:
            Pin loads AFX, AFY, BFX, BFY
        """
        # todo: The below assumes up is positive direction for LOAD,
        # todo: check if this is correct!!
        F = np.array(F) / 2
        BFY = np.abs(F*0)
        BFX = -5*self.a*F / self.b
        AFX = -BFX
        AFY = -F

        return np.array([AFX, AFY, BFX, BFY])

    def get_member_forces(self, F, return_dict=False):
        """
        Computes all member forces

        Args:
            F: Applied load
            return_dict: Whether or not to return the forces in a dict

        Returns:
            All member forces
        """
        AFX, AFY, BFX, BFY = self.get_reactions(F)
        F = np.array(F) / 2

        # todo: Remove this after computing all member forces!!
        # AC, CE, EG, BD, DF, FH, AB, BC, CD, DE, EF, FG, GH = np.zeros((13,) + F.shape)

        # Method of Joints at A
        AC = -AFX
        AB = AFY
        # Method of Joints at B
        BC = F / np.sin(self.theta)
        BD = -BFX - BC * np.cos(self.theta)
        # Method of Joints at C
        CD = -BC
        CE = AC + np.cos(self.theta) * (BC - CD)
        # Method of Joints at D
        DE = -CD
        DF = BD + np.cos(self.theta) * (CD- DE)
        # Method of Joints at E
        EF = -DE
        EG = CE + np.cos(self.theta) * (DE - EF)
        # Method of Joints at F
        FG = -EF
        FH = DF + np.cos(self.theta) * (EF + FG)
        # Method of Joints at G
        GH = -F

        forces = np.array([AC, CE, EG, BD, DF, FH, AB, BC, CD, DE, EF, FG, GH])

        if return_dict:
            forces_dict = {}
            for key in ['AC', 'CE', 'EG', 'BD', 'DF', 'FH', 'AB', 'BC', 'CD', 'DE', 'EF', 'FG', 'GH']:
                forces_dict[key] = locals()[key]

            return forces_dict

        else:
            return forces
