import time
import DataBaseConnection
import RedisConnection
import MeetingInstance
import datetime

class Scheduler:
    meeting_instances = []
    def get_last_minute_updated_meetings(self,):
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
        return meetingInstaces
    def activate_meetings(self):
        # get all meeting instances with start time less than or equal to current time
        current_time = datetime.datetime.now()
        meetingsInstances = self.meeting_instances
        redis = RedisConnection.connect_to_redis()
        for meetingInstance in meetingsInstances:
            meetingID, orderID = meetingInstance.meetingId, meetingInstance.orderId
            # set meeting instance status to "active"
            if meetingInstance.fromdatatime <= current_time:
                if not(redis.exists(f'{meetingID}:{orderID}:status', 'active')):
                    redis.set(f'{meetingID}:{orderID}:status', 'active')
                    print("Add to redis "
                        "" + redis.get(f'{meetingID}:{orderID}:status').decode('utf-8'))


    def deactivate_meetings(self):
        # get all meeting instances with end time less than or equal to current time
        current_time = datetime.datetime.now()
        meetingsInstances = self.meeting_instances
        redis = RedisConnection.connect_to_redis()
        for meetingInstance in meetingsInstances:
            meetingID, orderID = meetingInstance.meetingId, meetingInstance.orderId
            # set meeting instance status to "inactive"
            if meetingInstance.todatetime <= current_time:
                print(not (redis.exists(f'{meetingID}:{orderID}:status', 'inactive')))

                if redis.exists(f'{meetingID}:{orderID}:status', 'active'):
                    redis.set(f'{meetingID}:{orderID}:status', 'inactive')
                    print("Add to redis "
                          "" + redis.get(f'{meetingID}:{orderID}:status').decode('utf-8'))
    def getallmeetings(self):
        redis = RedisConnection.connect_to_redis()
        keys = redis.keys()
        for key in keys:
            print(key.decode('utf-8') + " " + redis.get(key).decode('utf-8'))
    def run(self):
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
        return meetingInstaces


sc = Scheduler()
sc.run()


