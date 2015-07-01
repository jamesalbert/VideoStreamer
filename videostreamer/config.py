from flask_peewee.db import Database
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mobility import Mobility
from os.path import expanduser

def prepare(app):
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/jcannon87'
    app.config['SECRET_KEY'] = 'ooohprivate'
    app.config['SOCIAL_TWITTER'] = {
        'consumer_key': 'udsNQPoI0NpJnlhVd5XIzqhvF',
        'consumer_secret': 'gRPh3NYuLSepMOQcuAFS0AvYUZAbFLYRxU5umoaS28LotJFMaw'
    }
    app.config['SOCIAL_FACEBOOK'] = {
        'consumer_key': '1601277736801081',
        'consumer_secret': '55aec8cd54286dbe7ab85d541955f55f'
    }
    '''
    app.config['SOCIAL_FOURSQUARE'] = {
        'consumer_key': 'client id',
        'consumer_secret': 'client secret'
    }
    app.config['SOCIAL_GOOGLE'] = {
        'consumer_key': '364228911271-99ep9ssr6ci8q221gtn5fbah11cmdop5.apps.googleusercontent.com',
        'consumer_secret': 'XsyRPxOuHAp8tDDtSCZNI1gv'
    }
    '''
    #app.config['SECURITY_LOGIN_URL'] = '/mylogin'
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    app.config['SECURITY_PASSWORD_SALT'] = 'sneaky'
    app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['UPLOADED_VIDEOS_DEST'] = '/var/www/VideoStreamer/upload'
    app.config['UPLOADED_IMAGES_DEST'] = '/var/opt/images'
    Mobility(app)

def prepare_db_model(app):
    '''
    DATABASE = {
        'name': 'jcannon87',
        'engine': 'peewee.MySQLDatabase',
        'user': 'root'
    }
    app.config['DATABASE'] = DATABASE
    app.config.from_object(__name__)
    return Database(app)
    '''
    return SQLAlchemy(app)
