"""Storage service for handling file uploads and management."""
import logging
from minio import Minio, S3Error  # type: ignore
from fastapi import UploadFile
from io import BytesIO
import uuid
import magic
from PIL import Image
import pyclamd as clamd  # type: ignore

from core.config import settings
from core.exceptions import FileUploadException, BaseCustomException

logger = logging.getLogger(__name__)


class StorageService:
    """Service for handling file uploads and management using MinIO and ClamAV.

        Attributes:
            bucket_name (str): The name of the MinIO bucket to use for storage.
            client (Minio): The MinIO client instance for interacting with the storage service.
            clamd (ClamdNetworkSocket): The ClamAV client instance for virus scanning.
    """

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        self.clamd = clamd.ClamdNetworkSocket(
            settings.CLAMD_HOST, settings.CLAMD_PORT, timeout=30)
        self._ensure_bucket_exists()
        try:
            if not self.clamd.ping():
                raise BaseCustomException(
                    503, "ClamAV Unavailable", "Could not connect to ClamAV service")
        except Exception as e:
            raise BaseCustomException(
                503, "ClamAV Unavailable", f"Error connecting to ClamAV: {e}")

    def _ensure_bucket_exists(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        raw_url = self.client.presigned_get_object(
            self.bucket_name, object_name, expires=expires)
        return raw_url.replace(settings.MINIO_ENDPOINT, settings.VARNISH_URL)

    async def upload_image(
        self,
        file: UploadFile,
    ) -> tuple[str, str]:  # object_name, content_type
        """Uploads image to a given bucket, after doing several safety checks, with a randomly generated uuid.

        Args:
            file (UploadFile): File to be uploaded, expected to be an image.

        Raises:
            FileUploadException: When the file is empty, invalid, or corrupted.
            BaseCustomException: When the file exceeds the maximum size or has an unsupported type.
            BaseCustomException: When ClamAV is unavailable or fails to scan.
            FileUploadException: When the upload fails due to storage errors.
            BaseCustomException: When malware is detected during scanning.
            BaseCustomException: When an unexpected error occurs during scanning.

        Returns:
            str: The object name of the uploaded file.
        """
        contents = await file.read()
        size = len(contents)

        if size == 0:
            logger.warning("User attempted to upload empty file.")
            raise FileUploadException("Empty file")
        max_size_bytes = settings.MAX_UPLOAD_SIZE
        if max_size_bytes and size > max_size_bytes:
            logger.warning(f"Uploaded file exceeds size limit. Size: {size}")
            raise BaseCustomException(
                413, "File too large", f"File size {size} exceeds limit of {max_size_bytes} bytes")

        allowed_types = settings.ALLOWED_IMAGE_MIMES
        detected = magic.Magic(mime=True).from_buffer(contents)
        if allowed_types and detected not in allowed_types:
            logger.warning(f"Uploaded image has unsupported type: {detected}")
            raise BaseCustomException(
                415, "Unsupported file type", f"File type {detected} is not allowed")

        try:
            Image.open(BytesIO(contents)).verify()
        except Exception:
            raise FileUploadException("Invalid or corrupted image")

        try:
            # Use INSTREAM for memory buffer (no temp file needed)
            scan_result = self.clamd.scan_stream(BytesIO(contents))

            if scan_result:
                logger.warning("Uploaded file has malware!")
                raise BaseCustomException(
                    400, "Malware detected", f"Malware detected: {scan_result.get('stream', (None, None))[1] or 'unknown threat'}"
                )

        except clamd.ConnectionError as e:
            raise BaseCustomException(
                503, "Antivirus service unavailable", f"Error connecting to ClamAV: {str(e)}")
        except Exception as e:
            raise BaseCustomException(
                500, "Unexpected scan error", f"Error during antivirus scan: {str(e)}")

        ext = detected.split("/")[-1].replace("jpeg", "jpg")
        object_name = f"{uuid.uuid4().hex}.{ext}"

        try:
            self.client.put_object(
                bucket_name=self.bucket_name,  # or pass bucket as param
                object_name=object_name,
                data=BytesIO(contents),
                length=size,
                content_type=detected,
            )
        except Exception as e:
            raise FileUploadException(f"Upload failed: {e}")

        logger.info("File upload succesful")

        return detected, object_name

    async def delete_file(self, file_name: str):
        try:
            self.client.stat_object(self.bucket_name, file_name)
            self.client.remove_object(self.bucket_name, file_name)
        except S3Error:
            raise BaseCustomException(status_code=404, error="File not found",
                                      description=f"File {file_name} does not exist")
