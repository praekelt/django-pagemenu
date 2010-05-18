from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.tag
def pagemenu(parser, token):
    """
    Output pagemenu.
    """
    try:
        tag_name, pagemenu = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('pagemenu tag requires 1 argument (pagemenu), %s given' % (len(token.split_contents()) - 1))
    return PageMenuNode(pagemenu)

class PageMenuNode(template.Node):
    def __init__(self, pagemenu):
        self.pagemenu = template.Variable(pagemenu)
    
    def render(self, context):
        pagemenu = self.pagemenu.resolve(context)
        context = {
            'request': context['request'],
            'pagemenu': pagemenu,
        }
        return render_to_string('pagemenu/inclusion_tags/pagemenu.html', context)
