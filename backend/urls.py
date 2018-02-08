from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home/', views.home, name='home'),
    url(r'^shared/', views.shared, name='shared'),
    url(r'^directory/edit/', views.directory_edit, name='directory_edit'),
    url(r'^directory/create/', views.directory_create, name='directory_create'),
    # url(r'^directory/(?P<path>(.*))', views.directory_show, name='directory_show'),

    url(r'^file/create/', views.file_create, name='file_create'),

    url(r'^file/', views.file_show, name='file_show'),

]