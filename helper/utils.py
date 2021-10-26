"""
Useful utility functions

"""
import numpy as np

# Compute percentage error
def calc_error(expected, actual, abs=False):
    difference = expected - actual
    if abs:
        difference = np.abs(difference)

    return difference / expected

# RPM to rad/s
def rpm2rads(speed):
    return speed*2*np.pi / 60

# rad/s to RPM
def rads2rpm(speed):
    return speed/(2*np.pi) * 60

# Pa to MPa
def mpa(stress):
    return stress / (10**6)

# m to mm
def mm(dist):
    return dist * 1000

# mm to m
def meters(dist):
    return dist / 1000