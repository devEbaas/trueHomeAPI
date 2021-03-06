from django.http import HttpRequest
from rest_framework import serializers
from django.contrib.sites.shortcuts import get_current_site
import logging
# Modelos, Serializadores y funciones
from trueHomeAPI.apps.activity.models import ActivityModel
from trueHomeAPI.apps.property.api.serializers import PropertyFilterSerializer
from trueHomeAPI.apps.survey.api.serializers import SurveySerializer
from trueHomeAPI.apps.common_functions import find_survey_by_activity, validate_activity_condition

# Definimos el logger
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityModel
        fields = '__all__'

# Serializer para listar actividades con campos de property y survey
class ActivityListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ActivityModel
        exclude = ['updated_at', 'property_id']

    def to_representation(self, instance):
        activity_data = super(ActivityListSerializer, self).to_representation(instance)
        property_data = PropertyFilterSerializer(instance.property_id).data
        survey = find_survey_by_activity(instance.id)
        survey_data = SurveySerializer(survey, context= self.context).data
        # Asignación de propiedades a la instancia 
        activity_data['condition'] = validate_activity_condition(instance)
        activity_data['property'] = property_data
        try:
            if survey_data:
                activity_data['survey'] = "{0}/survey/detail/{1}/".format(get_current_site(self.context['request']), survey.id)
        except Exception as ex:
            logger.error(f"Ha ocurrido el siguiente error: {ex}")
            activity_data['survey'] = None 
            
        return activity_data

class ReAgendActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    schedule = serializers.DateTimeField()


class CancelActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()

        # pass
    

# qs = ActivityModel.objects.prefetch_related('property_id')