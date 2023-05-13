import sys
import RedisFunctions
from User import User
from Meeting import Meeting
from MeetingInstance import MeetingInstance


def main():
    while True:
        print("Enter the number corresponding to the function you want to run:")
        print("1. Get active meeting instances")
        print("2. Delete all meeting instances")
        print("3. Join a meeting")
        print("4. Leave a meeting")
        print("5. Show meeting current users")
        print("6. Show meeting current users with timestamp")
        print("7. Post message")
        print("8. Delete current users at meeting end")
        print("0. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            RedisFunctions.get_active_meeting_instances()
        elif choice == '2':
            RedisFunctions.delete_all_meeting_instances()
        elif choice == '3':
            meeting_id = input("Enter meeting ID: ")
            order_id = input("Enter order ID: ")
            meeting_instance = MeetingInstance(meeting_id, order_id, None, None)
            user_id = input("Enter user ID: ")
            email = input("Enter email: ")
            print(email)
            user = User(user_id, None, None, None, email)
            RedisFunctions.join_meeting(meeting_instance, user)
        elif choice == '4':
            meeting_id = input("Enter meeting ID: ")
            order_id = input("Enter order ID: ")
            meeting_instance = MeetingInstance(meeting_id, order_id, None, None)
            user_id = input("Enter user ID: ")
            email = input("Enter email: ")
            user = User(user_id, None, None, None, email)
            RedisFunctions.leave_meeting(meeting_instance, user)
        elif choice == '5':
            meeting_id = input("Enter meeting ID: ")
            order_id = input("Enter order ID: ")
            meeting_instance = MeetingInstance(meeting_id, order_id, None, None)
            RedisFunctions.show_meeting_current_users(meeting_instance)
        elif choice == '6':
            meeting_id = input("Enter meeting ID: ")
            order_id = input("Enter order ID: ")
            meeting_instance = MeetingInstance(meeting_id, order_id, None, None)
            RedisFunctions.show_meeting_current_users_with_timestamp(meeting_instance)
        elif choice == '7':
            meeting_id = input("Enter meeting ID: ")
            order_id = input("Enter order ID: ")
            meeting_instance = MeetingInstance(meeting_id, order_id, None, None)
            user_id = input("Enter user ID: ")
            email = input("Enter email: ")
            user = User(user_id, None, None, None, email)
            message = input("Enter message: ")
            RedisFunctions.post_message(user, meeting_instance, message)
        elif choice == '8':
            meeting_id = input("Enter meeting ID: ")
            order_id = input("Enter order ID: ")
            meeting_instance = MeetingInstance(meeting_id, order_id, None, None)
            RedisFunctions.delete_current_users_at_meeting_end(meeting_instance)
        elif choice == '0':
            sys.exit()
        else:
            print("Invalid choice")
        print()


if __name__ == "__main__":
    main()
