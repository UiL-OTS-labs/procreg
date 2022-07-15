from .forms import NewRegistrationQuestion, CategoryQuestion, \
    TraversalQuestion, QUESTIONS, FacultyQuestion

class ProgressItem:

    def __init__(self):

        self.title = "Nameless"
        self.current = False
        self.completed = False
        self.url = None

    def from_question(question, completed=False, current=False):

        item = ProgressItem()
        item.title = question.title
        item.url = question.get_edit_url()
        item.completed = completed
        item.current = current

        return item

    def css_class(self):

        classes = []
        if self.completed:
            classes.append("completed")
        if self.current:
            classes.append("current")

        return " ".join(classes)


class RegistrationProgressBar:

    all_questions = [
        NewRegistrationQuestion,
        FacultyQuestion,
        TraversalQuestion,
        ]

    def __init__(self, blueprint):

        self.blueprint = blueprint

    def items(self, current=None):
        item_list = []
        completed = self.blueprint.instantiate_completed()
        for q in completed:
            item_list.append(
                ProgressItem.from_question(
                    q,
                    completed=True,
                    current=(current==q.slug),
                )
            )
        return item_list        
