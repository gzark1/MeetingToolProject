import time

from Channel import Channel
import DataBaseConnection
import RedisConnection
import MeetingInstance
import datetime
import RedisFunctions


def add_meeting_details(meetingInstance):
    """Add meeting details to redis
    :param meetingInstance: MeetingInstance object
    :return: None
    """
    redis = RedisConnection.connect_to_redis()
    meetingId = meetingInstance.meetingId
    con = DataBaseConnection.check_connection()
    if con is None:
        con = DataBaseConnection.connect_to_database()
    cursor = con.cursor()
    cursor.execute("SELECT isPublic, audience FROM meetings WHERE meetingID = %s", (meetingId,))
    isPublic, audience = cursor.fetchone()
    audience = audience.split(',')
    cursor.close()
    if isPublic == 1:
        redis.set(f'{meetingId}:public', 'true')
    else:
        redis.set(f'{meetingId}:public', 'false')
        # Add audience to redis, for now it is hardcoded
        redis.sadd(f'{meetingId}:audience', *audience)


class Scheduler:
    meeting_instances = []
    channels = {}
    redis = RedisConnection.connect_to_redis()
    con = DataBaseConnection.connect_to_database()

    def get_last_minute_updated_meetings(self, ):
        con = DataBaseConnection.check_connection()
        if con is None:
            con = DataBaseConnection.connect_to_database()
        cursor = con.cursor()
        cursor.execute(
            "SELECT meetingID, orderID, fromdatetime, todatetime FROM meeting_instances "
            "WHERE created_at >= NOW() - INTERVAL 1 MINUTE AND created_at < NOW()")
        meetings = cursor.fetchall()
        cursor.close()
        meetingInstaces = []
        for meeting in meetings:
            meetingID, orderID, fromdatetime, todatetime = meeting
            meet = MeetingInstance.MeetingInstance(meetingID, orderID, fromdatetime, todatetime)
            meetingInstaces.append(meet)
            if self.redis.get(f'{meetingID}:{orderID}:status') is None:
                self.redis.set(f'{meetingID}:{orderID}:status', 'inactive')
                add_meeting_details(meet)
        return meetingInstaces

    def activate_meetings(self):
        # get all meeting instances with start time less than or equal to current time
        current_time = datetime.datetime.now()
        meetingsInstances = self.meeting_instances
        for meetingInstance in meetingsInstances:
            meetingID, orderID = meetingInstance.meetingId, meetingInstance.orderId
            # set meeting instance status to "active"
            if meetingInstance.fromdatatime <= current_time <= meetingInstance.todatetime:
                status = self.redis.get(f'{meetingID}:{orderID}:status')
                RedisFunctions.create_channel(f'{meetingID}:{orderID}:channel')
                if status.decode('utf-8') != "active":
                    self.redis.set(f'{meetingID}:{orderID}:status', 'active')

    def deactivate_meetings(self):
        # get all meeting instances with end time less than or equal to current time
        current_time = datetime.datetime.now()
        meetingsInstances = self.meeting_instances
        redis = RedisConnection.connect_to_redis()
        for meetingInstance in meetingsInstances:
            meetingID, orderID = meetingInstance.meetingId, meetingInstance.orderId
            # set meeting instance status to "inactive"
            if meetingInstance.todatetime <= current_time:
                status = redis.get(f'{meetingID}:{orderID}:status')
                if status.decode('utf-8') != "inactive":
                    redis.set(f'{meetingID}:{orderID}:status', 'inactive')
                    RedisFunctions.delete_current_users_at_meeting_end(meetingInstance)

    def run(self):
        """Run the scheduler"""
        # Add all meetings to redis when the scheduler starts
        self.meeting_instances = self.get_all_meetings_instances()
        self.activate_meetings()
        self.deactivate_meetings()
        # run the scheduler every 1 minute to check for new meetings
        while True:
            self.meeting_instances = self.get_last_minute_updated_meetings()
            self.activate_meetings()
            self.deactivate_meetings()
            time.sleep(2)

    def get_all_meetings_instances(self):
        """Get all meeting instances from database
        :return: list of MeetingInstance objects
        """
        con = DataBaseConnection.check_connection()
        if con is None:
            con = DataBaseConnection.connect_to_database()
        cursor = con.cursor()
        cursor.execute(
            "SELECT meetingID, orderID, fromdatetime, todatetime FROM meeting_instances")
        meetings = cursor.fetchall()
        cursor.close()
        meetingInstaces = []
        for meeting in meetings:
            meetingID, orderID, fromdatetime, todatetime = meeting
            meet = MeetingInstance.MeetingInstance(meetingID, orderID, fromdatetime, todatetime)
            meetingInstaces.append(meet)
            if self.redis.get(f'{meetingID}:{orderID}:status') is None:
                self.redis.set(f'{meetingID}:{orderID}:status', 'inactive')
                add_meeting_details(meet)
        return meetingInstaces


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.run()
