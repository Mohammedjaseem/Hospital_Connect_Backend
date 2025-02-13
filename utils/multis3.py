import os
import uuid
from storages.backends.s3boto3 import S3Boto3Storage
from django.db import connection  # To get the tenant schema name

class TenantMediaStorage(S3Boto3Storage):
    location = "media"

    def _save(self, name, content):
        """
        Saves files in a tenant-specific directory with a UUID-based filename.
        """
        if not name:
            raise ValueError("File name is required but was not provided.")

        # Get the tenant schema name (Default to 'default_tenant' if not found)
        tenant_name = self.get_current_tenant_name()

        # Extract file extension
        ext = os.path.splitext(name)[1] or ".jpg"  # Default to .jpg if extension missing
        uuid_name = f"{uuid.uuid4()}{ext}"  # Generate a unique filename

        # Ensure the name has a valid path
        upload_subdirectory = os.path.dirname(name) if os.path.dirname(name) else "uploads"

        # Construct full S3 path
        name = os.path.join(self.location, tenant_name, upload_subdirectory, uuid_name)

        # Ensure name is set properly
        content.name = name

        return super()._save(name, content)

    def get_current_tenant_name(self):
        """
        Retrieve the tenant schema name.
        """
        return getattr(connection, "schema_name", "default_tenant")  # Default fallback
