import json
import operator
import lxml.html

from django import template
from django.template.base import Node
from django.utils.safestring import mark_safe
from markdown import markdown as marked

from hipeac.api.serializers import MetadataListField


register = template.Library()


@register.simple_tag
def active(request, patterns):
    for pattern in patterns.split(','):
        if pattern == request.path or ('+' in pattern and request.path.startswith(pattern[:-1])):
            return 'active'
        if pattern.startswith('/conference/') and request.path.split('/')[1].isnumeric():
            return 'active'
    return ''


@register.filter
def join_json(json_string, separator=','):
    return mark_safe(separator.join(json.loads(json_string)))


def convert_metadata(ids):
    metadata = MetadataListField().to_representation(ids)
    metadata.sort(key=operator.itemgetter('value'))
    return metadata


@register.filter
def markdown(text):
    return mark_safe(marked(text))


@register.filter
def metadata_list(ids, title):
    if not ids:
        return ''

    output = []
    output.append('<div class="mb-4"><h5 class="display-sm">{0}</h5><ul class="list-unstyled">'.format(title))
    for m in convert_metadata(ids):
        output.append('<li><small>{0}</small></li>'.format(m['value']))
    output.append('</ul></div>')
    return mark_safe(''.join(output))


@register.filter
def metadata_badges(ids, title):
    if not ids:
        return ''

    output = []
    output.append('<div class="mb-4"><h5 class="display-sm">{0}</h5>'.format(title))
    for m in convert_metadata(ids):
        output.append('<span class="badge badge-primary mr-1">{0}</span>'.format(m['value']))
    output.append('</div>')
    return mark_safe(''.join(output))


@register.filter
def truncate(text, limit=300, smart=True):
    if not text:
        return ''

    html = marked(text)
    text = ''.join(lxml.html.fromstring(html).xpath('//p')[0].text_content())
    text = ' '.join(text.split())

    if len(text) <= limit:
        return text

    limit = limit - 3
    text = text[:limit]

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
