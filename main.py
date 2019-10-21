import webapp2
import logging
import startViewer
import functions
import re
from uploadhandler import UploadHandler
from downloadhandler import DownloadHandler
from directoryInfo import Directory
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import ndb



class MainPage(webapp2.RequestHandler):

    # GET-request
    def get(self):
        logging.debug('GET')
        self.response.headers['Content-Type'] = 'text/html'

        # check whether user is logged in
        if users.get_current_user():
            # if userInfo object is None --> No user with key found --> new user --> make new user in datastore
            if not functions.getCurrentUser():
                functions.addUser(users.get_current_user())
            self.navigate()

            # get all directories and files in the current path
            directoriesList = functions.getDirectoryList().directories
            filesList = functions.getDirectoryList().files

            # sort all directories and files alphabetically
            directoriesList = sorted(directoriesList, key=lambda element: element.get().name.lower())
            filesList = sorted(filesList, key=lambda element: element.get().name.lower())

            # extract file and directory names from the key list
            # so that only the names have to be send to the gui and not the whole object
            directoriesList = functions.getValueFromList(directoriesList)
            filesList = functions.getValueFromList(filesList)
            val=""
            SizeOfCurrentWorkingDirectory = 0
            for file in filesList:
            	val=file
            	key1 = functions.getFileList(val)
            	stat=blobstore.BlobInfo.get(blobstore.BlobKey(str(key1.blob)))
            	SizeOfCurrentWorkingDirectory = SizeOfCurrentWorkingDirectory + stat.size
    		# renderer.showFileInformation(self,val,float(SizeOfCurrentWorkingDirectory)/(1000*1000))
            startViewer.showfileName(self,
                                users.create_logout_url(self.request.uri),
                                directoriesList,
                                filesList,
                                functions.getDirectoryList().path,
                                functions.getDirectoryList().parentDirectory is None,
								float(SizeOfCurrentWorkingDirectory)/1000,
                                blobstore.create_upload_url('/upload'))

        # if no user is logged in create login url
        else:
            startViewer.showLoginPage(self, users.create_login_url(self.request.uri))

    # POST-request
    def post(self):
        logging.debug('POST')
        self.response.headers['Content-Type'] = 'text/html'

        buttonVal = self.request.get('button')

        if buttonVal == 'Add':
            self.add()
            self.redirect('/')

        elif buttonVal == 'Delete':
            self.delete()
            self.redirect('/')

        elif buttonVal == 'Up':
            currentUser = functions.getCurrentUser()
            if not functions.getDirectoryList().parentDirectory is None:
            	parentDirectoryId = functions.getCurrentUser().currentDirectory.get().parentDirectory
            	currentUser.currentDirectory = parentDirectoryId
            	currentUser.put()
            self.redirect('/')

        elif buttonVal == 'info':
        	fileName = self.request.get('fileName')
        	key = functions.getFileList(fileName)
        	stat=blobstore.BlobInfo.get(blobstore.BlobKey(str(key.blob)))
    		startViewer.showFileInformation(self,fileName,stat.size/1000,stat.content_type,stat.creation)
            
        elif buttonVal == 'Home':
            currentUser = functions.getCurrentUser()
            currentUser.currentDirectory = ndb.Key(Directory, currentUser.key.id() + '/')
            currentUser.put()
            self.redirect('/')

        


    def add(self):
        directory_name = self.request.get('value')
        directory_name = re.sub(r'[/;]', '', directory_name).lstrip()
        if not (directory_name is None or directory_name == ''):
            functions.addDirectory(directory_name, functions.getCurrentUser().currentDirectory)

    def delete(self):
        name = self.request.get('name')
        kind = self.request.get('kind')

        if kind == 'file':
            functions.deleteFile(name)
        elif kind == 'directory':
            functions.deleteDirectory(name)


    def navigate(self):
        directory_name = self.request.get('directory_name')

        # Navigate to a directory sent in the url via get request
        if directory_name != '':
            currentUser = functions.getCurrentUser()
            directoryList = functions.getDirectoryList()
            directoryKey = currentUser.key.id() + functions.getFilePath(directory_name, directoryList)
            directoryId = ndb.Key(Directory, directoryKey)
            currentUser.currentDirectory = directoryId
            currentUser.put()

            self.redirect('/')


# starts the web application and specifies the routing table
app = webapp2.WSGIApplication(
    [
        ('/', MainPage),
        ('/upload', UploadHandler),
        ('/download', DownloadHandler)
    ], debug=True)
