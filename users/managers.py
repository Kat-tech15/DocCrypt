from django.contrib.auth.models import UserManager

class CustomUserManager(UserManager):
    def create_user(
            self,
            username,
            email=None, 
            password=None,
            **extra_fields
    ):
        extra_fields.setdefault("role", "STUDENT")

        return super().create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields,
        )
    
    def create_superuser(
            self, 
            username,
            email=None,
            password=None,
            **extra_fields
    ):
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        
        if extra_fields.get("is_superuser" is not True):
            raise ValueError("Superuser must hacve is_supeuser=True.")
        
        return super().create_superuser(
            username=username,
            email=email,
            password=password,
            **extra_fields,
        )