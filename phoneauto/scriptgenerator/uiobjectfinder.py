# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import math
import sys


class UiObjectFinder(object):

    _FIND_OBJECT_DISTANCE_THRESH = 200

    def __init__(self, device):
        self._device = device
        self._hierarchy_dump = None

    def set_hierarchy_dump(self, hierarchy_dump):
        self._hierarchy_dump = hierarchy_dump

    def find_object_contains(self, coord, ignore_distant, **criteria):
        objects = self._find_objects_contains(
            coord, ignore_distant, **criteria)
        smallest = self._select_smallest_object(objects)
        if smallest is None:
            return None
        locator = self._determine_locator(smallest['info'])
        retval = {'object': smallest['object']}
        if locator is None:
            retval.update({'locator': criteria, 'index': smallest['index']})
        else:
            retval.update({'locator': locator})
        return retval

    def _find_objects_contains(self, coord, ignore_distant, **criteria):
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
            info = obj.info
            if xy_in_rect(info['visibleBounds']):
                yield (i, obj, info)

    @staticmethod
    def _select_smallest_object(object_enum):
        def rect_area(r):
            """Returns area of rect r"""
            return (r['bottom'] - r['top']) * (r['right'] - r['left'])

        min_obj = (sys.maxsize, )
        for i, obj, info in object_enum:
            area = rect_area(info['visibleBounds'])
            if area < min_obj[0]:
                min_obj = (area, i, obj, info)
        if len(min_obj) == 1:
            return None
        return {'index': min_obj[1], 'object': min_obj[2], 'info': min_obj[3]}

    def _find_objects(self, **criteria):
        if self._hierarchy_dump is None:
            return self._device(**criteria)
        return self._hierarchy_dump.find_objects(**criteria)

    def _determine_locator(self, info):
        """Determines locator and creates UI element object"""

        def unique(**criteria):
            objects = self._find_objects(**criteria)
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
