#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Google DFP Utils
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Third Party Library Imports
from suds.sudsobject import asdict


def _underscore_key(string):
    """
    Replace periods with underscores

    @return string, str
    @return key, str
    """
    return string.replace('.', '_')


def to_string(item, convert_bool=True):
    """
    Handles unicode strings with non-ascii characters
    """
    str_val = unicode(item).encode('utf-8', 'replace')

    if convert_bool:
        if str_val == u'True' or str_val == u'true':
            return True
        elif str_val == u'False' or str_val == u'false':
            return False

    return str_val


def recursive_asdict(obj):
    """
    Convert Suds object into a dict so it can be serialized.
    Taken (mostly) from: http://stackoverflow.com/a/15678861

    @param obj, sudsobject: the suds object to be converted to dict
    @return dict: the object converted to a dict
    """
    # Don't convert a dict
    if isinstance(obj, dict):
        return obj

    out = {}
    for key, val in asdict(obj).iteritems():
        if hasattr(val, '__keylist__'):
            out[_underscore_key(key)] = recursive_asdict(val)
        elif isinstance(val, list):
            out[_underscore_key(key)] = []
            for item in val:
                if hasattr(item, '__keylist__'):
                    out[_underscore_key(key)].append(recursive_asdict(item))
                else:
                    out[_underscore_key(key)].append(to_string(item))
        else:
            out[_underscore_key(key)] = to_string(val)
    return out


def format_pql_response(raw_list):
    """
    Convert a list of lists to where the first
    row is a list of column names, to a list
    of dictionaries with keys associated to each
    column name and values the associated values.

    @param raw_list: list
    @return: list(dict)
    """
    column_keys = raw_list.pop(0)
    data_list = []
    for result in raw_list:
        data = {}
        for col_name, val in zip(column_keys, result):
            # NOTE: DFP returns numbers as integers. We refer to integers
            # as strings throughout the app and therefore want to be
            # consistent here.
            data[col_name] = str(val)
        data_list.append(data)
    return data_list


def format_report_list(raw_list):
    """
    Convert a list of lists to where the first
    row is a list of column names, to a list
    of dictionaries with keys associated to each
    column name and values the associated values.

    @param raw_list: list
    @return: list(dict)
    """
    column_keys = raw_list.pop(0)
    data_list = []
    for result in raw_list:
        data = {}
        for col_name, val in zip(column_keys, result):
            # NOTE: DFP returns numbers as integers. We refer to integers
            # as strings throughout the app and therefore want to be
            # consistent here.
            val = val.encode('utf-8')
            data[col_name] = str(val)
        data_list.append(data)
    return data_list


def sanitize_report_response(response):
    """
    The dfp report api returns reponses with
    types pre-pended to column names. This function
    deletes these to make for a cleaner response.

    @param response: dict
    @return: dict
    """
    clean_response = {}
    for _key, _val in response.items():
        clean_key = _key.split('Dimension.')[-1]
        clean_key = clean_key.split('Column.')[-1]
        clean_response[clean_key] = _val

    return clean_response
