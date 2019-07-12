# Copyright (c) 2017-2018 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from spinn_utilities.overrides import overrides
from .abstract_grandparent import AbstractGrandParent
from .abstract_has_constraints import AbstractHasConstraints


class UncheckedBadParam(AbstractGrandParent):
    def label(self):
        return "GRANDPARENT"

    def set_label(selfself, not_label):
        pass

    @overrides(AbstractHasConstraints.add_constraint)
    def add_constraint(self, constraint):
        raise Exception("We set our own constrainst")

    @overrides(AbstractHasConstraints.constraints)
    def constraints(self):
        return ["No night feeds", "No nappy changes"]
