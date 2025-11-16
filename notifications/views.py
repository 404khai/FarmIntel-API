from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from .models import Notification
from .serializers import NotificationSerializer


# -------------------------------
# 1. List All Notifications
# -------------------------------
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")


# -------------------------------
# 2. Mark One Notification Read
# -------------------------------
class MarkNotificationReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()

        if notification.user != request.user:
            return Response({"error": "Not your notification"}, status=403)

        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"})


# -------------------------------
# 3. Mark ALL Notifications Read
# -------------------------------
class MarkAllNotificationsReadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"message": "All notifications marked as read"}, status=200)
