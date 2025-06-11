from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ActionLog
from .serializers import UserActionLogSerializer
from datetime import datetime
import pytz

def get_indonesia_time():
    return datetime.now(pytz.timezone('Asia/Jakarta'))

# class LogViewSet(viewsets.ModelViewSet):
#     queryset = ActionLog.objects.all().order_by('timestamp')
#     serializer_class = ActionLogSerializer

#     def create(self, request, *args, **kwargs):
#         data = request.data.copy()

#         jakarta = pytz.timezone('Asia/Jakarta')
#         now_wib = datetime.now(jakarta)
#         data['timestamp'] = now_wib.strftime('%Y-%m-%d %H:%M:%S')

#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)

    #     
    #     jakarta = pytz.timezone('Asia/Jakarta')
    #     for item in serializer.data:
    #         if item['timestamp']:
    #             dt = datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
    #             item['timestamp'] = dt.astimezone(jakarta).strftime('%Y-%m-%d %H:%M:%S')

    #     return Response(serializer.data)

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
        return Response(serializer.data, status=status.HTTP_200_OK)
