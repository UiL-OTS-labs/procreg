from django import template
import logging

register = template.Library()

class ProgressEnumerator:

    def __init__(self):
        self.counter = {
            "new_reg": 1,
            "faculty": 2,
            "involved_people": 3,
        }

    def __call__(self, slug):
        return str(self.counter[slug])

@register.inclusion_tag(
    "registrations/templatetags/progress_bar.html",
)
def progress_bar(blueprint, current):
    enumerator = ProgressEnumerator()
    tag_context = {
        "involved": [],
        "current_slug": current.slug,
        "current_question": current,
        "blueprint": blueprint,
        "enumerator": enumerator,
        "group_one": ["new_reg", "faculty"]
    }
    return tag_context


@register.inclusion_tag(
    "registrations/templatetags/progress_item_question.html",
    takes_context=True,
)
def progress_item_from_question(context, question, size="largest",
                                text=None, url=True, number=True):
    if question in ["", None]:
        return None
    # Caller can set url to False or None to disable
    if url is True:
        url = question.get_edit_url()
    if not text:
        text = question.title

    size = "stepper-bubble-" + size
    span_classes = ["stepper-bubble", size]
    item_classes = []
    current = context.get("current_question")
    if question.slug == current.slug:
        item_classes.append("active")

    if number is True:
        enumerator = context.get("enumerator")
        number = enumerator(question.slug)

    tag_context = {
        "title": text,
        "span_classes": " ".join(span_classes),
        "item_classes": " ".join(item_classes),
        "number": number,
        "link": url,
    }
    return tag_context


@register.inclusion_tag(
    "registrations/templatetags/progress_item_question.html",
    takes_context=True,
)
def progress_item_from_slug(context, slug, **kwargs):
    blueprint = context.get("blueprint")
    question_kwargs = kwargs.get("question_kwargs", {})
    question = blueprint.get_question(
        slug=slug,
        **question_kwargs,
    )
    return progress_item_from_question(context, question, **kwargs)