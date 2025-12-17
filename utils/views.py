`from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .cloudinary_service import CloudinaryService
from rest_framework.permissions import IsAuthenticated

class CloudinaryUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('image_url')
        if not file:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        folder = request.data.get('folder', 'general')
        url = CloudinaryService.upload_image(file, folder=folder)
        
        if url:
            return Response({"url": url}, status=status.HTTP_200_OK)
        return Response({"error": "Upload failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
