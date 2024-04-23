from django import template
from django.http import QueryDict

register = template.Library()

@register.simple_tag(takes_context=True)
def concat_get_params(context, **kwargs):
    """Generates get params to stick after a URL, so that ? and &
    get put in the right places. It requires """
    if "current_get_params" in context:
        all_params = context["current_get_params"].copy()
    else:
        all_params = QueryDict()
    all_params.update(kwargs)
    args = [k + "=" + str(v) for k, v in all_params.items()]
    out = "?" + "&".join(args)
    return out
