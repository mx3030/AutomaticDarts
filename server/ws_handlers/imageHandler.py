import os
import base64
from PIL import Image, UnidentifiedImageError
from io import BytesIO

class ImageHandler:
    def base64_to_photo(self, data, position, image_dir):
        """
        Save a photo from base64 encoded data.

        Args:
            data (str): Base64 encoded image data.
            position (str): Position identifier for the image.
            image_dir (str): Directory to save the image.
        """
        try:
            base64_data = data.split(',')[1]
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            image_path = os.path.join(image_dir, f"{position}_img.jpg")
            image.save(image_path)
        except (ValueError, IndexError, UnidentifiedImageError) as e:
            print(f"Error saving photo: {e}")
