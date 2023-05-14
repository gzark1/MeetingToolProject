# Meeting Tool Project

## Description
This project is a meeting tool that allows users to create meetings and chat. The tool is built using Redis and a traditional Mysql Database. 

## Installation
1. Clone the repository
2. Install the dependencies using `pip install -r requirements.txt`
3. Run a local mysql server
4. Run a local redis server
5. Load the database schema from the file `database.sql`
6. Run the program using 'python UI.py'


## Development
The project is developed using Python and the following libraries:
- Redis
- Mysql

In order to achieve the goal of the project, the following classes were created:
- User
- Meeting
- MetingInstance
- RedisConnection
- DataBaseConnection
- UI
- Scheduler
- RedisFunctions

Scheduler is a class that is used to run the program in the background. It is used to check if there are any meetings that are due to start and if so, it starts them. It also checks if there are any meetings that are due to end and if so, it ends them.
Scheduler in the start of the program is started in a separate thread and it runs in the background.

UI is a class that is used to interact with the user. It is used to get the user input and to display the output to the user.

The main functions of the program are implemented in the RedisFunctions class. This class is used to interact with the Redis database. It is used to create, delete and update meetings and users. It is also used to get the information about the meetings and users.

In order to support chat we used redis pub/sub. When a user joins a meeting, he subscribes to the channel of that meeting. When a user sends a message, the message is published to the channel of the meeting. When a user joins a meeting, he receives all the messages that were sent to the channel of that meeting.The channel of the meeting runs in a separate thread and it runs in the background. 

In Main class we run the Ui class and Scheduler class in separate threads. We also run the channel of the meeting in a separate thread.

## Authors
- Marios Aintini(8200003)
- Giorgos Zarkadas(8200043)