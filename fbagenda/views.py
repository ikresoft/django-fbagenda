import urllib2
import django.utils.simplejson as json
from django.shortcuts import render_to_response
from django.template import RequestContext, defaultfilters
from django.core.cache import cache
from pytz import timezone
import dateutil.parser

from django.conf import settings

graph_url = 'https://graph.facebook.com'
access_token = 'access_token=%s|%s' % (settings.FB_APP_ID, settings.FB_APP_SECRET)
events_url = '%s/%s/events?limit=10000&%s' % (graph_url, settings.FB_PAGE_ID, access_token)
cache_expires = getattr(settings, 'CACHE_EXPIRES', 30)


def get_graph_result(url, object_hook=None):
    cachename = 'fbgallery_cache_' + defaultfilters.slugify(url)
    data = None
    if cache_expires > 0:
        data = cache.get(cachename)
    if data is None:
        f = urllib2.urlopen(urllib2.Request(url))
        response = f.read()
        f.close()
        data = json.loads(response, object_hook=object_hook)
        if cache_expires > 0:
            cache.set(cachename, data, cache_expires*60)
    return data


class Event(object):

    def __init__(self, name='', start_time='', location='', timezone='', id=''):
        self.name = name
        self._start_time = start_time
        self.location = location
        self._timezone = timezone
        self.id = id

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, value):
        self._timezone = value

    @property
    def start_time(self):
        tz = timezone(settings.TIME_ZONE)
        if self.timezone != '':
            tz = timezone(self.timezone)
        try:
            return dateutil.parser.parse(self._start_time).astimezone(tz)
        except:
            return dateutil.parser.parse(self._start_time)

    @start_time.setter
    def start_time(self, value):
        self._start_time = value


def object_decoder(dct):
    event = Event()
    if 'name' in dct:
        event.name = dct['name']

    if 'start_time' in dct:
        event.start_time = dct['start_time']

    if 'location' in dct:
        event.location = dct['location']

    if 'timezone' in dct:
        event.timezone = dct['timezone']

    if 'id' in dct:
        event.id = dct['id']
    return event


def get_events():
    events_temp = get_graph_result(events_url)["data"]
    events = []
    for temp_event in events_temp:
        event = object_decoder(temp_event)
        events.append(event)
    return events


def display_events(request):
    events = get_graph_result(events_url)["data"]

    data = RequestContext(request, {
        'events': events,
    })

    return render_to_response('fbagenda/events.html', context_instance=data)
