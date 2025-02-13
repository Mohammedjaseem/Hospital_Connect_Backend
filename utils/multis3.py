import os
import uuid
import logging
from storages.backends.s3boto3 import S3Boto3Storage
from django.db import connection

# Configure logging
logger = logging.getLogger(__name__)

class TenantMediaStorage(S3Boto3Storage):
    location = "media"

    def _save(self, name, content):
        """
        Saves files in a tenant-specific directory with a UUID-based filename.
        """
        try:
            if not name:
                logger.warning("File name is missing, generating a default name.")
                name = f"default/{uuid.uuid4()}.jpg"

            # Get tenant schema name (default to 'default_tenant')
            tenant_name = self.get_current_tenant_name()
            logger.info(f"Uploading for tenant: {tenant_name}")

            # Extract file extension and generate a UUID-based filename
            ext = os.path.splitext(name)[1] or ".jpg"
            uuid_name = f"{uuid.uuid4()}{ext}"

            # Ensure a valid upload directory
            upload_subdirectory = os.path.dirname(name) if os.path.dirname(name) else "uploads"
            name = os.path.join(self.location, tenant_name, upload_subdirectory, uuid_name)

            # Set file name explicitly
            content.name = name
            logger.info(f"Final file path in S3: {name}")

            return super()._save(name, content)

        except Exception as e:
            logger.error(f"Error while saving file: {e}", exc_info=True)
            raise

    def get_current_tenant_name(self):
        """
        Retrieve the tenant schema name.
        """
        tenant_name = getattr(connection, "schema_name", "default_tenant")
        logger.info(f"Current tenant schema: {tenant_name}")
        return tenant_name
