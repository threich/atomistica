# ======================================================================
# Atomistica - Interatomic potential library and molecular dynamics code
# https://github.com/Atomistica/atomistica
#
# Copyright (2005-2015) Lars Pastewka <lars.pastewka@kit.edu> and others
# See the AUTHORS file in the top-level Atomistica directory.
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

"""
Tools related to homogenously deformed volumes.
"""

import numpy as np

###

def get_shear_distance(a):
    """
    Returns the distance a volume has moved during simple shear. Considers
    either Lees-Edwards boundary conditions or sheared cells.
    """
    cx, cy, cz = a.cell
    if 'shear_dx' in a.info:
        assert abs(cx[1]) < 1e-12, 'cx[1] = {0}'.format(cx[1])
        assert abs(cx[2]) < 1e-12, 'cx[2] = {0}'.format(cx[2])
        assert abs(cy[0]) < 1e-12, 'cx[0] = {0}'.format(cy[0])
        assert abs(cy[2]) < 1e-12, 'cy[2] = {0}'.format(cy[2])
        assert abs(cz[0]) < 1e-12, 'cz[0] = {0}'.format(cz[0])
        assert abs(cz[1]) < 1e-12, 'cz[1] = {0}'.format(cz[1])
        dx, dy, dz = a.info['shear_dx']
    else:
        assert abs(cx[1]) < 1e-12, 'cx[1] = {0}'.format(cx[1])
        assert abs(cx[2]) < 1e-12, 'cx[2] = {0}'.format(cx[2])
        assert abs(cy[0]) < 1e-12, 'cy[0] = {0}'.format(cy[0])
        assert abs(cy[2]) < 1e-12, 'cy[2] = {0}'.format(cy[2])
        dx, dy, sz = cz
    return dx, dy

###

class RemoveSimpleShearDeformation:
    """
    Remove a homogeneous cell deformation given an (iterable) trajectory
    object. This will take proper care of cells that are instantaneously
    flipped from +0.5 strain to -0.5 strain during simple shear, as e.g.
    generated by LAMMPS.
    """

    def __init__(self, traj):
        self.traj = traj

        self.last_d = [ ]

        self.sheared_cells = [ ]
        self.unsheared_cells = [ ]


    def _fill_cell_info_upto(self, i):
        # Iterate up to frame i the full trajectory first and generate a list
        # of cell vectors.
        if i < len(self.last_d):
            return

        # Iterate up to frame i the full trajectory first and generate a list
        # of cell vectors.
        if len(self.last_d) == 0:
            i0 = 0
            last_dx, last_dy = get_shear_distance(self.traj[0])
            dx = last_dx
            dy = last_dy
        else:
            i0 = len(self.last_d)
            last_dx, last_dy = self.last_d[i0-1]
            dx, dy, dummy = self.sheared_cells[i0-1][2]

        for a in self.traj[i0:i+1]:
            sx, sy, sz = a.cell.diagonal()
            cur_dx, cur_dy = get_shear_distance(a)
            while cur_dx-last_dx < -sx/2:
                cur_dx += sx
            dx += cur_dx-last_dx
            while cur_dy-last_dy < -sy/2:
                cur_dy += sy
            dy += cur_dy-last_dy

            # Store last shear distance
            last_dx = cur_dx
            last_dy = cur_dy

            # Store cells and shear distance
            self.last_d += [ ( last_dx, last_dy ) ]

            self.sheared_cells += [ np.array([[sx,0,0],[0,sy,0],[dx,dy,sz]]) ]
            self.unsheared_cells += [ np.array([sx,sy,sz]) ]


    def __getitem__(self, i=-1):
        if i < 0:
            i = len(self) + i
            if i < 0 or i >= len(self):
                raise IndexError('Trajectory index out of range.')

        self._fill_cell_info_upto(i)

        a = self.traj[i]

        # Set true cell shape
        a.set_cell(self.sheared_cells[i], scale_atoms=False)
        # Unshear
        a.set_cell(self.unsheared_cells[i], scale_atoms=True)

        # Wrap to cell
        a.set_scaled_positions(a.get_scaled_positions()%1.0)

        a.info['true_cell'] = self.sheared_cells[i]

        return a


    def __len__(self):
        return len(self.traj)
