import User
import MeetingInstance
import Meeting
import RedisFunctions
import RedisConnection
import DataBaseConnection



redis = RedisConnection.connect_to_redis()

user = User.User(2, 'user1', 22, 'Male', 'john.doe@example.com')
redis.set(f'{2}:{69}:status', 'active')
meeting = MeetingInstance.MeetingInstance(2, 69, '2023-05-12 15:31:43', '2023-05-12 15:55:43', )
RedisFunctions.join_meeting(user, meeting)

