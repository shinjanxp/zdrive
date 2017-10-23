from django.conf.urls import url

from . import api_views
from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [
	url(r'^api-token-auth/', rest_framework_views.obtain_auth_token),
    url(r'^home/', api_views.home, name='home'),
    url(r'^shared/', api_views.shared, name='shared'),
    url(r'^directory/edit/', api_views.directory_edit, name='directory_edit'),
    url(r'^directory/create/', api_views.directory_create, name='directory_create'),

    # url(r'^directory/(?P<path>(.*))', api_views.directory_show, name='directory_show'),

    url(r'^file/create/', api_views.file_create, name='file_create'),

    url(r'^file/', api_views.file_show, name='file_show'),
    url(r'^user/', api_views.user_list, name='user_list'),
    url(r'^me/', api_views.me, name='me'),

]