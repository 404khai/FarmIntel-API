import cloudinary.uploader
from django.conf import settings

class CloudinaryService:
    @staticmethod
    def upload_image(file, folder="uploads"):
        """
        Uploads an image to Cloudinary and returns the URL.
        """
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                folder=folder
            )
            return upload_result.get("secure_url")
        except Exception as e:
            print(f"Cloudinary upload error: {e}")
            return None
