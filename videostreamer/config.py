from flask_peewee.db import Database
from os.path import expanduser

def prepare(app):
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
    app.config['UPLOADED_VIDEOS_DEST'] = '/var/opt/videos'
    app.config['UPLOADED_IMAGES_DEST'] = '/var/opt/images'

def prepare_db_model(app):
    DATABASE = {
        'name': 'jcannon87',
        'engine': 'peewee.MySQLDatabase',
        'user': 'root'
    }
    app.config['DATABASE'] = DATABASE
    app.config.from_object(__name__)
    return Database(app).Model
