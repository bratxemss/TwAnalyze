from uuid import uuid4
import peewee as pw
from peewee_aio.model import AIOModel
from . import db


@db.register
class Customer(AIOModel):
    user_login = pw.CharField(unique=True)
    user_description = pw.CharField(null=True)

    def __repr__(self):
        return f"<Customer: {self.telegram_id}>"

    @classmethod
    async def create_with_user_login(cls, user_login, user_description):
        return await cls.create(
            user_login=user_login,
            user_description=user_description,
        )

    @classmethod
    async def get_description_by_user(cls, user_login):
        try:
            user = await cls.select().where(cls.user_login == user_login)
            return [{
                "login": data.user_login,
                "description": data.user_description,
            } for data in user]

        except cls.DoesNotExist:
            return None



@db.register
class Tweet(AIOModel):
    Tweet_sender = pw.ForeignKeyField(Customer, to_field=Customer.user_login)
    Tweet_text = pw.CharField(null=True)
    Tweet_comments = pw.IntegerField(default=0)
    Tweet_reposts = pw.IntegerField(default=0)
    Tweet_likes = pw.IntegerField(default=0)
    Tweet_views = pw.IntegerField(default=0)

    def __repr__(self):
        return f"<Tweet: {self.id}, {self.Tweet_sender}, {self.Tweet_text}>"

    @classmethod
    async def get_tweets_by_sender(cls, user):
        user_tweets = await cls.select().where(
            cls.Tweet_sender == user
        )
        return [
            {
                "id": tweet.id,
                "Tweet_text": tweet.Tweet_text,
                "Tweet_comments": tweet.Tweet_comments,
                "Tweet_reposts": tweet.Tweet_reposts,
                "Tweet_likes": tweet.Tweet_likes,
                "Tweet_views": tweet.Tweet_views
            }
            for tweet in user_tweets
        ]

    @classmethod
    async def check_tweet_by_text(cls,user,text):
        return await cls.get_or_none(
            Tweet_sender=user,
            Tweet_text=text,
        )



