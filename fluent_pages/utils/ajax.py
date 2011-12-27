"""
Generic Ajax functionality
"""

from django.http import HttpResponse
from django.utils import simplejson
from django.core.serializers import serialize
from django.db.models.query import QuerySet


def to_json(object):
    """
    Convert a data structure to JSON.
    If the data is a QuerySet, Django's serialize() will be used.
    """
    if isinstance(object, QuerySet):
        return serialize('json', object)
    else:
        return simplejson.dumps(object)


class JsonResponse(HttpResponse):
    """
    A convenient HttpResponse class, which encodes the response in JSON format.
    """
    def __init__(self, jsondata):
        self.jsondata = jsondata
        jsonstr = to_json(jsondata)
        super(JsonResponse, self).__init__(jsonstr, content_type='application/javascript')
