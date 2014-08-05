from django.template import Library

register = Library()


@register.filter(is_safe=True)
def get_title(value):
    value = value.title()
    return value.replace('_', ' ')
