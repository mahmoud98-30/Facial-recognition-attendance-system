from django.db import models
from django.contrib.auth.models import User, AbstractUser, UserManager
from django.db.models.signals import post_save
from PIL import Image
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    is_student = models.BooleanField(default=False, verbose_name=_("Is Student"))
    is_lecturer = models.BooleanField(default=False, verbose_name=_("Is Lecturer"))
    phone = models.IntegerField(
        unique=True,
        verbose_name=_("Phone Number"))

    REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    def __str__(self):
        return self.username


class Profile(models.Model):
    image = models.ImageField(default='media/profile_pics/profile_logo.png', upload_to='profile_pics',
                              verbose_name=_("Image"))
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profile')

    def __str__(self):
        return '{} profile.'.format(self.user.username)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.width > 300 or img.height > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


def create_profile(sender, **kwarg):
    if kwarg['created']:
        Profile.objects.create(user=kwarg['instance'])


post_save.connect(create_profile, sender=User)
