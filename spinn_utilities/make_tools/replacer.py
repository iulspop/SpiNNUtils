# Copyright (c) 2018 The University of Manchester
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

import logging
import six
import struct
from spinn_utilities.log import FormatAdapter
from .file_converter import FORMAT_EXP
from .file_converter import TOKEN
from .log_sqllite_database import LogSqlLiteDatabase

logger = FormatAdapter(logging.getLogger(__name__))


class Replacer(LogSqlLiteDatabase):

    def __enter__(self):
       return self

    def __exit__(self, type, value, traceback):
        # nothing yet
        pass

    def replace(self, short):
        parts = short.split(TOKEN)
        if not parts[0].isdigit():
            return short
        data = self.get_log_info(parts[0])
        if data is None:
            return short
        (preface, original) = data
        replaced = six.b(original).decode("unicode_escape")
        if len(parts) > 1:
            matches = FORMAT_EXP.findall(original)
            # Remove any blanks due to double spacing
            matches = [x for x in matches if x != ""]
            # Start at 0 so first i+1 puts you at 1 as part 0 is the short
            i = 0
            try:
                for match in matches:
                    i += 1
                    if match.endswith("f"):
                        replacement = str(self.hex_to_float(parts[i]))
                    elif match.endswith("F"):
                        replacement = str(self.hexes_to_double(
                            parts[i], parts[i+1]))
                        i += 1
                    else:
                        replacement = parts[i]
                    replaced = replaced.replace(match, replacement, 1)
            except Exception:  # pylint: disable=broad-except
                return short

        return preface + replaced

    @staticmethod
    def hex_to_float(hex_str):
        return struct.unpack('!f', struct.pack("!I", int(hex_str, 16)))[0]

    @staticmethod
    def hexes_to_double(upper, lower):
        return struct.unpack(
            '!d',
            struct.pack("!I", int(upper, 16)) +
            struct.pack("!I", int(lower, 16)))[0]
