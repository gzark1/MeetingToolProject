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



