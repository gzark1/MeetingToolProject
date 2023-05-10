import mysql.connector

from MeetingInstance import MeetingInstance


# Connect to MySQL on localhost


def connect_to_database():
    """Connect to a MySQL database."""
    cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="test123@!Aabvhj",
        database="test_schema"
    )
    return cnx


def check_connection():
    """Check connection to MySQL database."""
    connection = connect_to_database()
    if connection.is_connected():
        return connection
    else:
        return None


def get_meetings_by_from_time():
    con = check_connection()
    if con is None:
        con = connect_to_database()
    cursor = con.cursor()
    cursor.execute(
        "SELECT meetingID, orderID, fromdatetime, todatetime FROM meeting_instances "
        "WHERE created_at >= NOW() - INTERVAL 1 MINUTE AND created_at < NOW() AND"
        "  fromdatetime <= NOW()")
    meetings = cursor.fetchall()
    cursor.close()
    meetingInstaces = []
    for meeting in meetings:
        meetingID, orderID, fromdatetime, todatetime = meeting
        meet = MeetingInstance(meetingID, orderID, fromdatetime, todatetime)
        meetingInstaces.append(meet)
    return meetingInstaces

def get_meetings_by_to_time():
    con = check_connection()
    if con is None:
        con = connect_to_database()
    cursor = con.cursor()
    cursor.execute(
        "SELECT meetingID, orderID, fromdatetime, todatetime FROM meeting_instances"
        " WHERE todatetime <= NOW()")
    meetings = cursor.fetchall()
    cursor.close()
    meetingInstaces = []
    for meeting in meetings:
        meetingID, orderID, fromdatetime, todatetime = meeting
        meet = MeetingInstance(meetingID, orderID, fromdatetime, todatetime)
        meetingInstaces.append(meet)
    return meetingInstaces


if __name__ == '__main__':
    meetings = get_meetings_by_from_time('2023-05-10 09:00:00')
    for meeting in meetings:
        print(meeting)
