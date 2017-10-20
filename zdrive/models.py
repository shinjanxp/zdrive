from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.
@python_2_unicode_compatible  # only if you need to support Python 2
class Directory(models.Model):
    name = models.CharField(max_length=255)
    path=models.TextField(unique=True)
    def __str__(self):
        return self.name
    class Meta:
        permissions = (
            ('view_directory', 'View Directory'),
        )
@python_2_unicode_compatible  # only if you need to support Python 2
class File(models.Model):
    name = models.CharField(max_length=255)
    path=models.TextField(unique=True)
    def __str__(self):
        return self.name
    class Meta:
        permissions = (
            ('view_file', 'View file'),
        )