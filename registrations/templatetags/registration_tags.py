from django import template
import logging

register = template.Library()

@register.inclusion_tag("registrations/h2_and_buttons.html")
def h2_and_buttons(title, *args):
    return {}

@register.inclusion_tag("registrations/templatetags/display_question_small.html")
def display_question_small(question, title=None):
    """Display question in small form for overview pages."""

    tag_context = {
        'question': question,
        'title': title,
        'segments': question.get_segments(),
    }

    return tag_context


@register.inclusion_tag("registrations/templatetags/display_question_header.html")
def display_question_header(question):
    """Display a question's header and description without
    fields"""

    tag_context = {
        'question': question,
    }

    return tag_context


@register.inclusion_tag("registrations/templatetags/display_loq.html")
def display_loq(question):
    """This displays the current instances of a question
    that functions as a CreateView for submodels. It should
    have get_create_url() and get_delete_url() defined."""
    tag_context = {
        'source_question': question,
        "editing": True,
    }
    return tag_context


def copy_context(context, keys, default=None):

    out = {}
    for k in keys:
        out[k] = context.get(k, default)
    return out
