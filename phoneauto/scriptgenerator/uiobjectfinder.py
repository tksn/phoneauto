# -*- coding: utf-8 -*-
"""UiObject finder

:copyright: (c) 2015 by tksn
:license: MIT
"""

from __future__ import unicode_literals
import math
import sys
from phoneauto.scriptgenerator.exception import UiObjectNotFound


class UiObjectLocator(object):
    """Locator for locating a UI object on the screen"""

    def __init__(self, filters, index=None):
        """Initialize locator object

        Args:
            filters (dict): Key-value pairs which are used as filter conditions
                to filter out UI Objects.
            index (int): Index in a list which is yielded by applying
                filters. It is used to identify the UI object.
                When filters are enough to filter out UI objects to one single
                object, index is not used and can be None.
        """
        self._filters = filters
        self._index = index
        self._meta = None

    def set_meta(self, meta):
        """Set meta information"""
        self._meta = meta

    @property
    def meta(self):
        """Meta information aquired on search"""
        return self._meta

    @property
    def filters(self):
        """Filter conditions which is used to identify a UI object"""
        return self._filters

    @property
    def index(self):
        """Index in filter results, which is used to identify a UI object"""
        return self._index


class UiObjectFinder(object):
    """Finder to spot a UI object for provided conditions"""

    _FIND_OBJECT_DISTANCE_THRESH = 200

    def __init__(self, hierarchy_dump):
        """Initialize finder object

        Args:
            hierarchy_dump (object): UI hierarchy dump object
        """
        self._hierarchy_dump = hierarchy_dump

    def find_object_contains(self, coord, ignore_distant, **criteria):
        """Find an object of which rect contains given coordinates
        and meeds given criteria.

        Args:
            coord (tuple): Coordinates (x, y)
            ignore_distant (bool):
                Boolean flag which specifies whether it ignores
                UI objects of which center are too far from coord.
            criteria (dict):
                Optional key-value pairs which filter search result
        Returns:
            locator object
        Raiseafes:
          eafe  UiObjectNotFound: If there is no such object corresponds to
         f       given coordinates and criteria.
        """
        # Find all objects which contain (x, y)
        objects_iter = self._find_objects_contains(
            coord, ignore_distant, **criteria)
        # Pick an object which has smallest area
        smallest = self._select_smallest_object(objects_iter)
        if smallest is None:
            raise UiObjectNotFound('({0}, {1})'.format(*coord))
        # Try finding filters which can uniquely identify an object
        locator = self._determine_locator(smallest['object'])
        # If failed, Use index in addition to filters
        locator = locator or UiObjectLocator(
            filters=criteria, index=smallest['index'])
        locator.set_meta(smallest['object'])
        return locator

    def _find_objects_contains(self, coord, ignore_distant, **criteria):
        """Find UI object of which rect contains coord"""
        # pylint: disable=invalid-name

        T, L, B, R = 'top', 'left', 'bottom', 'right'
        x, y = coord

        def xy_in_rect(r):
            """Check xy is in rect r"""
            if x < r[L] or r[R] <= x or y < r[T] or r[B] <= y:
                return False
            if ignore_distant:
                r_x, r_y = r[L] + (r[R] - r[L]) / 2, r[T] + (r[B] - r[T]) / 2
                distance = math.hypot(x - r_x, y - r_y)
                return distance < self._FIND_OBJECT_DISTANCE_THRESH
            return True

        objects = self._hierarchy_dump.find_objects(**criteria)
        for i, obj in enumerate(objects):
            if xy_in_rect(obj['visibleBounds']):
                yield (i, obj)

    @staticmethod
    def _select_smallest_object(object_enum):
        """Select the smallest UI object from a set of UI objects"""

        def rect_area(rect):
            """Returns area of rect"""
            return ((rect['bottom'] - rect['top']) *
                    (rect['right'] - rect['left']))

        min_obj = sentinel = (sys.maxsize, )
        for i, obj in object_enum:
            area = rect_area(obj['visibleBounds'])
            if area < min_obj[0]:
                min_obj = (area, i, obj)
        if min_obj is sentinel:
            return None
        return {'index': min_obj[1], 'object': min_obj[2]}

    def _determine_locator(self, info):
        """Determine locator which identifies one single UI object"""

        def unique(**criteria):
            """Check if given criteria finds single UI object"""
            objects = list(self._hierarchy_dump.find_objects(**criteria))
            return len(objects) == 1

        # uses resource_id if it's available and unique
        resource_id = info['resourceName']
        if resource_id and unique(resourceId=resource_id):
            return UiObjectLocator(filters={'resourceId': resource_id})

        # uses content-desc if it's available
        content_desc = info['contentDescription']
        if content_desc and unique(description=content_desc):
            return UiObjectLocator(filters={'description': content_desc})

        # uses text if it's available
        if info['text'] and unique(text=info['text']):
            return UiObjectLocator(filters={'text': info['text']})

        # uses text if it's available
        class_name = info['className']
        if class_name and unique(className=class_name):
            return UiObjectLocator(filters={'className': class_name})

        return None
