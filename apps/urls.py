from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='apps_home'),
    path('class/', class_list, name='apps_class_list'),
    path('class/<int:class_id>/', class_detail, name='apps_class_detail'),
    path('class/<int:class_id>/edit/', class_edit, name='apps_class_edit'),
    path('class/create/', class_create, name='apps_class_create'),
    path('instance/', instance_list, name='apps_instance_list'),
    path('instance/<int:instance_id>/', instance_detail, name='apps_instance_detail'),
    path('instance/<int:instance_id>/raw', instance_detail_raw, name='apps_instance_detail_raw'),
    path('instance/<int:instance_id>/wiki', instance_detail_wiki, name='apps_instance_detail_wiki'),
    path('instance/<int:instance_id>/edit/', instance_edit, name='apps_instance_edit'),
    path('instance/<int:instance_id>/property/', instance_property_list, name='apps_instance_property_list'),
    path('instance/<int:instance_id>/property/<int:property_type_id>/', instance_property_form, name='apps_instance_property_form'),
    path('instance/<int:instance_id>/property/<int:property_type_id>/delete', instance_property_delete, name='apps_instance_property_delete'),
    path('instance/<int:instance_id>/create_wiki_property/', instance_create_wiki_property, name='apps_instance_create_wiki_property'),
    path('instance/create/', instance_create, name='apps_instance_create'),
    path('property_type/', property_type_list, name='apps_property_type_list'),
    path('property_type/create/', property_type_create, name='apps_property_type_create'),
    path('property_type/<int:property_type_id>/', property_type_detail, name='apps_property_type_detail')
]