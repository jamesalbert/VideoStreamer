from flask import Flask, render_template, request, send_file, redirect, url_for
from flask_stormpath import StormpathManager, user, login_required
from stormpath.client import Client
from requests import post
from os.path import expanduser
from videostreamer import config
from videostreamer.db import VideoManager
from videostreamer.uploader import UploadManager
from videostreamer.utils import create_thumbnail

"""app config"""
app = Flask(__name__)
config.prepare(app)
StormpathManager(app)
cli = Client(api_key_file_location=app.config['STORMPATH_API_KEY_FILE'])
app_ref = cli.applications.search('VideoStreamer')[0]
video_handler = VideoManager(app)
Videos = video_handler.Videos
uploader = UploadManager(app)

@app.route('/upload/image', methods=['POST'])
def upload_image():
    """
    uploads an image to the specified directory
    these images are used for thumbnails of videos
    """
    if 'image' in request.files:
        return uploader.save_image(request.files['image'])

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST' and 'video' in request.files:
        name = request.form['name']
        desc = request.form['desc']
        """save video"""
        filename = uploader.save_video(request.files['video'])
        url, path = uploader.lookup_video(filename)
        """create thumbnail"""
        thumb_name = create_thumbnail(path, filename)
        """upload thumbnail"""
        image_payload = {'image': open(thumb_name, 'rb')}
        image_upload_uri = url_for('upload_image', _external=True)
        thumb_url = post(image_upload_uri, files=image_payload).text
        """record upload"""
        Videos.create(filename=filename, rating=0,
                      user=user.email, views=0,
                      name=name, description=desc,
                      url=url, thumb=thumb_url)
        return redirect(url_for('video', video=filename))
    return render_template('upload.html')

"""error handling"""
@app.errorhandler(500)
def server_error(e):
    return e.message

@app.errorhandler(400)
def server_error(e):
    return e.message

@app.route('/')
def front():
    try:
        related_videos = []
        videos_query = Videos.select().order_by(Videos.views.desc())
        for video in videos_query:
            related_videos.append(video)
        return render_template('index.html', logged_in=hasattr(user, 'email'), videos=related_videos)
    except Exception as e:
        print e.message

@app.route('/account')
@login_required
def account():
    videos = video_handler.get_videos(user.email)
    return render_template('account.html', logged_in=True, user=user, videos=videos)

@app.route('/account/<username>')
def other_account(username):
    requested_user = app_ref.accounts.search({'email': username})[0]
    videos = video_handler.get_videos(requested_user.email)
    return render_template('account.html', logged_in=hasattr(user, 'email'), user=requested_user, videos=videos)

@app.route('/video/<video>')
def video(video):
    try:
        video_url = uploader.videos.url(video)
        video = Videos.get(Videos.url == video_url)
        username = video.user
        other_videos = video_handler.get_videos(username)
        return render_template('video.html',
                                video=video,
                                logged_in=hasattr(user, 'email'),
                                videos=other_videos)
    except Exception as e:
        print e.message

@app.route('/listings', methods=['POST'])
def listings():
    pay = request.form.to_dict()
    query = pay['query']
    return render_template('listings.html', query=query, logged_in=hasattr(user, 'email'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
