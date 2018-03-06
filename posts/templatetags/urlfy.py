from urllib.parse import urlparse
from django import template

register = template.Library()

@register.filter
def urlfy(value):
    return urlparse(value)