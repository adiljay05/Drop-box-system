from google.appengine.ext import *


class userInfo(ndb.Model):
    # A KeyProperty which stores the root directory key
    root_directory = ndb.KeyProperty()

    # The current path in which the user is in/ was in the last time
    currentDirectory = ndb.KeyProperty()
