import RedisConnection
import MeetingInstance
import redis
import threading
import DataBaseConnection

redis = RedisConnection.connect_to_redis()
database = DataBaseConnection.connect_to_database()


def get_active_meeting_instances():
    active_meetings = []
    for key in redis.keys('*:status'):
        meeting_id, order_id = key.decode('utf-8').split(':')[:2]
        status = redis.get(key).decode('utf-8')
        if status == 'active':
            active_meetings.append(f"Meeting ID: {meeting_id}, Order ID: {order_id}")
            print(f"Meeting ID: {meeting_id}, Order ID: {order_id}")
    return active_meetings


def delete_all_meeting_instances():
    for key in redis.keys('*:status'):
        redis.delete(key)


def update_event_log(userId, event):
    cursor = database.cursor()
    if event != 'join_meeting' and event != 'leave_meeting' and event != 'time_out':
        return
    try:
        cursor.execute(f"INSERT INTO eventsLog (userID, event_type) VALUES ({userId}, '{event}')")
        database.commit()
    except Exception as e:
        print(e)
    cursor.close()


def create_channel_in_redis(channel):
    sub = redis.pubsub()
    sub.subscribe(channel)
    while True:
        for message in sub.listen():
            pass


def create_channel(channel):
    t = threading.Thread(target=create_channel_in_redis, args=(channel,))
    t.start()


def join_meeting(user, meeting):
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'active':
        if redis.get(f'{meeting_id}:public').decode('utf-8') == 'true':
            redis.sadd(f'{meeting_id}:{order_id}:connected_users', user.userId)
            subscriber = redis.pubsub()
            subscriber.subscribe(f'channel_{order_id}')
            update_event_log(user.userId, 'join_meeting')
        else:
            if redis.sismember(f'{meeting_id}:audience', user.userId):
                redis.sadd(f'{meeting_id}:{order_id}:connected_users', user.userId)
                subscriber = redis.pubsub()
                subscriber.subscribe(f'channel_{order_id}')
                update_event_log(user.userId, 'join_meeting')
            else:
                print("You are not allowed to join this meeting")
    else:
        print("Meeting is not active")

