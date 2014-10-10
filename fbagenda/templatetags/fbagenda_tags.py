from django import template
from fbagenda.views import get_events

register = template.Library()


@register.inclusion_tag('fbagenda/templatetags/latest_events.html')
def latest_events():
    events = get_events()
    return {'events': events}
