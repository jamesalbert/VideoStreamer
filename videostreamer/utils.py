from ffvideo import VideoStream

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
