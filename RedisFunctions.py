import RedisConnection
import MeetingInstance
import redis
import threading

# Connect to Redis
redis = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)# redis = RedisConnection.connect_to_redis()


def get_active_meeting_instances():
    active_meetings = []
    for key in redis.keys('*:status'):
        meeting_id, order_id = key.decode('utf-8').split(':')[:2]
        status = redis.get(key).decode('utf-8')
        if status == 'active':
            active_meetings.append(f"Meeting ID: {meeting_id}, Order ID: {order_id}")
            #print(f"Meeting ID: {meeting_id}, Order ID: {order_id}")
    return active_meetings

def pubsubtest():
    #answer = redis.pubsub()
    redis.publish('mychannel', 'hello')
    print(redis.pubsub_channels()[0].decode('utf-8'))


# redis.publish('newchannel', "opening meeting")
sub = redis.pubsub()


l = ["channel1", "channel2", "channel3", "channel4", "channel5"]
def create_channel(ch):
    sub = redis.pubsub()
    sub.subscribe(ch)
    while True:
        for message in sub.listen():
            pass

for ch in l:
    t = threading.Thread(target=create_channel, args=(ch,))
    t.start()

# pubsubtest2()
# pubsubtest()
# print(get_active_meeting_instances())
