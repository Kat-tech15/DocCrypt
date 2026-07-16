import base64
import hashlib
import logging
from django.db import transaction
from pathlib import Path
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

class EncryptionService:

    @staticmethod
    def derive_user_key(student):
        secret = (
            student.admission_number +
            settings.SECRET_KEY
        )

        digest = hashlib.sha256(
            secret.encode()
        ).digest()

        return base64.urlsafe_b64encode(digest)

    @staticmethod
    def generate_document_key():
        return Fernet.generate_key()

    @staticmethod
    def encrypt_document(document):
        try:
            with document.original_file.open("rb") as file:

                original_data = file.read()

            document_key = EncryptionService.generate_document_key()

            cipher = Fernet(document_key)

            encrypted_data = cipher.encrypt(original_data)

            original_name = Path(document.original_file.name).stem
            encrypted_filename = f"{original_name}.encrypted"

            user_key = EncryptionService.derive_user_key(document.student)
            key_cipher = Fernet(user_key)
            wrapped_key = key_cipher.encrypt(document_key)
                
            with transaction.atomic():
                document.encrypted_file.save(
                    encrypted_filename,
                    ContentFile(encrypted_data),
                    save=False
                )
                document.encrypted_key = wrapped_key
                document.status = document.Status.ENCRYPTED
                document.encrypted_at = timezone.now()
                document.save()
                    
            logger.info(f"Document '{document.title}' encrypted successfully.")
                
        except Exception as e:
            logger.exception(f"Encryption failed for document '{document.title}'.")
            raise
    
    @staticmethod
    def recover_document_key(document, admission_number):
        secret = (
            admission_number + settings.SECRET_KEY
        )
        digest =hashlib.sha256(secret.encode()).digest()
        user_key = base64.urlsafe_b64encode(digest)
        key_cipher = Fernet(user_key)
        return key_cipher.decrypt(document.encrypted_key)
    
    @staticmethod
    def decrypt_document(document, admission_number):
        try:
            with document.encrypted_file.open("rb") as file:
                encrypted_data = file.read()
            print(f"Encrypted size: {len(encrypted_data)} bytes")
            document_key = EncryptionService.recover_document_key(
                document,
                admission_number
            )
            print(document_key)
            cipher = Fernet(document_key)
            original_data = cipher.decrypt(encrypted_data)
            print(f"Original size: {len(original_data)} bytes")
            return original_data

        except Exception:
            logger.exception(
                f"Failed to decrypt document '{document.title}'."
            )
            raise