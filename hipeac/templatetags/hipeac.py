import json
import lxml.html

from django import template
from django.template.base import Node
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from markdown import markdown as marked

from hipeac.models import get_cached_metadata


register = template.Library()


@register.simple_tag
def active(request, patterns):
    if patterns:
        for pattern in patterns.split(','):
            try:
                if pattern == request.resolver_match.url_name:
                    return 'active'
            except Exception as e:
                return ''
    return ''


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


@register.filter
def metadata_list(ids, title):
    if not ids:
        return ''

    keys = [int(key) for key in ids.split(',')]
    metadata = get_cached_metadata()

    output = []
    output.append(f'<div class="mb-4"><h5 class="display-sm">{title}</h5><ul class="list-unstyled">')
    for m in [metadata[key] for key in keys if key in metadata]:
        output.append(f'<li><small>{m.value}</small></li>')
    output.append('</ul></div>')
    return mark_safe(''.join(output))


@register.filter
def metadata_badges(ids, title):
    if not ids:
        return ''

    keys = [int(key) for key in ids.split(',')]
    metadata = get_cached_metadata()

    output = []
    output.append(f'<div class="mb-4"><h5 class="display-sm">{title}</h5>')
    for m in [metadata[key] for key in keys if key in metadata]:
        output.append(f'<span class="badge badge-primary mr-1">{m.value}</span>')
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
