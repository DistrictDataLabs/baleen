from flask import Flask
from flask_admin import Admin
from flask_mongoengine import MongoEngine
from flask_admin.contrib.pymongo import ModelView
import baleen.models as db
app = Flask(__name__)
app.debug = True
app.config['MONGODB_SETTINGS'] = {'DB': 'baleen', "HOST": "mongo"}

me_db = MongoEngine()
me_db.init_app(app)

# admin = Admin(app)
#
# class JobView(ModelView):
#     column_filters = ['name']
#
# admin.add_view(JobView(db.Job, name="job", endpoint="job"))

@app.route("/")
def index():
    db.connect()
    feeds = db.Feed.objects()
    feed_count = feeds.count()
    feeds_topics_count = len(set([feed.category for feed in feeds]))
    import pdb; pdb.set_trace()

    return """{feed_count} feeds in {topic_count} topics""".format(feed_count=feed_count, topic_count=feeds_topics_count)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
