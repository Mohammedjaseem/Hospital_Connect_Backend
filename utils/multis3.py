import os
import uuid
from storages.backends.s3boto3 import S3Boto3Storage
from django.db import connection  # Get tenant schema name

class TenantMediaStorage(S3Boto3Storage):
    location = "media"

    def _save(self, name, content):
        """
        Saves files in a tenant-specific directory with UUID-based names.
        """
        tenant_name = self.get_current_tenant_name()

        # Extract file extension
        ext = os.path.splitext(name)[1]
        uuid_name = f"{uuid.uuid4()}{ext}"  # Generate unique filename

        # Extract upload subdirectory (e.g., "users/picture")
        upload_subdirectory = os.path.dirname(name)

        # Construct full S3 path
        name = os.path.join(self.location, tenant_name, upload_subdirectory, uuid_name)

        return super()._save(name, content)

    def get_current_tenant_name(self):
        """
        Retrieve the tenant schema name.
        """
        return getattr(connection, "schema_name", "default_tenant")  # Default if no tenant is found
