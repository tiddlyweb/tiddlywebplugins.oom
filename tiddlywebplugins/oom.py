"""
This is a TiddlyWeb plugin which extends the TiddlyWeb filter syntax 
to add 'oom' (One Of Many) which matches if the named attribute is any
of those named in the provided list. It is similar to
tiddlywebplugins.mselect but only matches the named attribute against
many values, not many possible attributes.

This will return all tiddlers with tag blog or published (or both) and
then sort by modified:

    oom=tag:blog,published;sort=-modified

Install by adding 'tiddlywebplugins.oom' to 'system_plugins'
in tiddlywebconfig.py.
"""

from itertools import ifilter

from tiddlyweb.filters import FILTER_PARSERS
from tiddlyweb.store import get_entity


OOM_SEPARATOR = ','

test_oom = None


def init(config):
    """
    Install the filter.
    """

    global test_oom

    def select_if_one(attribute, value, entities, environ=None):
        if environ == None:
            environ = {}

        store = environ.get('tiddlyweb.store', None)

        if environ:
            try:
                separator = environ['tiddlyweb.config']['oom.separator']
            except (TypeError, KeyError):
                separator = OOM_SEPARATOR
        else:
            separator = config.get('oom.separator', OOM_SEPARATOR)

        values = value.split(separator)

        def get_value_in_values(entity):
            entity = get_entity(entity, store)
            try:
                return getattr(entity, attribute) in values
            except AttributeError:
                try:
                    return entity.fields[attribute] in values
                except (AttributeError, KeyError):
                    return False

        return ifilter(get_value_in_values, entities)

    def oom_parse(command):
        attribute, args = command.split(':', 1)

        def selector(entities, indexable=False, environ=None):
            return select_if_one(attribute, args, entities, environ=environ)

        return selector

    FILTER_PARSERS['oom'] = oom_parse

    test_oom = select_if_one
