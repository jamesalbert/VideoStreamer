from flask import Flask, render_template, request, send_file, redirect, url_for
from flask_stormpath import StormpathManager, user, login_required
from flask_peewee.db import Database
from flask.ext.uploads import UploadSet, configure_uploads
from stormpath.client import Client
from requests import post
from peewee import *
from ffvideo import VideoStream
from os.path import expanduser

"""app config"""
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ooohprivate'
app.config['STORMPATH_API_KEY_FILE'] = expanduser('~/.stormpath/apiKey.properties')
app.config['STORMPATH_APPLICATION'] = 'VideoStreamer'
app.config['STORMPATH_ENABLE_FACEBOOK'] = True
app.config['STORMPATH_ENABLE_GOOGLE'] = True
app.config['STORMPATH_SOCIAL'] = {
    'FACEBOOK': {
        'app_id': '1601277736801081',
        'app_secret': '55aec8cd54286dbe7ab85d541955f55f',
    },
    'GOOGLE': {
        'client_id': '364228911271-99ep9ssr6ci8q221gtn5fbah11cmdop5.apps.googleusercontent.com',
        'client_secret': 'XsyRPxOuHAp8tDDtSCZNI1gv',
    }
}

spm = StormpathManager(app)
cli = Client(api_key_file_location=app.config['STORMPATH_API_KEY_FILE'])
app_ref = cli.applications.search('VideoStreamer')[0]

"""database config"""
DATABASE = {
    'name': 'jcannon87',
    'engine': 'peewee.MySQLDatabase',
    'user': 'root'
}
app.config.from_object(__name__)
db = Database(app)

class Videos(db.Model):
    filename = CharField()
    name = CharField()
    rating = IntegerField()
    url = CharField()
    user = CharField()
    views = IntegerField()
    description = CharField()
    thumb = CharField()

    class Meta:
        db_table = 'Videos'


"""upload config"""
app.config['UPLOADED_VIDEOS_DEST'] = '/var/opt/videos'
app.config['UPLOADED_IMAGES_DEST'] = '/var/opt/images'
videos = UploadSet('videos', ('mp4',))
images = UploadSet('images', ('jpeg',))
configure_uploads(app, (videos,images,))

@app.route('/upload/image', methods=['POST'])
def upload_image():
    if 'image' in request.files:
        """save thumbnail"""
        filename = images.save(request.files['image'])
        url = images.url(filename)
        return url

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST' and 'video' in request.files:
        name = request.form['name']
        desc = request.form['desc']
        """save video"""
        filename = videos.save(request.files['video'])
        url = videos.url(filename)
        path = videos.path(filename)
        """create thumbnail"""
        thumb_name = '/tmp/%s.jpeg' % filename
        VideoStream(path).get_frame_at_sec(2).image().save(thumb_name)
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
    related_videos = []
    videos_query = Videos.select().where(Videos.user == user.email).execute()
    for video in videos_query:
        related_videos.append(video)
    return render_template('account.html', logged_in=True, user=user, videos=related_videos)

@app.route('/account/<username>')
def other_account(username):
    requested_user = app_ref.accounts.search({'email': username})[0]
    related_videos = []
    videos_query = Videos.select().where(Videos.user == requested_user.email).execute()
    for video in videos_query:
        related_videos.append(video)
    return render_template('account.html', logged_in=hasattr(user, 'email'), user=requested_user, videos=related_videos)

@app.route('/video/<video>')
def video(video):
    try:
        video_url = videos.url(video)
        video_rec = Videos.get(Videos.url == video_url)
        username = video_rec.user
        print username
        related_videos = []
        video_query = Videos.select().where(Videos.user == username).execute()
        for video in video_query:
            related_videos.append(video)
        print related_videos
        return render_template('video.html',
                                video_rec=video_rec,
                                logged_in=hasattr(user, 'email'),
                                videos=related_videos)
    except Exception as e:
        print e.message

@app.route('/listings', methods=['POST'])
def listings():
    pay = request.form.to_dict()
    query = pay['query']
    return render_template('listings.html', query=query, logged_in=hasattr(user, 'email'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
