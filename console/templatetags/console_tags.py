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
    if metric_type == u'domain_per_tag':
        metric_list = (
            (u'domain_net_rx_per_tag', u'Network RX'),
            (u'domain_net_tx_per_tag', u'Network TX'),
            (u'domain_hits_per_tag', u'Hits')
        )
    elif metric_type == u'container_per_tag':
        metric_list = (
            (u'container_io_read_per_tag', u'IO Read'),
            (u'container_io_write_per_tag', u'IO Write'),
            (u'container_net_rx_per_tag', u'Network RX'),
            (u'container_net_tx_per_tag', u'Network TX'),
            (u'container_cpu_per_tag', u'CPU Ticks'),
            (u'container_mem_per_tag', u'Memory'),
            (u'container_quota_per_tag', u'Quota')
        )
    elif metric_type == u'domain':
        metric_list = (
            (u'domain_net_rx', u'Network RX'),
            (u'domain_net_tx', u'Network TX'),
            (u'domain_hits', u'Hits')
        )
    elif metric_type == u'container':
        metric_list = (
            (u'container_io_read', u'IO Read'),
            (u'container_io_write', u'IO Write'),
            (u'container_net_rx', u'Network RX'),
            (u'container_net_tx', u'Network TX'),
            (u'container_cpu', u'CPU Ticks'),
            (u'container_mem', u'Memory'),
            (u'container_quota', u'Quota')
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
        return ""
