class MeetingInstance:
    def __init__(self, meetingId, orderId, fromdatatime, todatetime):
        self.meetingId = meetingId
        self.orderId = orderId
        self.fromdatatime = fromdatatime
        self.todatetime = todatetime

    def __str__(self):
        return "MeetingInstance: " + str(self.meetingId) + " " + str(self.orderId) + " " + str(self.fromdatatime) + " " + str(self.todatetime)