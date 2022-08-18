from .forms import NewRegistrationQuestion, CategoryQuestion, \
    TraversalQuestion, QUESTIONS, FacultyQuestion, \
    InvolvedPeopleQuestion, StorageQuestion, UsesInformationQuestion


class ProgressItem:

    def __init__(self):

        self.title = "Nameless"
        self.current = False
        self.completed = False
        self.url = None
        self.children = []

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
        self.items = []

    def get_items(self, current=None):
        item_list = []

        completed = self.blueprint.instantiate_question(
            self.blueprint.completed,
        )
        for q in completed:
            item_list.append(
                ProgressItem.from_question(
                    q,
                    completed=True,
                    current=(current == q.slug),
                )
            )
        required = self.blueprint.instantiate_question(
            self.blueprint.required,
        )
        for q in required:
            item_list.append(
                ProgressItem.from_question(
                    q,
                    completed=False,
                    current=(current == q.slug),
                )
            )
        return item_list

    def populate(self):

        for q in self.blueprint.completed:
            self.add_question(q)

        for rq in self.blueprint.required:
            self.add_question(rq)

    def add_question(self, question):
        question = self.blueprint.instantiate_question(question)
        completed = question.slug in [
            q.slug for q in self.blueprint.completed
        ]
        self.items.append(
            ProgressItem.from_question(
                question,
                completed=completed,
            ),
        )
