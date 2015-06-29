from ffvideo import VideoStream
from PIL import Image
from requests import post

pages = {
    'video': (231, 173),
    'account': (328, 246),
    'index': (260, 195)
}

def slurp_video(path):
    video = VideoStream(path)
    return video.get_frame_at_sec(2)

def snap_video(video):
    return video.image()

def create_thumbnail(path, filename):
    thumb_tmp_path = '/tmp/%s.jpeg' % filename
    video = slurp_video(path)
    thumb = snap_video(video)
    thumb.save(thumb_tmp_path)
    return thumb_tmp_path

def resize(image, upload_url):
    """
    resize an image

    image  (string) - path of image to be resized
    size   (set)    - resize dimensions
    append (string) - optional appended string of output
    """

    #if not isinstance(image, str) or not os.path.isfile(image):
    #    raise IOError('bad image path')
    try:
        filename = image.split('/')[-1]
        file_parts = filename.split('.')
        ext = file_parts.pop(-1)
        name = '.'.join(file_parts)
        for page, size in pages.iteritems():
            temp_outfile = '/tmp/%s_%s.%s' % (name, page, ext)
            im = Image.open(image)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(temp_outfile)
            image_payload = {'image': open(temp_outfile, 'rb')}
            thumb = post(upload_url, files=image_payload).json()
            thumb['url'], thumb['path']
    except IOError as e:
        print 'Could not resize image because: %s' % e.message
