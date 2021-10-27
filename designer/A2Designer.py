from helper import *
import numpy as np

class A2Designer:
    def __init__(self, file):
        self.r = A2Reader(file)
        self.sheet = self.r.sheet

        get_spec = lambda key, table:\
            self.sheet.range(f'F{self.r.keyrow(key, table)}').value

        # Retrieve specifications
        self.a = meters(get_spec('A', 1))
        self.b = meters(get_spec('B', 1))
        self.theta = np.arctan(self.b / self.a)

        self.DCHORD = meters(get_spec('DCHORD', 1))
        self.TCHORD = meters(get_spec('TCHORD', 1))
        self.DBRACE = meters(get_spec('DBRACE', 1))
        self.TBRACE = meters(get_spec('TBRACE', 1))
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
        AC, CE, EG, BD, DF, FH, AB, BC, CD, DE, EF, FG, GH = self.get_member_forces(1)



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
