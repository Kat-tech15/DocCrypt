import base64
import hashlib
import os
import logging
from pathlib import Path
from .models import Document
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Handles document encryption and decryption.
    """
    @staticmethod
    def derive_user_key(student):
        """
        Derive a Fernet-compatible key from the student's admission number
        and the application's SECRET_KEY.
        """
        secret = f"{student.admission_number}{settings.SECRET_KEY}"

        digest = hashlib.sha256(secret.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    @staticmethod
    def generate_document_key():
        """
        Generate a unique encryption key for a document.
        """
        return Fernet.generate_key()

    @staticmethod
    def read_file(file_field):
        """ 
        Read and return the contents of a Django FileField.
        """
        if not file_field:
            raise FileNotFoundError("No file is associated with the document.")
        
        if not os.path.exists(file_field.path):
            raise FileNotFoundError(f"{file_field.name} does not exist.")
        
        with file_field.open("rb") as file:
            return file.read()

    @staticmethod
    def encrypt_document(document):
        """
        Encrypt a document and securely store its encrypted
        document key.
        """
        try:
            original_data = EncryptionService.read_file(document.original_file)
            document_key = EncryptionService.generate_document_key()
            cipher = Fernet(document_key)
            encrypted_data = cipher.encrypt(original_data)

            safe_title = slugify(document.title)
            encrypted_filename = (
                f"{safe_title}-{document.id}.encrypted"
            )

            user_key = EncryptionService.derive_user_key(
                document.student
            )

            key_cipher = Fernet(user_key)
            wrapped_key = key_cipher.encrypt(document_key)

            with transaction.atomic():

                if document.encrypted_file:
                    document.encrypted_file.delete(save=False)

                document.encrypted_file.save(
                    encrypted_filename,
                    ContentFile(encrypted_data),
                    save=False,
                )

                document.encrypted_key = wrapped_key
                document.status = Document.Status.ENCRYPTED
                document.encrypted_at = timezone.now()
                document.save()

            logger.info(
                "Document '%s' encrypted successfully.", document.title)

        except Exception:
            logger.exception(
                "Failed to encrypt document '%s'.",
                document.title,
            )
            raise

    @staticmethod
    def recover_document_key(document, admission_number):
        """
        Recover the encrypted document key using the
        student's admission number.
        """
        if admission_number != document.student.admission_number:
            raise ValueError("Invalid admission number.")

        user_key = EncryptionService.derive_user_key(document.student)

        key_cipher = Fernet(user_key)
        return key_cipher.decrypt(document.encrypted_key)

    @staticmethod
    def decrypt_document(document, admission_number):
        """
        Decrypt a document and return its original bytes.
        """
        try:
            encrypted_data = EncryptionService.read_file(
                document.encrypted_file
            )
            document_key = (
                EncryptionService.recover_document_key(
                    document,
                    admission_number,
                )
            )

            cipher = Fernet(document_key)
            return cipher.decrypt(encrypted_data)

        except InvalidToken:
            logger.warning(
                "Invalid admission number supplied for '%s'.",
                document.title,
            )
            raise

        except Exception:
            logger.exception(
                "Failed to decrypt document '%s'.",
                document.title,
            )
            raise