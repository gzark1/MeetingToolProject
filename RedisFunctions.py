import datetime

import RedisConnection
import MeetingInstance
import redis
import threading
import DataBaseConnection

redis = RedisConnection.connect_to_redis()
database = DataBaseConnection.connect_to_database()


def get_active_meeting_instances():
    active_meetings = []
    i = 0
    for key in redis.keys('*:status'):
        i += 1
        meeting_id, order_id = key.decode('utf-8').split(':')[:2]
        status = redis.get(key).decode('utf-8')
        if status == 'active':
            active_meetings.append(f"Meeting ID: {meeting_id}, Order ID: {order_id}")
            print(f"Meeting ID: {meeting_id}, Order ID: {order_id}")
    if i == 0:
        print("No active meetings")
    return active_meetings


def delete_all_meeting_instances():
    for key in redis.keys('*:status'):
        redis.delete(key)
    print("All meetings deleted")


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


def join_meeting(meeting, user):
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting Instance not found")
        return
    if redis.get(f'{meeting_id}:public') is None:
        print("Meeting not found")
        return
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'active':
        user_email = user.email
        if redis.get(f'{meeting_id}:public').decode('utf-8') == 'true':
            redis.sadd(f'{meeting_id}:{order_id}:connected_users', user_email)
            timestamp = datetime.datetime.now()
            redis.set(f'{meeting_id}:{order_id}:{user_email}:timestamp', timestamp)
            subscriber = redis.pubsub()
            subscriber.subscribe(f'{meeting_id}:{order_id}:channel')
            update_event_log(user_email, 'join_meeting')
        else:
            if redis.sismember(f'{meeting_id}:audience', user_email):
                redis.sadd(f'{meeting_id}:{order_id}:connected_users', user_email)
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                redis.set(f'{meeting_id}:{order_id}:{user_email}:timestamp', timestamp)
                subscriber = redis.pubsub()
                subscriber.subscribe(f'{meeting_id}:{order_id}:channel')
                update_event_log(user_email, 'join_meeting')
            else:
                print("You are not allowed to join this meeting")
    else:
        print("Meeting is not active")


def leave_meeting(meeting, user):
    """"""
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting not found")
        return
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'active':
        user_email = user.email
        if redis.get(f'{meeting_id}:public').decode('utf-8') == 'true':
            redis.srem(f'{meeting_id}:{order_id}:connected_users', user_email)
            update_event_log(user_email, 'leave_meeting')
        else:
            if redis.sismember(f'{meeting_id}:audience', user_email):
                redis.srem(f'{meeting_id}:{order_id}:connected_users', user_email)
                update_event_log(user_email, 'leave_meeting')
            else:
                print("You are not allowed to leave this meeting because you are not in the audience")
    else:
        print("Meeting is not active")


def show_meeting_current_users(meeting):
    """ Show all users in the meeting """
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting not found")
        return
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'active':
        print(redis.smembers(f'{meeting_id}:{order_id}:connected_users'))
    else:
        print("Meeting is not active")


def show_meeting_current_users_with_timestamp(meeting):
    """ Show all users in the meeting """
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting not found")
        return
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'active':
        for user_email in redis.smembers(f'{meeting_id}:{order_id}:connected_users'):
            user_email = user_email.decode('utf-8')
            print(
                f"User Email: {user_email}, Timestamp: {redis.get(f'{meeting_id}:{order_id}:{user_email}:timestamp').decode('utf-8')}")
    else:
        print("Meeting is not active")


def post_message(user, meeting, message):
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting not found")
        return
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'active':
        user_email = user.email
        if redis.get(f'{meeting_id}:public').decode('utf-8') == 'true':
            redis.publish(f'{meeting_id}:{order_id}:channel', f'{user_email}: {message}')
        else:
            if redis.sismember(f'{meeting_id}:audience', user_email):
                redis.publish(f'{meeting_id}:{order_id}:channel', f'{user_email}: {message}')
            else:
                print("You are not allowed to post message in this meeting")
    else:
        print("Meeting is not active")


def delete_current_users_at_meeting_end(meeting):
    """ Delete all users in the meeting """
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting not found")
        return
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'inactive':
        redis.delete(f'{meeting_id}:{order_id}:connected_users')
    else:
        print("Meeting is active users cannot be deleted")
