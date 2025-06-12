from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ActionLog
from .serializers import UserActionLogSerializer
from datetime import datetime
import pytz

def get_indonesia_time():
    return datetime.now(pytz.timezone('Asia/Jakarta'))

class LogUserActionView(APIView):
    def post(self, request):
        data = request.data
        id_user = data.get("id_user")
        log_created = data.get("log_created")
        new_actions = data.get("list_action", [])

        if not id_user or not new_actions:
            return Response({"error": "id_user and list_action are required"}, status=400)

        user_log = ActionLog.objects.create(id_user=id_user,log_created=log_created, list_action=new_actions)

        serializer = UserActionLogSerializer(user_log)
        return Response({
            "message": "Log created successfully",
            "id": str(user_log.idLog),  # ini bagian penting untuk PHP
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        data = request.data
        id = data.get("id")
        new_actions = data.get("list_action", [])

        if not id or not new_actions:
            return Response({"error": "id and list_action are required"}, status=400)

        try:
            log = ActionLog.objects.get(idLog=id)
        except ActionLog.DoesNotExist:
            return Response({"error": "Log not found"}, status=404)

        log.list_action = new_actions
        log.save()

        serializer = UserActionLogSerializer(log)
        return Response(serializer.data, status=200)
