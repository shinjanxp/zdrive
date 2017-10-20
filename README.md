# Requirements
* Python3
* django 1.11
* django-guardian

# Installation
* Run `./setup.sh`

# Description

* The project is a scaled down version of Google Drive. 
* Libraries used: 
	* Material Bootstrap
	* Google fonts
* The home page is taken from lab1 assignment b.
* The project supports creation and renaming of folders and upload/download of files. Storage is in the zdrive/home folder inside this project.
 * Each directory in the application corresponds to a similar directory in the linux filesystem. Each user of the application is given a separate folder inside zdrive/home. All files/folders created by a user is stored inside his/her folder. 
 * Clicking on a folder shows all subfolders and files inside it. Clicking on a file downloads it. Hovering on a folder causes a edit button to show, clicking on which takes one to the permission edit and renaming page.
 * Folder sharing option has been implemented using django-guardian. One user may share a folder with any number of other users in view, add or change mode. Once a folder is shared, all items which are only direct descendents of that folder will be available to the shared user. They will be visible in the `Shared with me` link on the right hand side of portal.
 * There is a small bug where clicking on the back arrow when on the home page causes the linux root directory to become visible. 
 * Custom filter tag has been implemented to show user initials with hashed color on permissions page.
 * There are currently 2 users:
 	* username: shinjan, password: django123
 	* username: johndoe, password: django123
 	* shinjan is the superuser and has all permissions on all objects.