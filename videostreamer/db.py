from config import prepare_db_model
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin
from flask_security.forms import RegisterForm, Required, TextField
from flask.ext.social import Social
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore

class VideoManager(object):
    def __init__(self, app):
        self.db = prepare_db_model(app)
        self.model = self.db.Model
        class Videos(self.model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            filename = self.db.Column(self.db.String(2083))
            name = self.db.Column(self.db.String(255))
            rating = self.db.Column(self.db.Integer)
            url = self.db.Column(self.db.String(2083))
            user = self.db.Column(self.db.String(50))
            views = self.db.Column(self.db.Integer)
            description = self.db.Column(self.db.Text)
            thumb = self.db.Column(self.db.String(2083))

            def __init__(self,
                         filename,
                         name,
                         rating,
                         url,
                         user,
                         views,
                         description,
                         thumb):
                self.filename = filename
                self.name = name
                self.rating = rating
                self.url = url
                self.user = user
                self.views = views
                self.description = description
                self.thumb = thumb

        roles_users = self.db.Table('roles_users',
            self.db.Column('user_id', self.db.Integer(), self.db.ForeignKey('user.id')),
            self.db.Column('role_id', self.db.Integer(), self.db.ForeignKey('role.id')))

        class Role(self.model, RoleMixin):
            id = self.db.Column(self.db.Integer(), primary_key=True)
            name = self.db.Column(self.db.String(80), unique=True)
            description = self.db.Column(self.db.String(255))

        class User(self.model, UserMixin):
            id = self.db.Column(self.db.Integer, primary_key=True)
            email = self.db.Column(self.db.String(255), unique=True)
            password = self.db.Column(self.db.String(255))
            first_name = self.db.Column(self.db.String(255))
            last_name = self.db.Column(self.db.String(255))
            active = self.db.Column(self.db.Boolean())
            roles = self.db.relationship('Role', secondary=roles_users,
                                    backref=self.db.backref('users', lazy='dynamic'))

        class Connection(self.model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            user_id = self.db.Column(self.db.Integer, self.db.ForeignKey('user.id'))
            provider_id = self.db.Column(self.db.String(255))
            provider_user_id = self.db.Column(self.db.String(255))
            access_token = self.db.Column(self.db.String(255))
            secret = self.db.Column(self.db.String(255))
            display_name = self.db.Column(self.db.String(255))
            full_name = self.db.Column(self.db.String(255))
            user = self.db.relationship('User')
            profile_url = self.db.Column(self.db.String(512))
            image_url = self.db.Column(self.db.String(512))
            rank = self.db.Column(self.db.Integer)

        class ExtendedRegisterForm(RegisterForm):
            first_name = TextField('First Name', [Required()])
            last_name = TextField('Last Name', [Required()])

        self.Videos = Videos
        self.Role = Role
        self.User = User
        self.Connectin = Connection
        self.datastore = SQLAlchemyUserDatastore(self.db, User, Role)
        self.connstore = SQLAlchemyConnectionDatastore(self.db, Connection)
        self.security = Security(app, self.datastore, register_form=ExtendedRegisterForm)
        self.social = Social(app, self.connstore)

    def get_videos(self, username):
        videos = []
        videos = self.Videos.query.filter_by(user=username)
        return videos
