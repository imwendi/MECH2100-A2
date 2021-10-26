import numpy as np
from melib import library

a = 1
b = 1
theta = np.arctan(b / a)
FBC = 0.71
d_brace = 76.1 / 1000
t_brace = 4.5 / 1000
d_brace_inner = d_brace - t_brace * 2
a_brace = ((d_brace / 2)**2 - (d_brace_inner / 2)**2) * np.pi
sig = FBC / a_brace
E = 207 * 10**9

print(300*10**(-6)*E*a_brace / np.sin(theta))

