from designer import *
from helper import *

# Helper to retrieve the correct sheet & row/table dicts
d_helper = A2Designer("i1s45814075.xlsx")
# Helper to retrive the right specs
d = A2Designer("c998.xlsx")
# Copy the correct sheet & row/table dicts into d
d.r = d_helper.r
d.sheet = d_helper.sheet

print(d.get_adjusted_stresses(d.get_peak_forces()))