from __future__ import unicode_literals, absolute_import

from django import template


register = template.Library()


@register.filter(is_safe=True)
def get_title(value):
    value = value.title()
    return value.replace('_', ' ')


@register.tag
def get_metrics_list(parser, token):
    bits = list(token.split_contents())
    if len(bits) == 4 and bits[2] == "as":
        varname = bits[-1]
        metric_type = bits[1]
    else:
        raise template.TemplateSyntaxError("{} expected format is 'metric_type as varname'".format(bits[0]))
    if metric_type == 'domain_per_tag':
        metric_list = (
            ('console_domain_net_rx_per_tag', 'Network RX'),
            ('console_domain_net_tx_per_tag', 'Network TX'),
            ('console_domain_hits_per_tag', 'Hits')
        )
    elif metric_type == 'container_per_tag':
        metric_list = (
            ('console_container_io_read_per_tag', 'IO Read'),
            ('console_container_io_write_per_tag', 'IO Write'),
            ('console_container_net_rx_per_tag', 'Network RX'),
            ('console_container_net_tx_per_tag', 'Network TX'),
            ('console_container_cpu_per_tag', 'CPU Ticks'),
            ('console_container_mem_per_tag', 'Memory'),
            ('console_container_quota_per_tag', 'Quota')
        )
    elif metric_type == 'domain':
        metric_list = (
            ('console_domain_net_rx', 'Network RX'),
            ('console_domain_net_tx', 'Network TX'),
            ('console_domain_hits', 'Hits')
        )
    elif metric_type == 'container':
        metric_list = (
            ('console_container_io_read', 'IO Read'),
            ('console_container_io_write', 'IO Write'),
            ('console_container_net_rx', 'Network RX'),
            ('console_container_net_tx', 'Network TX'),
            ('console_container_cpu', 'CPU Ticks'),
            ('console_container_mem', 'Memory'),
            ('console_container_quota', 'Quota')
        )
    else:
        raise template.TemplateSyntaxError(
            "Expected metric types are domain_per_tag, container_per_tag, domain or container_per_tag, got {}".format(metric_type))

    return MakeListNode(metric_list, varname)


class MakeListNode(template.Node):
    def __init__(self, items, varname):
        self.items = items
        self.varname = varname

    def render(self, context):
        context[self.varname] = self.items
        return ''
