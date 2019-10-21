from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from userInfo import userInfo
from directoryInfo import Directory
from filesInfo import File
import logging
import re


# get user from data
def getCurrentUser():
    user = users.get_current_user()
    if user:
        currentUserID = ndb.Key(userInfo, user.user_id())
        return currentUserID.get()



def addUser(user):
    currentUser = userInfo(id=user.user_id())
    addStartDirectory(currentUser)

    # set current path on first login to root directory
    currentUser.currentDirectory = ndb.Key(Directory, currentUser.key.id() + '/')
    currentUser.put()


def getFileList(file_name):
    currentUser = getCurrentUser()
    directoryList = getDirectoryList()
    path = getFilePath(file_name, directoryList)
    fileID = currentUser.key.id() + path
    fileKey = ndb.Key(File, fileID)
    return fileKey.get()


def getFilePath(name, directoryList):
    if getDirectoryList().parentDirectory is None:
        return directoryList.path + name
    else:
        return directoryList.path + '/' + name   


# returns key of current directory
def getDirectoryList():
    return getCurrentUser().currentDirectory.get()


def addStartDirectory(currentUser):
    directoryKey = currentUser.key.id() + '/'
    directory = Directory(id=directoryKey)

    directory.parentDirectory = None
    directory.name = 'root'
    directory.path = '/'
    directory.put()

    currentUser.root_directory = directory.key
    currentUser.put()


def addDirectory(name, parentDirectoryId):
    currentUser = getCurrentUser()

    directoryList = parentDirectoryId.get()

    path = getFilePath(name, directoryList)

    directoryKey = currentUser.key.id() + path
    directory = Directory(id=directoryKey)

    # check if directory already checkKey in this path
    if directory.key not in directoryList.directories:
        # Add key to parent directory
        directoryList.directories.append(directory.key)
        directoryList.put()

        # Set all attributes of the directory and save it to datastore
        directory.parentDirectory = parentDirectoryId
        directory.name = name
        directory.path = path
        directory.put()


def addFile(upload, file_name):
    currentUser = getCurrentUser()
    currentListDirectory = getDirectoryList()
    fileID = currentUser.key.id() + getFilePath(file_name, currentListDirectory)
    fileKey = ndb.Key(File, fileID)

    if fileKey not in currentListDirectory.files:
        file_object = File(id=fileID)
        file_object.name = file_name
        file_object.blob = upload.key()
        file_object.put()

        currentListDirectory.files.append(fileKey)
        currentListDirectory.put()

    else:
        # Delete uploaded file from the blobstore
        blobstore.delete(upload.key())
        logging.debug("A file with this name already checkKey in this directory!")


def deleteDirectory(directoryName):
    currentUser = getCurrentUser()

    # current directory is the parent directory of the one that will be deleted
    directoryList = getDirectoryList()

    directoryKey = currentUser.key.id() + getFilePath(directoryName, directoryList)
    directoryId = ndb.Key(Directory, directoryKey)
    directory_object = directoryId.get()

    if not directory_object.files and not directory_object.directories:
        # Delete reference to this object from parentDirectory
        directoryList.directories.remove(directoryId)
        directoryList.put()

        # Delete directory object from datastore
        directoryId.delete()


def deleteFile(file_name):
    currentUser = getCurrentUser()

    directoryList = getDirectoryList()
    path = getFilePath(file_name, directoryList)
    fileID = currentUser.key.id() + path
    fileKey = ndb.Key(File, fileID)

    # Delete file key from directoryInfo
    directoryList.files.remove(fileKey)
    directoryList.put()

    # Delete actual file from blobstore
    blobstore.delete(fileKey.get().blob)

    # Delete file object
    fileKey.delete()



# extracts all the names from a list of directory/ file keys
def getValueFromList(elements):
    names = list()

    for element in elements:
        names.append(element.get().name)

    return names
