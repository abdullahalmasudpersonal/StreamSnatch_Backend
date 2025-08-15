# from django.http import FileResponse, JsonResponse
# from rest_framework.decorators import api_view
# import yt_dlp
# import os
# import uuid

# DOWNLOAD_DIR = "downloads"

# @api_view(['POST'])
# def download_media(request):
#     url = request.data.get("url")
#     file_format = request.data.get("format", "mp4")

#     if not url:
#         return JsonResponse({"error": "URL is required"}, status=400)

#     if not os.path.exists(DOWNLOAD_DIR):
#         os.makedirs(DOWNLOAD_DIR)

#     file_name = f"{uuid.uuid4()}.{file_format}"
#     output_path = os.path.join(DOWNLOAD_DIR, file_name)

#     ydl_opts = {
#         'outtmpl': output_path,
#         'format': 'bestaudio/best' if file_format == 'mp3' else 'bestvideo+bestaudio/best',
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3' if file_format == 'mp3' else 'mp4',
#         }] if file_format == 'mp3' else [],
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             ydl.download([url])

#         response = FileResponse(open(output_path, 'rb'))
#         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return response
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)



import os
import uuid
import yt_dlp
from django.http import JsonResponse, FileResponse
from rest_framework.decorators import api_view

DOWNLOAD_DIR = "downloads"

@api_view(['POST'])
def download_media(request):
    url = request.data.get("url")
    file_format = request.data.get("format", "mp4")

    if not url:
        return JsonResponse({"error": "URL is required"}, status=400)

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    file_name = f"{uuid.uuid4()}.{file_format}"
    output_path = os.path.join(DOWNLOAD_DIR, file_name)

    # yt-dlp অপশন
    if file_format == "mp3":
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:  # mp4 বা অন্য ভিডিও ফরম্যাট
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': file_format,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # ফাইল রেসপন্স
        file_handle = open(output_path, 'rb')
        response = FileResponse(file_handle)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'

        # ডাউনলোড শেষে ফাইল মুছে ফেলার জন্য রেসপন্স ক্লোজ হবার পর হুক সেট করা
        def cleanup_file(response):
            file_handle.close()
            if os.path.exists(output_path):
                os.remove(output_path)
        response.close = lambda *args, **kwargs: (cleanup_file(response), None)

        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
