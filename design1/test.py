from helper import *
from designer import *
import numpy as np

d = A2Designer("c998.xlsx")
pin_loads = d.get_reactions(np.array([88896, 44448, 26669]))

AC, CE, EG, BD, DF, FH, AB, BC, CD, DE, EF, FG, GH = d.get_member_forces(1)
print(BC)

print(d.get_member_forces([88896, 44448, 26669]))


