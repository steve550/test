from django import template
import pytz
import datetime

register = template.Library()

@register.filter(name='to_ist')
def to_ist(value):
    inist = value.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Asia/Kolkata"))
    return inist.strftime("%Y-%m-%d %H:%M:%S %z %Z")

@register.filter(name='duration')
def duration(value):
    if not value.start_time or not value.end_time:
        return ""
    delta = value.end_time - value.start_time
    seconds = int(delta.total_seconds())
    return '{:}:{:02}:{:02}'.format(seconds // 3600, seconds % 3600 // 60, seconds % 60)

@register.filter(name='format_timedelta')
def format_timedelta(delta):
    seconds = int(delta.total_seconds())
    return '{:}:{:02}:{:02}'.format(seconds // 3600, seconds % 3600 // 60, seconds % 60)
