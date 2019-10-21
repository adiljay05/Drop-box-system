import jinja2
import os
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def showLoginPage(self, url):
    template_values = {
        'url': url
    }

    template = JINJA_ENVIRONMENT.get_template('/templates/login.html')
    self.response.write(template.render(template_values))


def showfileName(self, url, directories, files, current_path, is_in_root,sizeOfDirectory ,upload_url):
    template_values = {
        'url': url,
        'user': users.get_current_user(),
        'directories': directories,
        'files': files,
        'current_path': current_path,
        'is_not_in_root': not is_in_root,
        'upload_url': upload_url,
        'sizeOfDirectory' : sizeOfDirectory,
        'fileCount' : 0
    }

    template = JINJA_ENVIRONMENT.get_template('/templates/main.html')
    self.response.write(template.render(template_values))

def showFileInformation(self,fname,size,type1,creation):
    template_values = {
        'fileName' : fname,
        'user': users.get_current_user(),
        'size' : size,
        'type1': type1,
        'creation': creation
    }

    template = JINJA_ENVIRONMENT.get_template('/templates/fileInformation.html')
    self.response.write(template.render(template_values))