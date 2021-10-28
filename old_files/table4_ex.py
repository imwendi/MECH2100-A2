import numpy as np

a = 3000 / 1000
b = 3000 / 1000
cx = 5*a / 2
cy = b / 2
density = 7850 # kg/m^3

c_diam = 165.1 / 1000
c_thick = 5 / 1000
c_diam_inner = c_diam - c_thick * 2
c_area = np.pi*((c_diam / 2)**2 - (c_diam_inner / 2)**2)
c_len = 5*a*(2 + 2)
c_vol = c_area * c_len

b_diam = 76.1 / 1000
b_thick = 4.5 / 1000
b_diam_inner = b_diam - b_thick * 2
b_area = np.pi*((b_diam / 2)**2 - (b_diam_inner / 2)**2)
b_len = b*(6*2) + np.sqrt(a**2 + b**2)*10
b_vol = b_area * b_len

c_mass = density * c_vol
b_mass = density * b_vol
mass = c_mass + b_mass
g = 9.81
#print(mass)

grav_force = -mass * g / 2
AFY = grav_force
BFX = 2.5 * a * grav_force / b
AFX = -BFX
BFY = 0
#print(AFX, AFY, BFX, BFY)
