from django.contrib import admin
from guardian.admin import GuardedModelAdmin

# Register your models here.

from .models import Directory, File
class DirectoryAdmin(GuardedModelAdmin):
	pass

admin.site.register(Directory, DirectoryAdmin)
# admin.site.register(Directory)
admin.site.register(File)