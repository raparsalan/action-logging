from rest_framework import serializers
from .models import ActionLog
import pytz

# class ActionLogSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ActionLog
#         fields = '__all__'    

class ActionItemSerializer(serializers.Serializer):
    id_action = serializers.CharField()
    time_action = serializers.DateTimeField()

class UserActionLogSerializer(serializers.ModelSerializer):
    list_action = ActionItemSerializer(many=True)

    class Meta:
        model = ActionLog
        fields = ['id_user','log_created', 'list_action']