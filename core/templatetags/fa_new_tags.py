from django import template
from django.utils.html import conditional_escape, format_html, mark_safe

register = template.Library()


@register.filter
def split_lines(value):
    """Split a text field on newlines and return non-empty stripped lines."""
    if not value:
        return []
    return [line.strip() for line in value.splitlines() if line.strip()]


@register.simple_tag
def hero_headline(headline, highlight_word):
    """Render a hero headline, wrapping highlight_word in a gold <span>.

    Usage:
        {% hero_headline slide.headline slide.headline_highlight %}
    """
    if not headline:
        return ''
    safe_headline = conditional_escape(headline)
    if highlight_word and highlight_word in safe_headline:
        safe_highlight = conditional_escape(highlight_word)
        wrapped = format_html(
            '<span style="color:#efd99a">{}</span>',
            highlight_word,
        )
        rendered = safe_headline.replace(safe_highlight, wrapped, 1)
        return mark_safe(rendered)
    return mark_safe(safe_headline)
