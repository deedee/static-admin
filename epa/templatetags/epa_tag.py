from django import template

register = template.Library()

@register.filter
def is_list(val):
    return isinstance(val, list)