import Scheduler
import UI
import threading


def main():
    scheduler = Scheduler.Scheduler()
    scheduler_thread = threading.Thread(target=scheduler.run)
    scheduler_thread.start()
    UI.main()


if __name__ == '__main__':
    main()
