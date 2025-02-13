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
            # Debug: Print the incoming file name
            print(f"🔹 Initial file name received: {name}")
            logger.info(f"Initial file name received: {name}")

            if not name:
                logger.warning("⚠️ File name is missing, generating a default name.")
                name = f"default/{uuid.uuid4()}.jpg"

            # Get tenant schema name (default to 'default_tenant')
            tenant_name = self.get_current_tenant_name()
            print(f"🏢 Uploading for tenant: {tenant_name}")
            logger.info(f"Uploading for tenant: {tenant_name}")

            # Extract file extension (Ensure it always has a valid extension)
            ext = os.path.splitext(name)[1]
            if not ext:
                logger.warning("⚠️ File extension missing, assigning '.jpg'")
                ext = ".jpg"

            uuid_name = f"{uuid.uuid4()}{ext}"

            # Ensure a valid upload directory
            upload_subdirectory = os.path.dirname(name) if os.path.dirname(name) else "uploads"
            name = os.path.join(self.location, tenant_name, upload_subdirectory, uuid_name)

            # Replace backslashes (for Windows compatibility)
            name = name.replace("\\", "/")

            # Debug: Print final computed name
            print(f"✅ Final file path for S3: {name}")
            logger.info(f"Final file path in S3: {name}")

            # Set file name explicitly
            content.name = name

            return super()._save(name, content)

        except Exception as e:
            logger.error(f"❌ Error while saving file: {e}", exc_info=True)
            print(f"❌ Error while saving file: {e}")
            raise

    def get_current_tenant_name(self):
        """
        Retrieve the tenant schema name.
        """
        tenant_name = getattr(connection, "schema_name", "default_tenant")
        print(f"🔍 Current tenant schema: {tenant_name}")
        logger.info(f"Current tenant schema: {tenant_name}")
        return tenant_name
