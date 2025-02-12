from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
class ImageCompressorMixin:
    def compress_image(self):
        image = Image.open(self.picture)

        if image.mode == 'RGBA':
            image = image.convert('RGB')
        elif image.mode == 'LA':
            image = image.convert('RGB')  # Convert 'LA' to 'RGB'

        image = ImageOps.exif_transpose(image)

        max_size = (1000, 1000)
        image.thumbnail(max_size, Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BILINEAR)

        image_buffer = BytesIO()
        image.save(image_buffer, format='JPEG')
        image_buffer.seek(0)
        
        uuid_code = uuid.uuid4()

        self.picture = InMemoryUploadedFile(
            image_buffer,
            'ImageField',
            f'{uuid_code}.jpeg',
            'image/jpeg',
            image.tell(),
            None
        )