# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import xml.etree.ElementTree as ET


def _equals(search_str, attr_str):
    return search_str == attr_str

def _contains(search_str, attr_str):
    return search_str in attr_str

def _startswith(search_str, attr_str):
    return attr_str.startswith(search_str)

def _matches(search_str, attr_str):
    return bool(re.search(search_str, attr_str))


_ATTRIBUTE_CONV_MAPPING = {
    'text': ('text', _equals),
    'textContains': ('text', _contains),
    'textMatches': ('text', _matches),
    'textStartsWith': ('text', _startswith),
    'className': ('class', _equals),
    'classNameMatches': ('class', _matches),
    'description': ('content-desc', _equals),
    'descriptionContains': ('content-desc', _contains),
    'descriptionMatches': ('content-desc', _matches),
    'descriptionStartsWith': ('content-desc', _startswith),
    'checkable': ('checkable', _equals),
    'checked': ('checked', _equals),
    'clickable': ('clickable', _equals),
    'longClickable': ('long-clickable', _equals),
    'scrollable': ('scrollable', _equals),
    'enabled': ('enabled', _equals),
    'focusable': ('focusable', _equals),
    'focused': ('focused', _equals),
    'selected': ('selected', _equals),
    'packageName': ('package', _equals),
    'packageNameMatches': ('package', _matches),
    'resourceId': ('resource-id', _equals),
    'resourceIdMatches': ('resource-id', _matches),
    'index': ('index', _equals)
}


class ViewHierarchyDump(object):

    def __init__(self, device_info, dump):
        self._device_info = device_info
        self._root = ET.fromstring(dump)

    @staticmethod
    def _get_boolean_attrs(node_attrs, out_attrs):
        bool_attrs = ('checked', 'scrollable', 'selected', 'enabled',
                      'focused', 'focusable', 'clickable', 'checkable',
                      ('longClickable', 'long-clickable'))
        for attr in bool_attrs:
            to_attr = from_attr = attr
            if type(attr) == tuple:
                to_attr = attr[0]
                from_attr = attr[1]
            attr_value = node_attrs.get(from_attr)
            out_attrs[to_attr] = attr_value == 'true'

    @staticmethod
    def _get_string_attrs(node_attrs, out_attrs):
        string_attrs = (('contentDescription', 'content-desc'),
                        ('text', 'text'), ('packageName', 'package'),
                        ('className', 'class'),
                        ('resourceName', 'resource-id'))
        for attr in string_attrs:
            out_attrs[attr[0]] = node_attrs.get(attr[1], '')

    @staticmethod
    def _get_bounds_attr(node_attrs, out_attrs):
        bounds_str = node_attrs.get('bounds', '')
        dig = r'[+-]?\d+'
        pat = r'\[({dig}),({dig})\]\[({dig}),({dig})\]'.format(dig=dig)
        m = re.match(pat, bounds_str)
        if not m or len(m.groups()) != 4:
            raise ValueError('Dump result contained invalid bounds value')
        bounds = dict(zip(
            ('left', 'top', 'right', 'bottom'),
            (int(v) for v in m.groups())))
        out_attrs['bounds'] = bounds

    @staticmethod
    def _get_visible_bounds_attr(device_info, bounds):

        def truncate(pos, axis):
            key = 'displayWidth' if axis == 'x' else 'displayHeight'
            return max(0, min(pos, device_info[key]))
        return {
            'left': truncate(bounds['left'], 'x'),
            'top': truncate(bounds['top'], 'y'),
            'right': truncate(bounds['right'], 'x'),
            'bottom': truncate(bounds['bottom'], 'y')
        }

    def _get_attrs(self, node):
        out_attrs = {}
        self._get_boolean_attrs(node, out_attrs)
        self._get_string_attrs(node, out_attrs)
        self._get_bounds_attr(node, out_attrs)
        visible_bounds = self._get_visible_bounds_attr(
            self._device_info, out_attrs['bounds'])
        out_attrs['visibleBounds'] = visible_bounds
        out_attrs['childCount'] = len(node)
        return out_attrs

    @staticmethod
    def _get_matchers(criteria):

        class _Matcher(object):

            def __init__(self, key, func, lhs_value):
                self.key = key
                self._func = func
                self._lhs_value = lhs_value

            def __call__(self, rhs_value):
                return self._func(self._lhs_value, rhs_value)

        def value_to_str(value):
            if isinstance(value, type('')):
                return value
            if isinstance(value, bool):
                return str(value).lower()
            else:
                return str(value)

        matchers = []
        for name, value in criteria.items():
            attr_conv = _ATTRIBUTE_CONV_MAPPING.get(name)
            if attr_conv is None:
                raise NotImplementedError(
                    'Search by {0} has not implemented yet'.format(name))
            lhs_value = value_to_str(value)
            matchers.append(_Matcher(attr_conv[0], attr_conv[1], lhs_value))
        return matchers

    def find_objects(self, **criteria):

        matchers = self._get_matchers(criteria)

        found = []
        for node in self._root.iter('node'):
            match = True
            for matcher in matchers:
                rhs_value = node.get(matcher.key, '')
                if not matcher(rhs_value):
                    match = False
                    break
            if match:
                found.append(self._get_attrs(node))

        return found
