from django import template

register = template.Library()

@register.inclusion_tag("registrations/templatetags/render_faq.html")
def render_faq(faq):
    context = {
        "faq": faq,
    }
    return context
