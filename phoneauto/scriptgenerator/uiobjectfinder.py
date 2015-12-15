# -*- coding: utf-8 -*-
"""UiObject finder

:copyright: (c) 2015 by tksn
:license: MIT
"""

from __future__ import unicode_literals
import math
import sys


class UiObjectNotFound(Exception):
    """UiObject Not Found Exception"""

    def __init__(self, message):
        """Initialization"""
        super(UiObjectNotFound, self).__init__()
        self.message = message

    def __str__(self):
        """String representation"""
        return 'UiObjectNotFound: ' + self.message


class UiObjectFinder(object):
    """UiObject finder class"""

    _FIND_OBJECT_DISTANCE_THRESH = 200

    def __init__(self, device):
        """Initialization

        Args:
            device (object): uiautomator.Device object
        """
        self._device = device
        self._hierarchy_dump = None

    def set_hierarchy_dump(self, hierarchy_dump):
        """Sets hierarchy dump string to this object

        Args:
            hierarchy_dump (string):
                dump string obtained using uiautomator.Device.dump()
        """
        self._hierarchy_dump = hierarchy_dump

    def find_object_contains(self, coord, ignore_distant, **criteria):
        """Finds an object which rect contains given coordinates

        Args:
            coord (tuple): coordinates
            ignore_distant (boolean):
                boolean flag which specifies whether it ignores
                uiobjects which center are too far from coord.
            criteria (dict):
                optional key-value pairs which filter search result
        Returns:
            dict:
                dictionary which contains found UiObject and locator to find it
        """
        objects = self._find_objects_contains(
            coord, ignore_distant, **criteria)
        smallest = self._select_smallest_object(objects)
        if smallest is None:
            raise UiObjectNotFound('({0}, {1})'.format(*coord))

        index = None
        locator = self._determine_locator(smallest['object']['info'])
        if locator is None:
            locator = criteria
            index = smallest['index']
        inst = smallest['object'].get('instance')
        if inst is None:
            inst = self._device(**locator)[0 if index is None else index]
        retval = {'object': inst, 'locator': locator}
        if index is not None:
            retval.update({'index': index})
        return retval

    def _find_objects_contains(self, coord, ignore_distant, **criteria):
        """Finds UiObject which rect contains coord"""
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

        objects = self._find_objects(**criteria)
        for i, obj in enumerate(objects):
            if xy_in_rect(obj['info']['visibleBounds']):
                yield (i, obj)

    @staticmethod
    def _select_smallest_object(object_enum):
        """Selects the smallest UiObject from sets of UiObject"""

        def rect_area(rect):
            """Returns area of rect r"""
            return ((rect['bottom'] - rect['top']) *
                    (rect['right'] - rect['left']))

        min_obj = (sys.maxsize, )
        for i, obj in object_enum:
            area = rect_area(obj['info']['visibleBounds'])
            if area < min_obj[0]:
                min_obj = (area, i, obj)
        if len(min_obj) == 1:
            return None
        return {'index': min_obj[1], 'object': min_obj[2]}

    def _find_objects(self, **criteria):
        """Finds objects which conforms to given criteria"""
        if self._hierarchy_dump is None:
            for obj in self._device(**criteria):
                yield {'instance': obj, 'info': obj.info}
        else:
            infos = self._hierarchy_dump.find_objects(**criteria)
            for info in infos:
                yield {'info': info}

    def _determine_locator(self, info):
        """Determines locator and creates UI element object"""

        def unique(**criteria):
            """checks if given criteria finds single UiObject"""
            objects = list(self._find_objects(**criteria))
            if len(objects) == 1:
                return True
            return False

        # uses resource_id if it's available and unique
        resource_id = info['resourceName']
        if resource_id and unique(resourceId=resource_id):
            return {'resourceId': resource_id}

        # uses content-desc if it's available
        content_desc = info['contentDescription']
        if content_desc and unique(description=content_desc):
            return {'description': content_desc}

        # uses text if it's available
        if info['text'] and unique(text=info['text']):
            return {'text': info['text']}

        # uses text if it's available
        class_name = info['className']
        if class_name and unique(className=class_name):
            return {'className': class_name}

        return None
