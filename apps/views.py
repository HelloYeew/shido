from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect

from apps.forms import ClassForm, InstanceForm, PropertyTypeForm, \
    ObjectPropertyStringForm, ObjectPropertyNumberForm, ObjectPropertyFloatForm, ObjectPropertyBooleanForm, \
    ObjectPropertyDateForm, ObjectPropertyDateTimeForm, ObjectPropertyMarkdownForm, ObjectPropertyImageForm, \
    ObjectPropertyFileForm, ObjectPropertyInstanceForm, ObjectPropertyInstanceListForm, ObjectPropertyJSONForm, \
    ObjectPropertyClassForm, ObjectPropertyURLForm
from apps.models import Class, Instance, PropertyType, ObjectPropertyRelation
from apps.templatetags.json_to_list import json_to_list
from enums import WIKI_PROPERTY_TYPE_LIST


def home(request):
    # random the ObjectPropertyRelation property_type__name='wikiContent'
    try:
        wiki_instance = ObjectPropertyRelation.objects.filter(property_type__name='wikiContent').order_by('?').first().instance_object
        wiki_ready = True
        wiki_content = wiki_instance.have_wiki()
    except Exception as e:
        wiki_ready = False
        wiki_content = None
        wiki_instance = None
    return render(request, 'apps/home.html', {
        'wiki_ready': wiki_ready,
        'wiki_detail': wiki_content,
        'wiki_instance': wiki_instance,
        'total_class': Class.objects.count(),
        'total_instance': Instance.objects.count()
    })


def class_list(request):
    return render(request, 'apps/class/list.html', {
        'all_class': Class.objects.all()
    })


@login_required()
@user_passes_test(lambda u: u.is_staff)
def class_create(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Class created successfully!')
            return redirect('apps_class_list')
    else:
        form = ClassForm()
    return render(request, 'apps/class/create.html', {
        'form': form
    })


def class_detail(request, class_id):
    if not Class.objects.filter(id=class_id).exists():
        messages.error(request, f'Class with id {class_id} does not exist')
        return redirect('apps_class_list')
    return render(request, 'apps/class/detail.html', {
        'class': Class.objects.get(id=class_id),
        'instance_list': Instance.objects.filter(class_instance=Class.objects.get(id=class_id)),
        'property_type_list': PropertyType.objects.filter(class_instance=Class.objects.get(id=class_id))
    })


@login_required()
@user_passes_test(lambda u: u.is_staff)
def class_edit(request, class_id):
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=Class.objects.get(id=class_id))
        if form.is_valid():
            form.save()
            messages.success(request, f'Class edited successfully!')
            return redirect('apps_class_detail', class_id=class_id)
    else:
        form = ClassForm(instance=Class.objects.get(id=class_id))
    return render(request, 'apps/class/edit.html', {
        'form': form,
        'class': Class.objects.get(id=class_id)
    })


def instance_list(request):
    return render(request, 'apps/instances/list.html', {
        'all_instances': Instance.objects.all(),
        'all_classes': Class.objects.all()
    })


@login_required()
@user_passes_test(lambda u: u.is_staff)
def instance_create(request):
    if request.method == 'POST':
        form = InstanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Instance created successfully!')
            return redirect('apps_instance_list')
    else:
        form = InstanceForm()
    return render(request, 'apps/instances/create.html', {
        'form': form
    })


def instance_detail(request, instance_id):
    return redirect('apps_instance_detail_wiki', instance_id=instance_id)


def instance_detail_wiki(request, instance_id):
    if not Instance.objects.filter(id=instance_id).exists():
        messages.error(request, f'Instance with id {instance_id} does not exist')
        return redirect('apps_instance_list')
    have_wiki_property = True
    for wiki_property_name in WIKI_PROPERTY_TYPE_LIST:
        if not PropertyType.objects.filter(class_instance=Instance.objects.get(id=instance_id).class_instance, name=wiki_property_name).exists():
            have_wiki_property = False
            break
    wiki_detail = {}
    try:
        wiki_detail['title'] = ObjectPropertyRelation.objects.get(instance_object_id=instance_id, property_type__name='wikiTitle').raw_value
    except ObjectPropertyRelation.DoesNotExist:
        wiki_detail['title'] = None
    try:
        wiki_detail['content'] = ObjectPropertyRelation.objects.get(instance_object_id=instance_id, property_type__name='wikiContent').raw_value
    except ObjectPropertyRelation.DoesNotExist:
        wiki_detail['content'] = None
    try:
        wiki_detail['image'] = ObjectPropertyRelation.objects.get(instance_object_id=instance_id, property_type__name='wikiImage').raw_value
    except ObjectPropertyRelation.DoesNotExist:
        wiki_detail['image'] = None
    return render(request, 'apps/instances/detail_wiki.html', {
        'top_menu_active': 'wiki',
        'instance': Instance.objects.get(id=instance_id),
        'object_property': ObjectPropertyRelation.objects.filter(instance_object_id=instance_id),
        'have_wiki_property': have_wiki_property,
        'wiki_detail': wiki_detail
    })


def instance_detail_raw(request, instance_id):
    if not Instance.objects.filter(id=instance_id).exists():
        messages.error(request, f'Instance with id {instance_id} does not exist')
        return redirect('apps_instance_list')
    return render(request, 'apps/instances/detail_raw.html', {
        'top_menu_active': 'raw',
        'instance': Instance.objects.get(id=instance_id),
        'object_property': ObjectPropertyRelation.objects.filter(instance_object_id=instance_id)
    })


@login_required()
@user_passes_test(lambda u: u.is_staff)
def instance_edit(request, instance_id):
    if request.method == 'POST':
        form = InstanceForm(request.POST, instance=Instance.objects.get(id=instance_id))
        if form.is_valid():
            form.save()
            for object_property in ObjectPropertyRelation.objects.filter(instance_object=Instance.objects.get(id=instance_id)):
                exist_property_type = PropertyType.objects.filter(class_instance=object_property.instance_object.class_instance, name=object_property.property_type.name, raw_type=object_property.property_type.raw_type)
                if exist_property_type.exists():
                    object_property.property_type = exist_property_type.first()
                    object_property.save()
                else:
                    object_property.delete()
            messages.success(request, f'Instance edited successfully!')
            return redirect('apps_instance_detail', instance_id=instance_id)
    else:
        form = InstanceForm(instance=Instance.objects.get(id=instance_id))
    return render(request, 'apps/instances/edit.html', {
        'form': form,
        'instance': Instance.objects.get(id=instance_id)
    })


@login_required()
@user_passes_test(lambda u: u.is_staff)
def instance_property_list(request, instance_id):
    try:
        instance = Instance.objects.get(id=instance_id)
    except Instance.DoesNotExist:
        messages.error(request, f'Instance with id {instance_id} does not exist')
        return redirect('apps_instance_list')
    property_list = []
    for property_type in PropertyType.objects.filter(class_instance=instance.class_instance):
        property_list.append({
            'property_type': property_type,
            'exist': ObjectPropertyRelation.objects.filter(instance_object=instance, property_type=property_type).exists(),
            'id': ObjectPropertyRelation.objects.get(instance_object=instance, property_type=property_type).id if ObjectPropertyRelation.objects.filter(instance_object=instance, property_type=property_type).exists() else None
        })
    return render(request, 'apps/instances/property_list.html', {
        'instance': instance,
        'all_property_types': property_list
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def instance_property_form(request, instance_id, property_type_id):
    try:
        instance = Instance.objects.get(id=instance_id)
    except Instance.DoesNotExist:
        messages.error(request, f'Instance with id {instance_id} does not exist')
        return redirect('apps_instance_list')
    try:
        property_type = PropertyType.objects.get(id=property_type_id)
    except PropertyType.DoesNotExist:
        messages.error(request, f'Property type with id {property_type_id} does not exist')
        return redirect('apps_instance_list')
    # find old property
    if ObjectPropertyRelation.objects.filter(instance_object=instance, property_type=property_type).exists():
        old_property = ObjectPropertyRelation.objects.get(instance_object=instance, property_type=property_type)
    else:
        old_property = None
    if request.method == 'POST':
        if property_type.raw_type == 'string':
            form = ObjectPropertyStringForm(request.POST, max_length=property_type.limitation['max_length'], min_length=property_type.limitation['min_length'], initial_value='')
        elif property_type.raw_type == 'number':
            form = ObjectPropertyNumberForm(request.POST, min_value=property_type.limitation['min_value'], max_value=property_type.limitation['max_value'], initial_value=property_type.limitation['min_value'])
        elif property_type.raw_type == 'float':
            form = ObjectPropertyFloatForm(request.POST, min_value=property_type.limitation['min_value'], max_value=property_type.limitation['max_value'], decimal_places=property_type.limitation['decimal_places'], initial_value=property_type.limitation['min_value'])
        elif property_type.raw_type == 'boolean':
            form = ObjectPropertyBooleanForm(request.POST, initial_value=False)
        elif property_type.raw_type == 'date':
            form = ObjectPropertyDateForm(request.POST, initial_value='2020-01-01')
        elif property_type.raw_type == 'datetime':
            form = ObjectPropertyDateTimeForm(request.POST, initial_value='2020-01-01 00:00:00')
        elif property_type.raw_type == 'markdown':
            form = ObjectPropertyMarkdownForm(request.POST, request.FILES, initial_value='')
        elif property_type.raw_type == 'image':
            form = ObjectPropertyImageForm(request.POST, request.FILES, initial_value='')
        elif property_type.raw_type == 'file':
            form = ObjectPropertyFileForm(request.POST, request.FILES, initial_value='')
        elif property_type.raw_type == 'instance':
            form = ObjectPropertyInstanceForm(request.POST, class_id=property_type.limitation['class_id'], initial_value=Instance.objects.filter(class_instance_id=property_type.limitation['class_id']).first())
        elif property_type.raw_type == 'instance_list':
            form = ObjectPropertyInstanceListForm(request.POST, class_id_list=property_type.limitation['allow_class_id_list'], initial_value=[])
        elif property_type.raw_type == 'json':
            try:
                initial_json = property_type.limitation['initial_json']
            except KeyError:
                initial_json = {}
            form = ObjectPropertyJSONForm(request.POST, initial_value=initial_json)
        elif property_type.raw_type == 'class':
            form = ObjectPropertyClassForm(request.POST, initial_value=Class.objects.all().first())
        elif property_type.raw_type == 'url':
            form = ObjectPropertyURLForm(request.POST, initial_value='')
        else:
            messages.error(request, f'Raw type {property_type.raw_type} is not supported for adding property')
            return redirect('apps_instance_detail', instance_id=instance_id)
        if form.is_valid():
            if property_type.raw_type == 'image' or property_type.raw_type == 'file':
                # save file to media
                file = form.cleaned_data['value']
                file_name = default_storage.save(f'apps/{property_type.raw_type}/{file.name}', file)
                # get path to file, not full path, only path from media
                file_path = default_storage.url(file_name)
                raw_value = file_path
            elif property_type.raw_type == 'instance_list':
                # get list of instance id with comma separated
                raw_value = ','.join([str(instance.id) for instance in form.cleaned_data['value']])
            elif property_type.raw_type == 'instance':
                raw_value = str(form.cleaned_data['value'].id)
            elif property_type.raw_type == 'class':
                raw_value = str(form.cleaned_data['value'].id)
            else:
                raw_value = form.cleaned_data['value']
            if ObjectPropertyRelation.objects.filter(instance_object=instance, property_type=property_type).exists():
                old_property.raw_value = raw_value
                old_property.save()
            else:
                ObjectPropertyRelation.objects.create(
                    instance_object=instance,
                    property_type=property_type,
                    raw_value=raw_value
                )
            if old_property:
                messages.success(request, f'Property updated successfully!')
            else:
                messages.success(request, f'Property added successfully!')
            return redirect('apps_instance_detail_raw', instance_id=instance_id)
    else:
        if property_type.raw_type == 'string':
            form = ObjectPropertyStringForm(max_length=property_type.limitation['max_length'], min_length=property_type.limitation['min_length'], initial_value=old_property.raw_value if old_property else '')
        elif property_type.raw_type == 'number':
            form = ObjectPropertyNumberForm(min_value=property_type.limitation['min_value'], max_value=property_type.limitation['max_value'], initial_value=old_property.raw_value if old_property else property_type.limitation['min_value'])
        elif property_type.raw_type == 'float':
            form = ObjectPropertyFloatForm(min_value=property_type.limitation['min_value'], max_value=property_type.limitation['max_value'], decimal_places=property_type.limitation['decimal_places'], initial_value=old_property.raw_value if old_property else property_type.limitation['min_value'])
        elif property_type.raw_type == 'boolean':
            form = ObjectPropertyBooleanForm(initial_value=bool(old_property.raw_value) if old_property else False)
        elif property_type.raw_type == 'date':
            form = ObjectPropertyDateForm(initial_value=old_property.raw_value if old_property else '2020-01-01')
        elif property_type.raw_type == 'datetime':
            form = ObjectPropertyDateTimeForm(initial_value=old_property.raw_value if old_property else '2020-01-01 00:00:00')
        elif property_type.raw_type == 'markdown':
            form = ObjectPropertyMarkdownForm(initial_value=old_property.raw_value if old_property else '')
        elif property_type.raw_type == 'image':
            form = ObjectPropertyImageForm(initial_value=old_property.raw_value if old_property else '')
        elif property_type.raw_type == 'file':
            form = ObjectPropertyFileForm(initial_value=old_property.raw_value if old_property else '')
        elif property_type.raw_type == 'instance':
            form = ObjectPropertyInstanceForm(class_id=property_type.limitation['class_id'], initial_value=Instance.objects.get(id=old_property.raw_value) if old_property else Instance.objects.filter(class_instance_id=property_type.limitation['class_id']).first())
        elif property_type.raw_type == 'instance_list':
            form = ObjectPropertyInstanceListForm(class_id_list=property_type.limitation['allow_class_id_list'], initial_value=old_property.raw_value.split(',') if old_property else [])
        elif property_type.raw_type == 'json':
            try:
                initial_json = property_type.limitation['initial_json']
            except KeyError:
                initial_json = {}
            form = ObjectPropertyJSONForm(initial_value=old_property.raw_value if old_property else initial_json)
        elif property_type.raw_type == 'class':
            form = ObjectPropertyClassForm(initial_value=Class.objects.get(id=old_property.raw_value) if old_property else Class.objects.all().first())
        elif property_type.raw_type == 'url':
            form = ObjectPropertyURLForm(initial_value=old_property.raw_value if old_property else '')
        else:
            messages.error(request, f'Raw type {property_type.raw_type} is not supported for adding property')
            return redirect('apps_instance_detail', instance_id=instance_id)
    return render(request, 'apps/instances/property_form.html', {
        'form': form,
        'instance': instance,
        'property_type': property_type,
        'limitation_list': json_to_list(property_type.limitation),
        'old_property': old_property
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def instance_property_delete(request, instance_id, property_type_id):
    try:
        instance = Instance.objects.get(id=instance_id)
    except Instance.DoesNotExist:
        messages.error(request, f'Instance with id {instance_id} does not exist')
        return redirect('apps_instance_list')
    try:
        property_type = PropertyType.objects.get(id=property_type_id)
    except PropertyType.DoesNotExist:
        messages.error(request, f'Property type with id {property_type_id} does not exist')
        return redirect('apps_instance_list')
    if ObjectPropertyRelation.objects.filter(instance_object=instance, property_type=property_type).exists():
        ObjectPropertyRelation.objects.get(instance_object=instance, property_type=property_type).delete()
        messages.success(request, f'Property deleted successfully!')
    else:
        messages.error(request, f'Property does not exist')
    return redirect('apps_instance_detail_raw', instance_id=instance_id)


@login_required()
@user_passes_test(lambda u: u.is_staff)
def instance_create_wiki_property(request, instance_id):
    # create property type required for wiki
    # See list of required property type in apps/enums.py
    try:
        instance = Instance.objects.get(id=instance_id)
    except Instance.DoesNotExist:
        messages.error(request, f'Instance with id {instance_id} does not exist')
        return redirect('apps_instance_list')
    # create property type for wiki
    if not PropertyType.objects.filter(class_instance=instance.class_instance, name='wikiContent').exists():
        PropertyType.objects.create(
            class_instance=instance.class_instance,
            name='wikiContent',
            raw_type='markdown',
            limitation={}
        )
    if not PropertyType.objects.filter(class_instance=instance.class_instance, name='wikiImage').exists():
        PropertyType.objects.create(
            class_instance=instance.class_instance,
            name='wikiImage',
            raw_type='image',
            limitation={}
        )
    if not PropertyType.objects.filter(class_instance=instance.class_instance, name='wikiTitle').exists():
        PropertyType.objects.create(
            class_instance=instance.class_instance,
            name='wikiTitle',
            raw_type='string',
            limitation={
                'max_length': 255,
                'min_length': 1
            }
        )
    messages.success(request, f'Wiki property created successfully, please edit them!')
    return redirect('apps_instance_property_list', instance_id=instance_id)


def property_type_list(request):
    return render(request, 'apps/property_type/list.html', {
        'all_property_type': PropertyType.objects.all(),
        'all_classes': Class.objects.all()
    })


@login_required()
@user_passes_test(lambda u: u.is_staff)
def property_type_create(request):
    if request.method == 'POST':
        form = PropertyTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Property type created successfully!')
            return redirect('apps_property_type_list')
    else:
        form = PropertyTypeForm()
    return render(request, 'apps/property_type/create.html', {
        'form': form,
        'wiki_property_type_list': WIKI_PROPERTY_TYPE_LIST
    })


def property_type_detail(request, property_type_id):
    if not PropertyType.objects.filter(id=property_type_id).exists():
        messages.error(request, f'Property type with id {property_type_id} does not exist')
        return redirect('apps_property_type_list')
    property_type = PropertyType.objects.get(id=property_type_id)
    return render(request, 'apps/property_type/detail.html', {
        'property_type': property_type,
        'limitation_list': json_to_list(property_type.limitation),
        'all_property_value': ObjectPropertyRelation.objects.filter(property_type=property_type)
    })
