from django import template
import logging

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

@register.inclusion_tag("registrations/templatetags/progress_bar.html",
                        takes_context=True)
def progress_bar(context):

    tag_context = copy_context(
        context,
        [
            "blueprint",
            "question",
            "current",
            "view",
        ]
    )
    current = context.get("current", None)
    question = context.get("question", None)
    blueprint = context.get("blueprint")
    if not current:
        if question:
            current = question.slug
            tag_context.update({"current": current})
    tag_context["progress"] = blueprint.progress_bar
    tag_context["items"] = blueprint.progress_bar.items
        
    return tag_context


def copy_context(context, keys, default=None):
    
    out = {}
        
    for k in keys:
        out[k] = context.get(k, default)

    return out
        
