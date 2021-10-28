from helper import *
from designer import *
import numpy as np

d = A2Designer("c998.xlsx")
specs = d.get_structure_specs()
print(specs)