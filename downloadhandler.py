from google.appengine.ext.webapp import blobstore_handlers
import functions


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        filename = self.request.get('file_name')

        file_object = functions.getFileList(filename)

        self.send_blob(file_object.blob)
