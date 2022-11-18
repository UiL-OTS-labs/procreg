from django import template
import logging

register = template.Library()


class ProgressEnumerator:

    def __init__(self):
        self.counter = {
            None: 1,
        }

    def count(self, slug):
        num = self.counter[slug]
        self.counter[slug] = num + 1
        return num

    def __call__(self, slug):
        if slug in self.counter.keys():
            return str(self.count(slug))
        else:
            return self.count(None)

@register.inclusion_tag(
    "registrations/templatetags/progress_bar.html",
)
def progress_bar(blueprint, current):
    enumerator = ProgressEnumerator()
    tag_context = {
        "involved": [],
        "blueprint": blueprint,
        "enumerator": enumerator,
        "group_one": ["new_reg", "faculty"]
    }
    if hasattr(current, "slug"):
        tag_context['current_slug'] = current.slug
        tag_context['current_question'] = current
    else:
        tag_context['current_slug'] = current
        tag_context['current_question'] = blueprint.get_question(slug=current)
    return tag_context


@register.inclusion_tag(
    "registrations/templatetags/progress_item_question.html",
    takes_context=True,
)
def progress_item_from_question(context, question, size="largest",
                                text=None, url=True, number=True,
                                incomplete=False,):
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
    if question.disabled:
        item_classes.append("disabled")
    else:
        if incomplete or question.incomplete:
            item_classes.append("incomplete")
        else:
            if question.complete:
                item_classes.append("complete")

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
    from ..forms import PlaceholderQuestion
    blueprint = context.get("blueprint")
    question_kwargs = kwargs.get("question_kwargs", {})
    question = blueprint.get_question(
        slug=slug,
        **question_kwargs,
    )
    if not question:
        question = PlaceholderQuestion(slug=slug)
    return progress_item_from_question(context, question, **kwargs)
