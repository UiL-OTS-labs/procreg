from django import template

register = template.Library()

@register.inclusion_tag("registrations/h2_and_buttons.html")
def h2_and_buttons(title, *args):
    return {}

@register.inclusion_tag("registrations/templatetags/display_question_small.html")
def display_question_small(question, title=None):
    """Display question in small form for overview pages."""


    tag_context = {'question': question,
                   'title': title,
                   'segments': question.segments,
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

@register.inclusion_tag("registrations/templatetags/progress_bar.html")
def progress_bar(blueprint):

    return {blueprint: blueprint}
