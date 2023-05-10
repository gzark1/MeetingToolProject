class Meeting:
    def __init__(self, meetingId, title, description,isPublic,audience):
        self.title = title
        self.description = description
        self.isPublic = isPublic
        self.audience = audience

    def __str__(self):
        return "Meeting: " + self.title + " " + self.description + " " + self.isPublic + " " + self.audience

