from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from trueHomeAPI.apps.activity.api.serializers import ActivitySerializer, ActivityListSerializer, CancelActivitySerializer, ReAgendActivitySerializer
from trueHomeAPI.apps.common_functions import validate_schedule_availability
from trueHomeAPI.apps.activity.models import ActivityModel
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import logging

class ActivityAPIView(APIView):

    def get(self, request):
        activities = ActivityModel.objects.all()
        activity_serializer = ActivityListSerializer(activities,many=True, context={'request': request})
        return Response(activity_serializer.data, status = status.HTTP_200_OK)

    # Función para guardar una nueva actividad
    def post(self, request):
        try:
            activity_serializer = ActivitySerializer(data = request.data)
            activity_serializer.updated_at = timezone.now()
            if activity_serializer.is_valid():
                activity_data = activity_serializer.validated_data
                if activity_data['property_id'].status == "ENABLED":
                    # Retorna True si no hay actividiades e la hora seleccionada
                    is_available = validate_schedule_availability(activity_data['property_id'], activity_data['schedule'])
                    if is_available:
                        with transaction.atomic():
                            activity_serializer.save()
                            return Response(activity_serializer.data, status = status.HTTP_201_CREATED)
                    else:
                        return Response(data={'message': 'El horario ya se encuentra ocupado por otra actividad'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(data={'message': 'No se puede crear una actividad para una propiedad desactivada'},status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response(activity_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            logging.getLogger('Ha ocurrido un error al guardar la propiedad')
            print(ex)
            return Response(data = {'message': 'Ha ocurrido un error en el servidor'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CancelActivityAPIView(APIView):
    def get(self, request):
        activities = ActivityModel.objects.all()
        activity_serializer = ActivitySerializer(activities,many=True)
        return Response(activity_serializer.data, status = status.HTTP_200_OK)

    def post(self, request):
        try:
            cancel_serializer = CancelActivitySerializer(data = request.data)
            if cancel_serializer.is_valid():
                data = cancel_serializer.validated_data
                activity_to_cancel = get_object_or_404(ActivityModel.objects.all(), pk = data['id'])
                if activity_to_cancel.status == 'CANCELLED':
                    return Response(data = {'message': 'La Actividad ya ha sido cancelada'}, status = status.HTTP_400_BAD_REQUEST)
                with transaction.atomic():
                    activity_to_cancel.status = 'CANCELLED'
                    activity_to_cancel.updated_at = timezone.now()
                    activity_to_cancel.save()
                    return Response(ActivityListSerializer(activity_to_cancel, context={'request': request}).data, status = status.HTTP_202_ACCEPTED)
            else:
                return Response(cancel_serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as Ex:
            print(Ex)
            return Response(data = {'message': 'Ha ocurrido un error al actualizar el estatus de la actividad'}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReAgendActivityAPIView(APIView):
    def get(self, request):
        activities = ActivityModel.objects.all()
        activity_serializer = ActivitySerializer(activities,many=True)
        return Response(activity_serializer.data, status = status.HTTP_200_OK)

    def post(self, request):
        reagend_serializer = ReAgendActivitySerializer(data = request.data)
        try:
            if reagend_serializer.is_valid():
                data = reagend_serializer.validated_data
                activity_to_reagend = get_object_or_404(ActivityModel.objects.all(), pk=data['id'])
                if activity_to_reagend.status == "CANCELLED":
                    return Response(data ={'message':'La actividad no se puede reagendar debido a que está cancelada'}, status = status.HTTP_400_BAD_REQUEST)
                else:
                    # Se valida la disponibilidad de horario de la propiedad
                    is_available = validate_schedule_availability(activity_to_reagend.property_id, data['schedule'])
                    if is_available:
                        with transaction.atomic():
                            activity_to_reagend.schedule = data['schedule']
                            activity_to_reagend.updated_at = timezone.now()
                            activity_to_reagend.save()
                            return Response(ActivityListSerializer(activity_to_reagend,context={'request': request}).data, status = status.HTTP_202_ACCEPTED)
                        
                    else: 
                        return Response(data = {'message':'La fecha y hora proporcionada ya está en uso'}, status = status.HTTP_400_BAD_REQUEST)
            else:
                return Response(reagend_serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            print(ex)
