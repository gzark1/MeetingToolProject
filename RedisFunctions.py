import RedisConnection
import MeetingInstance

redis = RedisConnection.connect_to_redis()


def get_active_meeting_instances():
    active_meetings = []
    for key in redis.keys('*:status'):
        meeting_id, order_id = key.decode('utf-8').split(':')[:2]
        status = redis.get(key).decode('utf-8')
        if status == 'active':
            active_meetings.append(f"Meeting ID: {meeting_id}, Order ID: {order_id}")
            print(f"Meeting ID: {meeting_id}, Order ID: {order_id}")
    return active_meetings


print(get_active_meeting_instances())
