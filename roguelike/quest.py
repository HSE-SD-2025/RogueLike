class Quest:
    def __init__(self, description):
        self.description = description
        self.status = 'in_progress'

    def mark_found(self):
        if self.status == 'in_progress':
            self.status = 'artifact_found'

    def complete(self):
        if self.status == 'artifact_found':
            self.status = 'completed'

    def reset(self):
        self.status = 'in_progress'


def default_artifact_quest():
    return Quest('Find an artifact and return to base.') 