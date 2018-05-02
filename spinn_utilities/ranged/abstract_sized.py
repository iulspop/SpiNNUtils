# pylint: disable=redefined-builtin
import itertools
import logging
import numpy
import sys
from six import integer_types

logger = logging.getLogger(__file__)


class AbstractSized(object):
    """ Base class for slice and ID checking against size.
    """

    __slots__ = [
        "_size"]

    def __init__(self, size):
        """ Constructor for a ranged list.

        :param size: Fixed length of the list
        """
        self._size = max(int(round(size)), 0)

    def __len__(self):
        """ Size of the list, irrespective of actual values

        :return: the initial and Fixed size of the list
        """
        return self._size

    @staticmethod
    def _is_id_type(id):  # @ReservedAssignment
        """ Check if the given ID has a type acceptable for IDs. """
        return isinstance(id, integer_types)

    def _check_id_in_range(self, id):  # @ReservedAssignment
        if id < 0:
            if self._is_id_type(id):
                raise IndexError(
                    "The index {} is out of range.".format(id))
            # pragma: no cover
            raise TypeError("Invalid argument type {}.".format(type(id)))
        if id >= self._size:
            if self._is_id_type(id):
                raise IndexError(
                    "The index {0} is out of range.".format(id))
            raise TypeError("Invalid argument type {}.".format(type(id)))

    def _check_slice_in_range(self, slice_start, slice_stop):
        if slice_start is None:
            slice_start = 0
        elif slice_start < 0:
            slice_start = self._size + slice_start
            if slice_start < 0:
                if self._is_id_type(slice_start):
                    logger.warn(
                        "Specified slice start was {} while size is only {}. "
                        "Therefore slice will start at index 0".format(
                            slice_start - self._size, self._size))
                    slice_start = 0
                else:
                    raise TypeError("Invalid argument type {}.".format(
                        type(slice_start)))
        elif slice_start >= len(self):
            logger.warn(
                "Specified slice start was {} while size is only {}. "
                "Therefore slice will be empty".format(
                    slice_start - self._size, self._size))
            return (self._size, self._size)

        if slice_stop is None or slice_stop == sys.maxsize:
            slice_stop = self._size
        elif slice_stop < 0:
            slice_stop = self._size + slice_stop

        if slice_start > slice_stop:
            if not self._is_id_type(slice_start):
                raise TypeError("Invalid argument type {}.".format(
                    type(slice_start)))
            if not self._is_id_type(slice_stop):
                raise TypeError("Invalid argument type {}.".format(
                    type(slice_start)))
            logger.warn(
                "Specified slice has a start {} greater than its stop {} "
                "(based on size {}). Therefore slice will be empty".format(
                    slice_start, slice_stop, self._size))
            return (self._size, self._size)
        if slice_stop > len(self):
            if not self._is_id_type(slice_stop):
                raise TypeError("Invalid argument type {}.".format(
                    type(slice_start)))
            logger.warn(
                "Specified slice has a start {} equal to its stop {} "
                "(based on size {}). Therefore slice will be empty".format(
                    slice_start, slice_stop, self._size))
        if slice_stop < 0:
            logger.warn(
                "Specified slice stop was {} while size is only {}. "
                "Therefore slice will be empty".format(
                    slice_stop-self._size, self._size))
            return (self._size, self._size)
        elif slice_start > slice_stop:
            logger.warn(
                "Specified slice has a start {} greater than its stop {} "
                "(based on size {}). Therefore slice will be empty".format(
                    slice_start, slice_stop, self._size))
            return (self._size, self._size)
        elif slice_start == slice_stop:
            logger.warn(
                "Specified slice has a start {} equal to its stop {} "
                "(based on size {}). Therefore slice will be empty".format(
                    slice_start, slice_stop, self._size))
        elif slice_stop > len(self):
            logger.warn(
                "Specified slice stop was {} while size is only {}. "
                "Therefore slice will be truncated".format(
                    slice_stop, self._size))
            slice_stop = self._size
        return slice_start, slice_stop

    def _check_mask_size(self, selector):
        if len(selector) < self._size:
            logger.warning(
                "The boolean mask is too short. The expected length was {} "
                "but the length was only {}. All the missing entries will be "
                "treated as False!".format(self._size, len(selector)))
        elif len(selector) > self._size:
            logger.warning(
                "The boolean mask is too long. The expected length was {} "
                "but the length was only {}. All the missing entries will be "
                "ignored!".format(self._size, len(selector)))

    def selector_to_ids(self, selector, warn=False):
        """ Gets the list of ids covered by this selector

        The types of selector currently supported are:

        None: returns all ids

        slice: Standard python slice. \
            negative values and values larger than size are handled using
            slices's indices method. \
            This could result in am empty list

        int: (or long) Handles negative values as normal.
            Check id is within expected range. \

        iterator of bools: Used a mask. \
            If the length of the mask is longer or shorted than number of ids \
            the result is the shorter of the two, \
            with the remainer of the longer ignored.

        iterator of int (long) but not bool: \
            Every value checked that it is with the range 0 to size. \
            Negative values NOT allowed. \
            Original order and duplication is respected so result may be
            unordered and contain duplicates.

        :param selector: Some object that identifies a range of ids.

        :return: a (possibly sorted) list of ids
        """
        # Check selector is an iterable using pythonic try
        try:
            iterator = iter(selector)
        except TypeError:
            iterator = None

        if iterator is not None:
            # bool is superclass of int so if any are bools all must be
            if any(isinstance(item, (bool, numpy.bool_)) for item in selector):
                if all(isinstance(item, (bool, numpy.bool_))
                       for item in selector):
                    if warn:
                        self._check_mask_size(selector)
                    return list(itertools.compress(
                        range(self._size), selector))
                raise TypeError(
                    "An iterable type must be all ints or all bools")
            elif all(isinstance(item, (integer_types, numpy.integer))
                     for item in selector):
                # list converts any specific numpy types
                ids = list(selector)
                for id in ids:
                    if id < 0:
                        raise TypeError(
                            "Selector includes the id {} which is less than "
                            "zero".format(id))
                    if id >= self._size:
                        raise TypeError(
                            "Selector includes the id {} which not less than "
                            "the size {}".format(id, self._size))
                return ids
            else:
                raise TypeError(
                    "An iterable type must be all ints or all bools")

        # OK lets try for None, int and slice after all
        if selector is None:
            if warn:
                logger.warning("None selector taken as all ids")
            return range(self._size)

        if isinstance(selector, slice):
            (slice_start, slice_stop, step) = selector.indices(self._size)
            return range(slice_start, slice_stop, step)

        if isinstance(selector, integer_types):
            if selector < 0:
                selector = self._size + selector
            if selector < 0 or selector >= self._size:
                raise TypeError("Selector {} is unsupproted for size {} "
                                "".format(selector-self._size, self._size))
            return [selector]

        raise TypeError("Unexpected selector type {}".format(type(selector)))
