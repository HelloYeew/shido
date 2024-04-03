import logging

from django.http import JsonResponse
from rest_framework.decorators import api_view

from apis.serializers import ClassSerializer, PropertyTypeSerializer, InstanceSerializer
from apps.models import Class, PropertyType, Instance

logger = logging.getLogger(__name__)
internal_server_error_message = JsonResponse({
    'message': 'Internal server error'
}, status=500)


@api_view(['GET'])
def get_class(request):
    """
    View for return all class in JSON format.
    """
    try:
        class_id = request.GET.get('class', None)
        if class_id:
            try:
                class_instance = Class.objects.get(id=class_id)
                return JsonResponse(ClassSerializer(class_instance).data)
            except Class.DoesNotExist:
                return JsonResponse({
                    'message': 'Class does not exist'
                }, status=404)
        else:
            return JsonResponse({
                'class': ClassSerializer(Class.objects.all(), many=True).data
            })
    except Exception as e:
        logger.error(f'Error when getting class')
        logger.exception(e)
        return internal_server_error_message


@api_view(['GET'])
def get_property_type_from_class(request):
    """
    View for return all property type of class in JSON format.
    """
    try:
        class_id = request.GET.get('class', None)
        if class_id is None or class_id == '':
            return JsonResponse({
                'message': 'No class ID provided'
            }, status=400)
        try:
            class_instance = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return JsonResponse({
                'message': 'Class does not exist'
            }, status=404)
        return JsonResponse({
            'property_type': PropertyTypeSerializer(PropertyType.objects.filter(class_instance=class_instance), many=True).data
        })
    except Exception as e:
        logger.error(f'Error when getting property type from class')
        logger.exception(e)
        return internal_server_error_message


@api_view(['GET'])
def get_instance_from_class(request):
    """
    View for return all instance of class in JSON format.
    """
    try:
        class_id = request.GET.get('class', None)
        if class_id is None or class_id == '':
            return JsonResponse({
                'message': 'No class ID provided'
            }, status=400)
        try:
            class_instance = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return JsonResponse({
                'message': 'Class does not exist'
            }, status=404)
        return JsonResponse({
            'class': ClassSerializer(class_instance).data,
            'instance': InstanceSerializer(Instance.objects.filter(class_instance=class_instance), many=True).data
        })
    except Exception as e:
        logger.error(f'Error when getting instance from class')
        logger.exception(e)
        return internal_server_error_message


@api_view(['GET'])
def get_instance(request, instance_id):
    """
    View for return instance in JSON format.
    """
    try:
        try:
            instance = Instance.objects.get(id=instance_id)
        except Instance.DoesNotExist:
            return JsonResponse({
                'message': 'Instance does not exist'
            }, status=404)
        return JsonResponse(InstanceSerializer(instance).data)
    except Exception as e:
        logger.error(f'Error when getting instance')
        logger.exception(e)
        return internal_server_error_message


@api_view(['GET'])
def get_random_instance_from_class(request):
    """
    View for return random instance of class in JSON format.
    """
    try:
        class_id = request.GET.get('class', None)
        number_of_instance = request.GET.get('number', 1)
        if class_id is None:
            return JsonResponse({
                'message': 'No class ID provided'
            }, status=400)
        try:
            number_of_instance = int(number_of_instance)
        except ValueError:
            return JsonResponse({
                'message': 'Number of instance is not a number'
            }, status=400)
        if number_of_instance < 1:
            return JsonResponse({
                'message': 'Number of instance must be greater than 0'
            }, status=400)
        try:
            class_instance = Class.objects.get(id=class_id)
            instance_amount = Instance.objects.filter(class_instance=class_instance).count()
            if number_of_instance > instance_amount:
                return JsonResponse({
                    'message': f'Number of instance must be less than or equal to {instance_amount}'
                }, status=400)
        except Class.DoesNotExist:
            return JsonResponse({
                'message': 'Class does not exist'
            }, status=404)
        return JsonResponse({
            'class': ClassSerializer(class_instance).data,
            'instance': InstanceSerializer(Instance.objects.filter(class_instance=class_instance).order_by('?')[:number_of_instance], many=True).data
        })
    except Exception as e:
        logger.error(f'Error when getting random instance from class')
        logger.exception(e)
        return internal_server_error_message
