from .forms import NewRegistrationQuestion, CategoryQuestion, \
    TraversalQuestion, QUESTIONS, FacultyQuestion



class RegistrationProgressBar:

    all_questions = [
        NewRegistrationQuestion,
        FacultyQuestion,
        TraversalQuestion,
        ]

    def __init__(self, blueprint):

        self.blueprint = blueprint

    def make_progress_dict(self):

        progress_dict = dict()

        for question in self.all_questions:
            progress_dict[question] = self.make_dict_item(question)

        return progress_dict

    def make_dict_item(self, question):

        item = dict()

        try:
            from .blueprints import instantiate_question
            iq = instantiate_question(blueprint.registration, question)
            link = iq.get_edit_url()
        except:
            link = None

        if hasattr(question, 'short_name'):
            name = short_name
        else:
            name = question.title

        if question in self.blueprint.completed:
            status = 'completed'
        elif question in self.blueprint.errors.keys():
            status = 'error'
        else:
            status = None

        return {
            'name': name,
            'link': link,
            'status': status,
        }
