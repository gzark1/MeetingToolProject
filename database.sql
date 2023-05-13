CREATE DATABASE mydatabase;

USE mydatabase;

CREATE TABLE users (
  userID INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  age INT,
  gender ENUM('Male', 'Female', 'Other'),
  email VARCHAR(50),
  PRIMARY KEY (userID)
);

CREATE TABLE meetings (
  meetingID INT NOT NULL AUTO_INCREMENT,
  title VARCHAR(50) NOT NULL,
  description VARCHAR(255),
  isPublic BOOLEAN,
  audience ENUM('Public', 'Private', 'Internal'),
  PRIMARY KEY (meetingID)
);

CREATE TABLE meeting_instances (
    meetingID INT NOT NULL,
    orderID INT NOT NULL AUTO_INCREMENT,
    fromdatetime DATETIME,
    todatetime DATETIME,
    PRIMARY KEY (meetingID, orderID),
    UNIQUE KEY (orderID),
    FOREIGN KEY (meetingID) REFERENCES meetings(meetingID)
);


INSERT INTO users (name, age, gender, email)
VALUES
  ('John Doe', 25, 'Male', 'john.doe@example.com'),
  ('Jane Smith', 30, 'Female', 'jane.smith@example.com'),
  ('Bob Johnson', 40, 'Male', 'bob.johnson@example.com'),
  ('Alice Lee', 28, 'Female', 'alice.lee@example.com'),
  ('Chris Brown', NULL, 'Other', 'chris.brown@example.com');


INSERT INTO meetings (title, description, isPublic, audience)
VALUES
  ('Project Kickoff Meeting', 'Discuss project goals and timeline', TRUE, 'Internal'),
  ('Sales Presentation', 'Present new product to potential clients', FALSE, 'Public'),
  ('Team Building Activity', 'Participate in team-building exercises', TRUE, 'Private');

INSERT INTO meeting_instances (meetingID, fromdatetime, todatetime)
VALUES
  (1, '2023-05-10 09:00:00', '2023-05-10 11:00:00'),
  (1, '2023-05-12 14:00:00', '2023-05-12 16:00:00'),
  (2, '2023-05-15 10:00:00', '2023-05-15 12:00:00');
