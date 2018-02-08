from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def avatar_color(value	):
	# Returns a color to be used as avatar background
	colors = ["e53935","D81B60","8E24AA","5E35B1","3949AB","1E88E5","039BE5","00ACC1","00897B","43A047","7CB342","C0CA33","FDD835","FFB300","FB8C00","F4511E","6D4C41","757575","546E7A"]
	first_letter = value[0]
	color = colors[ord(first_letter)%len(colors)]
	return "#"+color

