import mysql.connector


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


if __name__ == '__main__':
    """Connect to MySQL database."""
    cnx = connect_to_database()
    # get database tables
    cursor = cnx.cursor()
    cursor.execute("SHOW TABLES")
    for table in cursor:
        print(table)
