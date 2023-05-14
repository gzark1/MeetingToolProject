import datetime
import time

import RedisConnection
import MeetingInstance
import redis
import threading
import DataBaseConnection

redis = RedisConnection.connect_to_redis()
database = DataBaseConnection.connect_to_database()


def get_active_meeting_instances():
    """Get all active meeting instances from redis
       return: list of MeetingInstance objects
    """
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


def create_channel_in_redis(channel):
    sub = redis.pubsub()
    sub.subscribe(channel)
    sub.parse_response()
    while True:
        for message in sub.listen():
            redis.rpush(channel + "_chat", message['data'])


def create_channel(channel):
    t = threading.Thread(target=create_channel_in_redis, args=(channel,))
    t.start()


def delete_all_meeting_instances():
    """Delete all meeting instances from redis"""
    for key in redis.keys('*:status'):
        redis.delete(key)
    print("All meetings deleted")


def update_event_log(user_email, event):
    """
    Update the event log in the database
    :param user_email: the user id
    :param event: the event type
    :return: None
    """
    cursor = database.cursor()
    if event != 'join_meeting' and event != 'leave_meeting' and event != 'time_out':
        return
    try:
        cursor.execute(f"SELECT userID FROM users WHERE email = '{user_email}'")
        result = cursor.fetchone()
        if result is not None:
            userId = result[0]
            cursor.execute(f"INSERT INTO eventsLog (userID, event_type) VALUES ({userId}, '{event}')")
            database.commit()
        else:
            print("User not found")
    except Exception as e:
        print(e)
    cursor.close()


def join_meeting(meeting, email):
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting Instance not found")
        return
    if redis.get(f'{meeting_id}:public') is None:
        print("Meeting not found")
        return
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'active':
        if redis.get(f'{meeting_id}:public').decode('utf-8') == 'true':
            redis.sadd(f'{meeting_id}:{order_id}:connected_users', email)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            redis.set(f'{meeting_id}:{order_id}:{email}:timestamp', timestamp)
            subscriber = redis.pubsub()
            subscriber.subscribe(f'{meeting_id}:{order_id}:channel')
            update_event_log(email, 'join_meeting')
        else:
            if redis.sismember(f'{meeting_id}:audience', email):
                redis.sadd(f'{meeting_id}:{order_id}:connected_users', email)
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                redis.set(f'{meeting_id}:{order_id}:{email}:timestamp', timestamp)
                subscriber = redis.pubsub()
                subscriber.subscribe(f'{meeting_id}:{order_id}:channel')
                update_event_log(email, 'join_meeting')
            else:
                print("You are not allowed to join this meeting")
    else:
        print("Meeting is not active")


def leave_meeting(meeting, user_email):
    """"""
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting not found")
        return
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'active':
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
        users = redis.smembers(f'{meeting_id}:{order_id}:connected_users')
        if len(users) == 0:
            print("No users in the meeting")
        else:
            for user_email in users:
                print(f"User Email: {user_email.decode('utf-8')}")
    else:
        print("Meeting is not active")


def show_meeting_current_users_with_timestamp(meeting):
    """ Show all users in the meeting """
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting not found")
        return
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'active':
        users = redis.smembers(f'{meeting_id}:{order_id}:connected_users')
        if len(users) == 0:
            print("No users in the meeting")
        else:
            for user_email in redis.smembers(f'{meeting_id}:{order_id}:connected_users'):
                user_email = user_email.decode('utf-8')
                print(
                    f"User Email: {user_email}, Timestamp: {redis.get(f'{meeting_id}:{order_id}:{user_email}:timestamp').decode('utf-8')}")
    else:
        print("Meeting is not active")


def post_message(user_email, meeting, message):
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting not found")
        return
    if redis.get(f'{meeting_id}:{order_id}:status').decode('utf-8') == 'active':
        if redis.get(f'{meeting_id}:public').decode('utf-8') == 'true':
            redis.publish(f'{meeting_id}:{order_id}:channel',
                          f'User:{user_email} Message: {message} Timestamp: {datetime.datetime.now()}')
        else:
            if redis.sismember(f'{meeting_id}:audience', user_email):
                redis.publish(f'{meeting_id}:{order_id}:channel',
                              f'User:{user_email} Message: {message} Timestamp: {datetime.datetime.now()}')
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
        cursor = database.cursor()
        for user_email in redis.smembers(f'{meeting_id}:{order_id}:connected_users'):
            redis.delete(f'{meeting_id}:{order_id}:{user_email}:timestamp')
            cursor.execute(f"SELECT userID FROM users WHERE email='{user_email}'")
            user_id = cursor.fetchone()[0]
            if user_id is not None:
                update_event_log(user_email, 'timeout')
            else:
                print("User not found")
    else:
        print("Meeting is active users cannot be deleted")


def show_meeting_chat_in_cronological_order(meeting):
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting not found")
        return
    chat = redis.lrange(f'{meeting_id}:{order_id}:channel_chat', 0, -1)
    for message in chat:
        print(message.decode('utf-8'))


def show_meeting_chat_of_a_user(meeting, user_email):
    meeting_id, order_id = meeting.meetingId, meeting.orderId
    if redis.get(f'{meeting_id}:{order_id}:status') is None:
        print("Meeting not found")
        return
    chat = redis.lrange(f'{meeting_id}:{order_id}:channel_chat', 0, -1)
    for message in chat:
        if f'User:{user_email}' in message.decode('utf-8'):
            print(message.decode('utf-8'))
