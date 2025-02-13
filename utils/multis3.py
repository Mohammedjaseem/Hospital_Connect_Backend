import os
import uuid
from storages.backends.s3boto3 import S3Boto3Storage
from django.db import connection  # For tenant schema name retrieval

class TenantMediaStorage(S3Boto3Storage):
    location = 'media'

    def _save(self, name, content):
        """
        Override the _save method to include tenant-specific directory
        and rename the file to a UUID-based file name.
        """
        if not name:
            raise ValueError("File name is not set. Ensure the model's 'upload_to' is correctly defined.")

        # Get the current tenant schema name
        tenant_name = self.get_current_tenant_name()

        # Extract the file extension
        ext = os.path.splitext(name)[1]
        # Generate a UUID-based file name
        uuid_name = f"{uuid.uuid4()}{ext}"

        # Ensure the name is not empty before using os.path.dirname
        upload_subdirectory = os.path.dirname(name) if name else ''  # Extract upload_to path
        name = os.path.join(self.location, tenant_name, upload_subdirectory, uuid_name)

        return super()._save(name, content)

    def get_current_tenant_name(self):
        """
        Get the current tenant schema name from Django's connection object.
        """
        return getattr(connection, 'schema_name', 'default_tenant')  # Fallback to 'default_tenant'
