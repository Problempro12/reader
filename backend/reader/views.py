from django.http import FileResponse
from django.conf import settings
import os

class MediaFileView(APIView):
    def get(self, request, path):
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'))
            response['Access-Control-Allow-Origin'] = '*'
            return response
        return Response({'error': 'File not found'}, status=404) 