import pytest

from hipeac.tools.twitter import Tweeter


LONG_TEXT = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam placerat, leo eget interdum tincidunt, enim eros
    malesuada lorem, nec tincidunt purus odio eget mi. Maecenas accumsan et turpis at hendrerit. Nunc molestie lacinia
    tellus, eu venenatis erat euismod sit amet. In hac habitasse platea dictumst. Vestibulum ac interdum dolor.
"""


@pytest.mark.parametrize('link,text,cleaned_text', [
    (
        None,
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit'
    ),
    (
        'https://short.url',
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit https://short.url'
    ),
    (
        None,
        LONG_TEXT,
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam placerat, leo eget interdum tincidunt, '
        'enim eros malesuada lorem, nec tin...'
    ),
    (
        'https://short.url',
        LONG_TEXT,
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam placerat, leo eget interdum tincidunt, '
        'enim eros malesu... https://short.url'
    ),
    (
        None,
        '   Lorem ipsum dolor sit amet, consectetur   adipiscing  elit',
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit'
    ),
])
def test_clean_status(link, text, cleaned_text):
    assert cleaned_text == Tweeter.clean_status(text, link)
