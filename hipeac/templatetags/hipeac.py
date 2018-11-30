import json

from commonmark import commonmark as marked
from django import template
from django.template.base import Node
from django.utils.safestring import mark_safe
from urllib.parse import quote_plus

from hipeac.functions import truncate_md
from hipeac.models import get_cached_metadata


register = template.Library()


@register.simple_tag
def active(request, patterns):
    if patterns:
        for pattern in patterns.split(','):
            try:
                if pattern == request.resolver_match.url_name:
                    return 'active'
            except Exception:
                return ''
    return ''


@register.filter
def euro(value):
    # http://publications.europa.eu/code/en/en-370303.htm
    return mark_safe('<span class="nowrap">EUR %s</span>' % str('{0:,}'.format(value).replace(',', ' ')))


@register.filter
def join_json(json_string, separator=','):
    return mark_safe(separator.join(json.loads(json_string)))


@register.filter
def markdown(text):
    return mark_safe(marked(text))


@register.tag(name='markdown')
def do_markdown(parser, token):
    nodelist = parser.parse(('endmarkdown',))
    parser.delete_first_token()
    bits = token.split_contents()
    if len(bits) > 1:
        raise template.TemplateSyntaxError('`markdown` tag requires exactly zero arguments')
    return MarkdownNode(nodelist)


class MarkdownNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        text = self.nodelist.render(context)
        return mark_safe(marked(text))


def metadata_output(ids, title, *, output_format: str = '<li><small>{0}</small></li>', maps=[str]):
    keys = [int(key) for key in ids.split(',')]
    metadata_items = get_cached_metadata()

    output = []
    output.append(f'<div class="mb-4"><h5 class="display-sm">{title}</h5><p>')
    for metadata in [metadata_items[key] for key in keys if key in metadata_items]:
        output.append(output_format.format(*[m(metadata.value) for m in maps]))
    output.append('</p></div>')

    return mark_safe(''.join(output))


@register.filter
def metadata_list(ids, title):
    if not ids:
        return ''
    return metadata_output(ids, title)


@register.filter
def metadata_list_jobs(ids, title):
    if not ids:
        return ''
    return metadata_output(
        ids,
        title,
        output_format='<small><a href="/jobs/#/?q={0}" class="inherit">{1}</a></small><br>',
        maps=[quote_plus, str]
    )


@register.filter
def metadata_badges(ids, title):
    if not ids:
        return ''
    return metadata_output(ids, title, output_format='<span class="badge badge-primary mr-1">{0}</span>')


@register.filter
def metadata_badges_jobs(ids, title):
    if not ids:
        return ''
    return metadata_output(
        ids,
        title,
        output_format='<a href="/jobs/#/?q={0}" class="inherit"><span class="badge badge-primary mr-1">{1}</span></a>',
        maps=[quote_plus, str]
    )


@register.filter
def truncate(text, limit=300, smart=True):
    if not text:
        return ''

    text = truncate_md(text, limit=limit)

    if smart:
        words = text.split(' ')[:-1]
        return ' '.join(words) + '...'
    else:
        return text + '...'


class SpacelessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return json.dumps(json.loads(self.nodelist.render(context).strip()))


@register.tag
def spaceless_json(parser, token):
    nodelist = parser.parse(('endspaceless_json',))
    parser.delete_first_token()
    return SpacelessNode(nodelist)
