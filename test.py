import User
import MeetingInstance
import Meeting
import RedisFunctions
import RedisConnection
import DataBaseConnection


redis = RedisConnection.connect_to_redis()
def create_channel_in_redis(channel):
    sub = redis.pubsub()
    sub.subscribe(channel)
    sub.parse_response()
    while True:
        for message in sub.listen():
            redis.rpush(channel+"_chat", message['data'])


create_channel_in_redis("1:69:channel")