from django.urls import reverse
import logging


from cdh.questions.blueprints import Blueprint

from .models import Registration, Involved
from .progress import RegistrationProgressBar
from .forms import NewRegistrationQuestion, CategoryQuestion, \
    TraversalQuestion, QUESTIONS, FacultyQuestion, \
    UsesInformationQuestion, ConfirmInformationUseQuestion, \
    SubmitQuestion, InvolvedPeopleQuestion, StorageQuestion, \
    NewInvolvedQuestion, PurposeQuestion
from .consumers import TopQuestionsConsumer, NewRegistrationConsumer, \
    FacultyConsumer


info = logging.info
debug = logging.debug


class BlueprintErrors():

    def __init__(self):
        self.all_errors = []

    def add(self, *args):
        self.all_errors.append(args)

    def __getitem__(self, *args):
        return self.rfilter(self.all_errors, args)

    def rfilter(self, sample, args):
        if len(args) == 0:
            return sample
        next_sample = [item[1:] for item in sample if item[0] == args[0]]
        if next_sample == []:
            return next_sample
        return [args[0]] + self.rfilter(next_sample, args[1:])


class CompletedList(list):

    def __init__(self, blueprint):
        self.blueprint = blueprint

    def append(self, item):
        self.blueprint.questions.append(item)
        return super().append(item)


class RegistrationBlueprint(Blueprint):
    """
    The blueprint for a ProcReg registration.

    This class provides information on current progress,
    error messages, nexT question, and validation information.
    """
    model = Registration
    starting_consumers = [
        NewRegistrationConsumer,
        FacultyConsumer,
        TopQuestionsConsumer,
    ]

    def __init__(self, registration):
        """Initialize the progress bar and continue"""
        super().__init__(registration)
        self.progress_bar = RegistrationProgressBar(self)
        self.desired_next = []
        self.top_questions = []
        # Completed is the list of items which are considered
        # correctly filled in. They show up on the summary page.
        self.completed = CompletedList(self)
        self.questions = []
        self.errors = BlueprintErrors()
        self.start()

    def get_desired_next(self, index=1):
        try:
            return self.desired_next[-index]
        except IndexError:
            return None

    def get_desired_next_url(self, index=1):
        """Turn the desired_next Question into a URL."""
        next_question = self.get_desired_next(index)
        if not next_question:
            return reverse('registrations:overview',
                           kwargs={
                               'reg_pk': self.object.pk,
                           })
        if next_question.slug in QUESTIONS.keys():
            return next_question.get_edit_url()
        return reverse(
            "registrations:overview",
            kwargs={
                "reg_pk": self.object.pk,
            })

    def get_question(self, **kwargs):
        """
        Get questions matching kwargs from this blueprints list of instantiated questions.
        """
        match = self.questions
        for key, value in kwargs.items():
            match = filter(
                lambda q: getattr(q, key, False) == value,
                match,
            )
        match = list(match)
        size = len(match)
        if size == 0:
            return None
        if size == 1:
            return match[0]
        else:
            return list(match)

    def instantiate_question(self, question_or_list, **kwargs):
        """
        Return an instantiated question.

        Take a question, and return an
        instantiated question for validation and introspection.
        """
        if type(question_or_list) == list:
            return [self.instantiate_question(q) for q in question_or_list]
        question = question_or_list
        
        if question.model == Registration:
            q_object = self.object
        else:
            q_object = question.model()
            # if hasattr(question.model, "registration_related_name"):
            #     q_object = getattr(
            #         self.registration, question.model.registration_related_name
            #     )
            # else:
            #     q_model_name = question.model.__name__
            #     q_object = getattr(self.registration, q_model_name)
        try:
            instantiated = question(
                instance=q_object,
                reg_pk=self.object.pk,
                **kwargs,
            )
        except TypeError:
            print(f"This is instantiated {question}\n\n")
            return question
        return instantiated

    def instantiate_completed(self):
        """Instantiate all questions in self.completed."""
        out = []
        for q in self.completed:
            inst = self.instantiate_question(q)
            if type(inst) != list:
                inst = [inst]
            out += inst
        return out

