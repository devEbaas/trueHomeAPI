from rest_framework import serializers
from trueHomeAPI.apps.property.models import PropertyModel

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyModel
        fields = '__all__'

class PropertyFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyModel
        fields=['id','title', 'address']