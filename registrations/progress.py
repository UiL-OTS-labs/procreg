from django.views import View
from cdh.questions.questions import Question


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

#    all_questions = [
        #NewRegistrationQuestion,
        #FacultyQuestion,
        #TraversalQuestion,
        #]

    def __init__(self, blueprint):

        self.blueprint = blueprint
        self.items = []

    def get_items(self, current=None):
        item_list = []

        completed = self.blueprint.completed
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

        try:
            for rq in self.blueprint.required:
                self.add_question(rq)

            for qq in self.blueprint.questions:
                self.add_question(qq)

            for ep in self.blueprint.extra_pages:
                self.add_question(ep)

        except Exception as exc:
            print(
                f"""Breaking out of progress bar construction with exception e:
                {exc}""")

    def ingest(self, item):
        self.add_item(item)

    def add_item(self, item):
        if isinstance(item, Question):
            self.add_question(item)
        elif isinstance(item, View):
            self.add_view(item)

    def add_view(self, item):
        pass

    def add_question(self, question):
        completed = question.slug in [
            q.slug for q in self.blueprint.completed
        ]
        self.items.append(
            ProgressItem.from_question(
                question,
                completed=completed,
            ),
        )


class ProgressItemMixin():
    """Provides the basic attributes for a view or question
    to be displayed in a progress bar"""

    title = "registrations:mixins:progress_item"
    slug = "progress_item"

    def __init__(self, *args, **kwargs):
        self.complete = False
        self.current = False
        self.disabled = False
        self.incomplete = False
        return super().__init__(*args, **kwargs)

    def get_edit_url(self):
        return "#"


