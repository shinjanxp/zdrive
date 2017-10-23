from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from .models import Directory, File
from .serializers import *
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user, get_users_with_perms, get_user_perms
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers

# Create your views here.
ZDRIVE_ROOT = settings.ZDRIVE_ROOT

def get_logical_path(abs_path):
	if abs_path.startswith(ZDRIVE_ROOT):
		lp= abs_path[len(ZDRIVE_ROOT):]
	if not lp[-1] == '/':
		lp = lp +"/"
	return lp

def get_parent_directory(directory):
	directory = directory.split('/')
	if directory[-1] == "":
		directory = directory[:-2]
	else:
		directory = directory[:-1]

	return "/".join(directory) + "/"
# def index(request):
# 	return render(request,"index.html")

@csrf_exempt
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
    	serializer = UserSerializer(data=request.data)
    	if serializer.is_valid():
    		user = serializer.save()
    		if user:
    			return Response(serializer.data, status=status.HTTP_201_CREATED)
    	else:
    		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)			


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def home(request):
	try:
		path = request.GET['path']
	except:
		path = request.user.username + "/"
		return redirect('/api/zdrive/home/?path='+path)
	try:
	# print(path)
		d = Directory.objects.get(path=path)
		if not request.user.has_perm('view_directory',d):
			return JsonResponse('Unauthorized', status=401)
	except:
		pass
	# path should always carry trailing slash but no leading slash
	abs_path = os.path.join(ZDRIVE_ROOT, path)
	# print(abs_path)
	files = [f for f in os.listdir(abs_path) if os.path.isfile(abs_path+"/"+f)]
	files.sort()
	# print(files)
	directories = list(set(os.listdir(abs_path)) - set(files))
	directories.sort()
	# print(directories)
	if path != "" and path[-1]!='/':
		path = path + "/"
	# print(directories,path)
	parent_path = get_parent_directory(path)
	return JsonResponse({'directories':directories, 'files':files, 'path':path, 'parent_path':parent_path})

@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def shared(request):
	shared_directories = get_objects_for_user(request.user, 'zdrive.view_directory')
	shared_files = get_objects_for_user(request.user, 'zdrive.view_file')

	return JsonResponse({'directories':shared_directories, 'files':shared_files,})


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def me(request):
	user = User.objects.get(pk=request.user.id);
	serializer = UserSerializer(user)
	print(serializer.data)
	return JsonResponse(serializer.data,safe=False)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def user_list(request):
	try:
		d = Directory.objects.get(path=request.GET['path'])
	except:
		return JsonResponse('Not found', status=404)
	users = User.objects.all();
	serializer = UserSerializer(users, many=True)
	serializer = serializer.data
	users = []
	for s in serializer:
		user = dict(s)
		user['perms'] = list(get_user_perms(User.objects.get(pk=user['id']),d))
		users.append(user)
	# for user in serializer:
	# 	for key, value in users:
	# 		if key.id == user.id:
	# 			user.perms = value
	return JsonResponse(users,safe=False)

@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def directory_create(request):
	try:
		d = Directory.objects.get(path=request.GET['path'])
		if not request.user.has_perm('add_directory',d):
			return JsonResponse('Unauthorized', status=401)
	except:
		pass
	# print (ZDRIVE_ROOT, request.user.username, request.GET['path'], request.POST['name'])
	abs_path = os.path.join(ZDRIVE_ROOT, request.GET['path'], request.data['name'])
	d=Directory.objects.create(path = get_logical_path(abs_path), name=request.data['name'])
	# abs_path = os.path.join(abs_path, request.GET['path'])
	# print(abs_path)
	if not os.path.exists(abs_path):
		os.makedirs(abs_path)
	assign_perm("view_directory", request.user, d)
	assign_perm("add_directory", request.user, d)
	assign_perm("change_directory", request.user, d)
	return redirect("/api/zdrive/home/?path="+os.path.join(request.GET['path']))

@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def directory_edit(request):
	try:
	# print(path)
		d = Directory.objects.get(path=request.GET['path'])
		if not request.user.has_perm('change_directory',d):
			return JsonResponse('Unauthorized', status=401)
	except:
		pass
	old_path = os.path.join(ZDRIVE_ROOT, request.GET['path'])
	new_path = os.path.join( os.path.abspath(get_parent_directory(old_path)) , request.data['name'])
	d, created = Directory.objects.get_or_create(path = get_logical_path(old_path), name=request.data['name'])
	os.rename(old_path,new_path)
	d.path = get_logical_path(new_path)
	d.name = request.data['name']
	d.save()
	# Assign perm
	# print(get_logical_path(new_path))
	#first remove all perms
	for user in User.objects.all():
		remove_perm('view_directory', user, d)
		remove_perm('add_directory', user, d)
		remove_perm('change_directory', user, d)

	view_perm_users=request.data.getlist('view')
	add_perm_users=request.data.getlist('add')
	change_perm_users=request.data.getlist('change')
	for view_perm_user in view_perm_users:
		assign_perm("view_directory", User.objects.get(pk=view_perm_user), d)
	for add_perm_user in add_perm_users:
		assign_perm("view_directory", User.objects.get(pk=add_perm_user), d)
		assign_perm("add_directory", User.objects.get(pk=add_perm_user), d)
	for change_perm_user in change_perm_users:
		assign_perm("view_directory", User.objects.get(pk=change_perm_user), d)
		assign_perm("add_directory", User.objects.get(pk=change_perm_user), d)
		assign_perm("change_directory", User.objects.get(pk=change_perm_user), d)
	return redirect("/api/zdrive/home/?path="+get_parent_directory(request.GET['path']) )

@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def file_create(request):
	# print (ZDRIVE_ROOT, request.user.username, request.GET['path'], request.POST['name'])
	abs_path = os.path.join(ZDRIVE_ROOT, request.GET['path'], )
	# abs_path = os.path.join(abs_path, request.GET['path'])
	# print(abs_path)
	if os.path.exists(abs_path):
		file = request.FILES['file']
		uploaded_filename = request.FILES['file'].name
		full_filename = os.path.join(abs_path, uploaded_filename)
		fout = open(full_filename, 'wb+')

		file_content = ContentFile( request.FILES['file'].read() )

		# Iterate through the chunks.
		for chunk in file_content.chunks():
			fout.write(chunk)
		fout.close()
		File.objects.create(path = get_logical_path(abs_path), name=uploaded_filename)

	return redirect("/api/zdrive/home/?path="+os.path.join(request.GET['path']))

@login_required
def file_show(request):
	path = request.GET['path']
	file_path = os.path.join(ZDRIVE_ROOT, path)
	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
			response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
			return response
	raise Http404