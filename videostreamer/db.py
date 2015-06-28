from config import prepare_db_model
from peewee import *

class VideoManager(object):
    def __init__(self, app):
        model = prepare_db_model(app)
        class Videos(model):
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
        self.Videos = Videos

    def get_videos(self, username):
        videos = []
        videos_query = self.Videos.select()\
                                  .where(self.Videos.user == username)\
                                  .execute()
        for video_result in videos_query:
            videos.append(video_result)
        return videos
