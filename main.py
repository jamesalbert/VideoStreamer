from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for,
    jsonify
)
from flask_security.decorators import login_required
from flask_security.core import current_user
from flask_security.utils import get_post_login_redirect
from flask.ext.social.utils import get_provider_or_404
from requests import post
from os.path import expanduser
from videostreamer import config
from videostreamer.db import VideoManager
from videostreamer.uploader import UploadManager
from videostreamer.utils import create_thumbnail, resize

"""app config"""
app = Flask(__name__)
config.prepare(app)
video_handler = VideoManager(app)
Videos = video_handler.Videos
User = video_handler.User
Role = video_handler.Role
uploader = UploadManager(app)

@app.route('/upload/image', methods=['POST'])
def upload_image():
    """
    uploads an image to the specified directory
    these images are used for thumbnails of videos
    """
    if 'image' in request.files:
        return jsonify(uploader.save_image(request.files['image']))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['desc']
        filename = request.form['filename']
        """save video"""
        #filename = uploader.save_video(request.files['video'])
        url, path = uploader.lookup_video(filename)
        """create thumbnail"""
        thumb_name = create_thumbnail(path, filename)
        """upload thumbnail"""
        image_payload = {'image': open(thumb_name, 'rb')}
        image_upload_uri = url_for('upload_image', _external=True)
        thumb = post(image_upload_uri, files=image_payload).json()
        resize(thumb['path'], image_upload_uri)
        """record upload"""
        video = Videos(filename=filename, rating=0,
                       user=current_user.email, views=0,
                       name=name, description=desc,
                       url=url, thumb=thumb['url'])
        video_handler.db.session.add(video)
        video_handler.db.session.commit()
        return url_for('video', video=filename)
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
        related_videos = Videos.query.order_by(Videos.rating)
        return render_template('index.html', logged_in=current_user.is_authenticated(), videos=related_videos)
    except Exception as e:
        print e.message

@app.route('/account')
@login_required
def account():
    videos = video_handler.get_videos(current_user.email)
    return render_template('account.html',
                           logged_in=current_user.is_authenticated(),
                           user=current_user,
                           requested_user=current_user,
                           videos=videos,
                           twitter_conn=video_handler.social.twitter.get_connection(),
                           facebook_conn=video_handler.social.facebook.get_connection())

@app.route('/account/<username>')
def other_account(username):
    requested_user = User.query.filter_by(email=username).first()
    videos = video_handler.get_videos(requested_user.email)
    user = None
    twitter_conn = None
    facebook_conn = None
    if current_user.is_authenticated():
        if current_user.email == requested_user.email:
            user = current_user
            twitter_conn = video_handler.social.twitter.get_connection()
            facebook_conn = video_handler.social.facebook.get_connection()
    return render_template('account.html',
                           logged_in=current_user.is_authenticated(),
                           requested_user=requested_user,
                           user=user,
                           videos=videos,
                           twitter_conn=twitter_conn,
                           facebook_conn=facebook_conn)

@app.route('/video/<video>')
def video(video):
    try:
        video_url = uploader.videos.url(video)
        video = Videos.query.filter_by(url=video_url).first()
        video.views += 1;
        video_handler.db.session.commit()
        username = video.user
        other_videos = video_handler.get_videos(username)
        return render_template('video.html',
                                video=video,
                                logged_in=current_user.is_authenticated(),
                                videos=other_videos)
    except Exception as e:
        print e.message

@app.route('/listings', methods=['POST'])
def listings():
    pay = request.form.to_dict()
    query = pay['query']
    return render_template('listings.html', query=query, logged_in=current_user.is_authenticated())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
