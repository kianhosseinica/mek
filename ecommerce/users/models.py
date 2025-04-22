from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.db import models
from django.conf import settings
from store.models import Product
from orders.models import *
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.db import models
from django.conf import settings
from store.models import Product
from django.utils.timezone import now  # Import for default timestamps

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone_number, email=None, first_name="", last_name="", password=None, **extra_fields):
        """Creates and saves a regular user with the given phone number and password."""
        if not phone_number:
            raise ValueError("The phone number must be set")

        extra_fields.setdefault("is_active", True)

        user = self.model(
            phone_number=phone_number,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email=None, first_name="", last_name="", password=None, **extra_fields):
        """Creates and saves a superuser with the given phone number and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone_number, email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Completely remove username

    CUSTOMER_TYPES = [
        ('regular', 'Regular'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('platinum', 'Platinum'),
    ]

    customer_type = models.CharField(max_length=10, choices=CUSTOMER_TYPES, default='regular')
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    verification_code = models.CharField(max_length=4, blank=True, null=True)

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, default='profile_images/default.jpg')

    company = models.CharField(max_length=255, blank=True, default="No Company")
    birth_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    member_since = models.DateTimeField(auto_now_add=True)  # Automatically set when user is created
    is_online = models.BooleanField(default=False)  # Track if the user is online

    # New field: Designates whether the user has access to the POS system.
    is_pos = models.BooleanField(default=False, help_text="Designates whether this user has access to the POS system.")

    # New field: POS PIN code (only required if is_pos is True)
    pos_pin = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        validators=[RegexValidator(regex='^[0-9]{4,6}$', message='PIN must be 4 to 6 digits')],
        help_text="Enter a 4-6 digit PIN if POS access is enabled."
    )

    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"

    def get_profile_image_url(self):
        """Returns profile image URL or a default image if not available."""
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return settings.MEDIA_URL + 'profile_images/default.jpg'  # Ensures correct default image

    def get_member_since(self):
        """Returns formatted 'member since' date."""
        return self.member_since.strftime("%B %d, %Y")  # Example: "January 15, 2023"

    def set_online(self):
        """Sets user status to online."""
        self.is_online = True
        self.save(update_fields=['is_online'])

    def set_offline(self):
        """Sets user status to offline."""
        self.is_online = False
        self.save(update_fields=['is_online'])

    def total_orders(self):
        """Returns the total number of orders placed by the user."""
        return Order.objects.filter(user=self).count()



class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name}'s wishlist - {self.product.name}"
