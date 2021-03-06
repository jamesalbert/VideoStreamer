from flask.ext.uploads import UploadSet, configure_uploads

class UploadManager(object):
    def __init__(self, app):
        self.videos = UploadSet('videos', ('mp4','webm','wmv','avi','mov',))
        self.images = UploadSet('images', ('jpeg',))
        configure_uploads(app, (self.videos,self.images,))

    def save_image(self, image):
        filename = self.images.save(image)
        return {
            'url': self.images.url(filename),
            'path': self.images.path(filename)
        }

    def save_video(self, video):
        filename = self.videos.save(video)
        return filename

    def lookup_video(self, filename):
        url = self.videos.url(filename)
        path = self.videos.path(filename)
        return url, path
