from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom user manager for handling:
    - user creation
    - superuser creation
    - email normalization
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a new user.
        """
        if not email:
            raise ValueError("Users must have an email address")

        # Normalize email = make lowercase
        email = self.normalize_email(email)

        # create user object
        user = self.model(email=email, **extra_fields)

        # hash password
        if password:
            user.set_password(password)
        else:
            raise ValueError("Password is required")

        # save user to database
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a new superuser.
        Must have is_staff and is_superuser = True
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Protection: avoid mistakes
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)
