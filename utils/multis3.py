import os
import uuid
from storages.backends.s3boto3 import S3Boto3Storage
from django.db import connection

class TenantMediaStorage(S3Boto3Storage):
    location = "media"

    def _save(self, name, content):
        """
        Saves files in a tenant-specific directory with a UUID-based filename.
        """
        if not name:
            # Set a default name if missing
            name = f"default/{uuid.uuid4()}.jpg"

        # Get tenant schema name (default to 'default_tenant')
        tenant_name = self.get_current_tenant_name()

        # Extract file extension and generate a UUID-based filename
        ext = os.path.splitext(name)[1] or ".jpg"
        uuid_name = f"{uuid.uuid4()}{ext}"

        # Ensure a valid upload directory
        upload_subdirectory = os.path.dirname(name) if os.path.dirname(name) else "uploads"
        name = os.path.join(self.location, tenant_name, upload_subdirectory, uuid_name)

        # Set file name explicitly
        content.name = name

        return super()._save(name, content)

    def get_current_tenant_name(self):
        """
        Retrieve the tenant schema name.
        """
        return getattr(connection, "schema_name", "default_tenant")
