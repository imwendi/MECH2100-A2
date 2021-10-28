from helper import *
import numpy as np
from melib.library import ec3life

class A2Designer:
    def __init__(self, file):
        self.r = A2Reader(file)
        self.wb = self.r.wb
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

        self.joint = get_spec('joint', 1)
        self.jointtype = get_spec('jointtype', 1)
        self.sg = get_spec('sg', 1)

        # STRAIN-GAUGE DATA
        strain_row = self.r.keyrow('PEAKSTRAIN', 2)
        self.strains = np.array\
                           (self.sheet.range
                            (f'F{strain_row}:H{strain_row}').value) / 10**6
        nperhour_row = self.r.keyrow('NPERHOUR', 2)
        self.nperhour = np.array\
                            (self.sheet.range
                             (f'F{nperhour_row}:H{nperhour_row}').value) / 8

        self.grav = get_spec('GRAV', 3)
        self.modulus = pa(get_spec('MODULUS', 3))
        self.density = get_spec('DENSITY', 3)
        self.poisson = get_spec('POISSON', 3)
        self.chsyield = get_spec('CHSYIELD', 3)
        self.pinyield = get_spec('PINYIELD', 3)
        self.staticfos = get_spec('STATICFOS', 3)
        self.code = get_spec('CODE', 3)

        # Members specified for analysis in the assignment
        self.members = list(self.r.tabledict[8].keys())


    def get_reactions(self, F):
        """
        Computes all pin reaction forces

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
        DF = BD + np.cos(self.theta) * (CD - DE)
        # Method of Joints at E
        EF = -DE
        EG = CE + np.cos(self.theta) * (DE - EF)
        # Method of Joints at F
        FG = -EF
        #FH = DF + np.cos(self.theta) * (EF - FG)
        FH = DF*0
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

    def get_peak_forces(self):
        """
        For Table 2
        """
        load = 1 / 2
        forces_dict = self.get_member_forces(load, return_dict=True)
        sg_force = forces_dict[self.sg]

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

        WEIGHT = self.density * (chord_vol + brace_vol)

        grav_force = -WEIGHT * self.grav / 2
        AGRAVY = grav_force
        BGRAVX = 2.5 * self.a * grav_force / self.b
        AGRAVX = -BGRAVX
        BGRAVY = 0 * AGRAVX

        return np.array([CENTX, CENTY, WEIGHT, AGRAVX, AGRAVY, BGRAVX, BGRAVY])

    def get_nominal_stresses(self, F):
        d = self.get_member_forces(F, return_dict=True)
        forces = np.array([d[key] for key in self.members])
        areas = np.concatenate((np.ones((1, 1)) * self.chord_area, np.ones((3, 1)) * self.brace_area))

        return forces / areas

    def get_magnification_factors(self):
        # Choose brace magnification factor depending on if the joint to
        # analyse is a K or N joint
        if self.joint in ['A', 'B', 'G', 'H']:
            # N joint
            brace_fac = 1.25
        else:
            # K joint
            brace_fac = 1.2

        factors = np.zeros((4, 1))
        for i, member in enumerate(self.members):
            if member in ['AB', 'BC', 'CD', 'DE', 'EF', 'FG', 'GH']:
                if member in ['AB', 'GH']:
                    # Diagonal brace

                    factors[i] = 1.65
                else:
                    # Vertical brace
                    factors[i] = brace_fac
            else:
                # The member is a chord
                factors[i] = 1.5

        return np.array([1.5, 1.2, 1.5, 1.2])

    def get_adjusted_stresses(self, F):
        return mpa(self.get_nominal_stresses(F) *\
               np.reshape(self.get_magnification_factors(), (4, 1)))

    def get_fatigue_life(self, F):
        tr = self.tchord / self.tbrace
        #todo: Are A and H actually N joints?
        joint = 'N' if self.joint in ['A', 'B', 'G', 'H'] else 'K'
        stresses = np.abs(self.get_adjusted_stresses(F))
        ec3lifes = np.zeros(stresses.shape)

        # Temporarily disable divide by 0 warning
        np.seterr(divide='ignore')

        for (i, j), stress in np.ndenumerate(stresses):
            ec3lifes[i, j] = ec3life(stress, tr, joint)[0]

        overall_ec3life = np.min((np.sum(self.nperhour / ec3lifes, axis=1))**(-1))

        # Restore error setting
        np.seterr(divide='warn')

        return overall_ec3life

    def xlwrite(self, table, rowkey, col, val):
        """
        Write to Excel sheet

        Args:
            table: Table key appears in
            rowkey: Key of row to write to
            col: Column to write to
            val: Value to write
        """
        cell = col + str(self.r.keyrow(rowkey, table))
        self.sheet.range(cell).value = val

    def write_excel(self):
        """
        Fills the Excel sheet
        """
        # Fill tables
        peak_forces = self.get_peak_forces()
        print("Writing Table 2...")
        self.xlwrite(2, 'PEAKFORCE', 'F', peak_forces)

        print("Writing Table 4...")
        self.xlwrite(4, 'CENTX', 'F', np.reshape(self.get_structure_specs(), (7, 1)))

        print("Writing Table 5...")
        self.xlwrite(5, 'AC', 'F', self.get_member_forces(peak_forces))

        print("Writing Table 6...")
        # Pin loads are negative of the pin reaction forces
        self.xlwrite(6, 'AFX', 'F', -self.get_reactions(peak_forces))

        print("Writing Table 7...")
        self.xlwrite(7, 'BD', 'F', mpa(self.get_nominal_stresses(peak_forces)))

        print("Writing Table 8...")
        tab789_first_key = list(self.r.tabledict[8].keys())[0]
        self.xlwrite(8, tab789_first_key, 'F', np.reshape(self.get_magnification_factors(), (4, 1)))

        print("Writing Table 9...")
        self.xlwrite(9, tab789_first_key, 'F', self.get_adjusted_stresses(peak_forces))

        print()
        print("Finished writing to the spreadsheet!!")

        self.wb.save()