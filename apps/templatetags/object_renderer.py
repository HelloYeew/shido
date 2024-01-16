from django import template
from django.urls import reverse

from apps.models import Instance

register = template.Library()


@register.filter
def render_instance(instance_id):
    instance = Instance.objects.get(id=instance_id)
    link_to_instance = reverse('apps_instance_detail', args=[instance.id])
    return f'<a href="{link_to_instance}">{instance.name}</a>'


@register.filter
def render_instance_list(instance_list):
    html = ''
    # instance_list example : 1,2,3
    for instance in [Instance.objects.get(id=instance_id) for instance_id in instance_list.split(',')]:
        link_to_instance = reverse('apps_instance_detail', args=[instance.id])
        html += f'<a href="{link_to_instance}">{instance.name}</a>, '
    return html[:-2]
