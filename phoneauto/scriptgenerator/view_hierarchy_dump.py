# -*- coding: utf-8 -*-
"""Manages hirearchy dump of views

:copyright: (c) 2015 by tksn
:license: MIT
"""

from __future__ import unicode_literals
import re
import xml.etree.ElementTree as ET


def _equals(search_str, attr_str):
    """Equals-operator which is used to find a view"""
    return search_str == attr_str


def _contains(search_str, attr_str):
    """Contains-operator which is used to find a view"""
    return search_str in attr_str


def _startswith(search_str, attr_str):
    """Startswith-operator which is used to find a view"""
    return attr_str.startswith(search_str)


def _matches(search_str, attr_str):
    """Matches-operator which is used to find a view"""
    return bool(re.search(search_str, attr_str))


# Query argument to (attribute, operator) mapping
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
    """Dump of view hierarchy"""

    def __init__(self, device_info, dump):
        """Initialization

        Args:
            device_info (dict): dictionary obtained by uiautomator.Device.info
            dump (string): dump string obtained by uiautomator.Device.dump()
        """
        self._device_info = device_info
        self._root = ET.fromstring(dump)

    @staticmethod
    def _get_boolean_attrs(node_attrs, out_attrs):
        """Attribute format conversion for boolean attributes

        Converts the format of boolean type attributes
        extracted from a view dump,
        to the same format as uiautomator.DeviceUiObject.info,
        and inserts the converted attribute to the dictionary argument
        out_attrs.

        Args:
            node_attrs (dict):
                view attributes extracted from a dump
            out_attrs (dict):
                view attributes which includes converted
                boolean conforms to the same format
                as uiautomator.DeviceUiObject.info.
        """
        bool_attrs = ('checked', 'scrollable', 'selected', 'enabled',
                      'focused', 'focusable', 'clickable', 'checkable',
                      ('longClickable', 'long-clickable'))
        for attr in bool_attrs:
            to_attr = from_attr = attr
            if isinstance(attr, tuple):
                to_attr = attr[0]
                from_attr = attr[1]
            attr_value = node_attrs.get(from_attr)
            out_attrs[to_attr] = attr_value == 'true'

    @staticmethod
    def _get_string_attrs(node_attrs, out_attrs):
        """Attribute format conversion for string attributes
        Almost same as the _get_boolean_attrs, but for string attributes.
        """
        string_attrs = (('contentDescription', 'content-desc'),
                        ('text', 'text'), ('packageName', 'package'),
                        ('className', 'class'),
                        ('resourceName', 'resource-id'))
        for attr in string_attrs:
            out_attrs[attr[0]] = node_attrs.get(attr[1], '')

    @staticmethod
    def _get_bounds_attr(node_attrs, out_attrs):
        """Attribute format conversion for bounds attribute
        Has the same objective as the _get_boolean_attrs,
        but specifically for bounds attribute.
        """
        bounds_str = node_attrs.get('bounds', '')
        dig = r'[+-]?\d+'
        pat = r'\[({dig}),({dig})\]\[({dig}),({dig})\]'.format(dig=dig)
        match_result = re.match(pat, bounds_str)
        if not match_result or len(match_result.groups()) != 4:
            raise ValueError('Dump result contained invalid bounds value')
        bounds = dict(zip(
            ('left', 'top', 'right', 'bottom'),
            (int(v) for v in match_result.groups())))
        out_attrs['bounds'] = bounds

    @staticmethod
    def _get_visible_bounds_attr(device_info, bounds):
        """Attribute format conversion for visibleBounds attribute
        Has the same objective as the _get_boolean_attrs,
        but specifically for visibleBounds attribute.
        """

        def truncate(pos, axis):
            """Truncates bounds to assure its not out of screen"""
            key = 'displayWidth' if axis == 'x' else 'displayHeight'
            return max(0, min(pos, device_info[key]))
        return {
            'left': truncate(bounds['left'], 'x'),
            'top': truncate(bounds['top'], 'y'),
            'right': truncate(bounds['right'], 'x'),
            'bottom': truncate(bounds['bottom'], 'y')
        }

    def _get_attrs(self, node):
        """Extracts attribute values from node and returns them as the same
        format as automator.Device"""

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
        """Returns matcher object to find objects which meets criteria """

        class _Matcher(object):
            """Matcher class holds a comparator function and
            left hand side value"""

            def __init__(self, key, func, lhs_value):
                """Initialization"""
                self.key = key
                self._func = func
                self._lhs_value = lhs_value

            def __call__(self, rhs_value):
                """compare lhs and rhs"""
                return self._func(self._lhs_value, rhs_value)

        def value_to_str(value):
            """value to string conversion used
            in order to stringify lhs value"""
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
        """Find objects which meet criteria

        Args:
            criteria (dict):
                keyword arguments which is to specify search criteria
                such as clickable=True, text="abc", etc.
        Returns:
            list: list of attributes of found objects
        """

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
