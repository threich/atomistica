# ======================================================================
# Atomistica - Interatomic potential library
# https://github.com/pastewka/atomistica
# Lars Pastewka, lars.pastewka@iwm.fraunhofer.de, and others.
# See the AUTHORS file in the top-level Atomistica directory.
#
# Copyright (2005-2013) Fraunhofer IWM
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ======================================================================

#! /usr/bin/env python

import sys

import numpy as np

import ase
from ase.io import read
from ase.units import mol
from mdcore.io import read

import mdcore.native as native

###

# Default parameters
nbins = 100
cutoff = 5.0
avgn = 100

import getopt
optlist, args = getopt.getopt(sys.argv[1:], '',
                              [ 'nbins=', 'cutoff=',
                                'avgn=' ])

assert len(args) == 1
fn = args[0]
for key, value in optlist:
    if key == '--nbins':
        nbins = int(value)
    elif key == '--cutoff':
        cutoff = float(value)
    elif key == '--avgn':
        avgn = int(value)

###

print '# fn = ', fn
print '# nbins = ', nbins
print '# cutoff = ', cutoff
print '# avgn = ', avgn

###

a = read(fn)

print '{0} atoms.'.format(len(a))

p = native.from_atoms(a)
nl = native.neighbor_list(p, cutoff, avgn=avgn)

i, j, dr, abs_dr = nl.get_neighbors(p, vec=True)
pavg, pvar = native.pair_distribution(i, abs_dr, nbins, cutoff)
r = np.linspace(0.0, cutoff, nbins+1)
r = (r[1:]+r[:-1])/2

rho = len(a)/a.get_volume()
np.savetxt('g2.out', np.transpose([r, pavg, pvar, pavg/rho]))

rho = np.sum(a.get_masses())/a.get_volume()
print 'Density is {0} g/cm^3.'.format(rho * 1e24/mol)
