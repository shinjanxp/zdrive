from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Directory, File
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user
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
def index(request):
	return render(request,"index.html")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            # Create user's root directory same as username
            abs_path = os.path.join(ZDRIVE_ROOT, user.username)
            if not os.path.exists(abs_path):
            	os.makedirs(abs_path)
            login(request, user)
            return redirect('/zdrive/home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def home(request):
	try:
		path = request.GET['path']
	except:
		path = request.user.username + "/"
		return redirect('/zdrive/home/?path='+path)
	try:
	# print(path)
		d = Directory.objects.get(path=path)
		if not request.user.has_perm('view_directory',d):
			return HttpResponse('Unauthorized', status=401)
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
	return render(request,"home.html",{'directories':directories, 'files':files, 'path':path, 'parent_path':parent_path})

@login_required
def shared(request):
	shared_directories = get_objects_for_user(request.user, 'zdrive.view_directory')
	shared_files = get_objects_for_user(request.user, 'zdrive.view_file')

	return render(request,"shared.html",{'directories':shared_directories, 'files':shared_files,})

@login_required
def directory_create(request):
	try:
		d = Directory.objects.get(path=request.GET['path'])
		if not request.user.has_perm('add_directory',d):
			return HttpResponse('Unauthorized', status=401)
	except:
		pass
	if request.method=="GET":
		users = User.objects.all()
		return render(request,"create_directory.html",{'users':users})
	else:
		# print (ZDRIVE_ROOT, request.user.username, request.GET['path'], request.POST['name'])
		abs_path = os.path.join(ZDRIVE_ROOT, request.GET['path'], request.POST['name'])
		d=Directory.objects.create(path = get_logical_path(abs_path), name=request.POST['name'])
		# abs_path = os.path.join(abs_path, request.GET['path'])
		# print(abs_path)
		if not os.path.exists(abs_path):
			os.makedirs(abs_path)
		assign_perm("view_directory", request.user, d)
		assign_perm("add_directory", request.user, d)
		assign_perm("change_directory", request.user, d)
		return redirect("/zdrive/home/?path="+os.path.join(request.GET['path']))

@login_required
def directory_edit(request):
	try:
	# print(path)
		d = Directory.objects.get(path=request.GET['path'])
		if not request.user.has_perm('change_directory',d):
			return HttpResponse('Unauthorized', status=401)
	except:
		pass
	if request.method=="GET":
		users = User.objects.all()
		# name = request.GET['path'].split('/')[-1]
		d = Directory.objects.get(path=request.GET['path'])
		return render(request,"edit_directory.html",{'name':d.name, 'users':users, 'directory':d})
	else:
		old_path = os.path.join(ZDRIVE_ROOT, request.GET['path'])
		new_path = os.path.join( os.path.abspath(get_parent_directory(old_path)) , request.POST['name'])
		d, created = Directory.objects.get_or_create(path = get_logical_path(old_path), name=request.POST['name'])
		os.rename(old_path,new_path)
		d.path = get_logical_path(new_path)
		d.name = request.POST['name']
		d.save()
		# Assign perm
		# print(get_logical_path(new_path))
		#first remove all perms
		for user in User.objects.all():
			remove_perm('view_directory', user, d)
			remove_perm('add_directory', user, d)
			remove_perm('change_directory', user, d)

		view_perms=request.POST.getlist('view')
		add_perms=request.POST.getlist('add')
		change_perms=request.POST.getlist('change')
		for view_perm_users in view_perms:
			assign_perm("view_directory", User.objects.get(pk=view_perm_users), d)
		for add_perm_users in add_perms:
			assign_perm("view_directory", User.objects.get(pk=add_perm_users), d)
			assign_perm("add_directory", User.objects.get(pk=add_perm_users), d)
		for change_perm_users in change_perms:
			assign_perm("view_directory", User.objects.get(pk=change_perm_users), d)
			assign_perm("add_directory", User.objects.get(pk=change_perm_users), d)
			assign_perm("change_directory", User.objects.get(pk=change_perm_users), d)
		return redirect("/zdrive/home/?path="+get_parent_directory(request.GET['path']) )

@login_required
def file_create(request):
	if request.method=="GET":
		return render(request,"edit_file.html")
	else:
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

		return redirect("/zdrive/home/?path="+os.path.join(request.GET['path']))

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