from django.urls import reverse
import logging

info = logging.info
debug = logging.debug

from uil.questions.blueprints import Blueprint

from .models import Registration
from .progress import RegistrationProgressBar
from .forms import NewRegistrationQuestion, CategoryQuestion, \
    TraversalQuestion, QUESTIONS, FacultyQuestion



class RegistrationBlueprint:

    model = Registration
    primary_questions = [NewRegistrationQuestion,
    ]

    def __init__(self, registration):

        self.required = []

        self.consumers = [BasicDetailsConsumer]
        self.registration = registration
        self.desired_next = None

        self.evaluate()

    def evaluate(self, consumers=None):
        """Go through the list of consumers and try to satisfy their needs"""

        # First run, get all consumers
        if consumers == None:
            consumers = self.consumers

        # We've run out of consumers
        if consumers == []:
            return True

        current = consumers[0](self)

        next_consumers = current.consume() + consumers[1:]

        return self.evaluate(consumers=next_consumers)

    def get_desired_next_url(self):
        if self.desired_next in QUESTIONS.values():
            if self.desired_next.model == Registration:
                question = self.desired_next(instance=self.registration)
                info(question.instance)
                return question.get_edit_url()
        return reverse(
            "registrations:overview",
            kwargs={
                "reg_pk": self.registration.pk,
            })


def instantiate_question(registration, question):
    """Take a question and registration, and return an
    instantiated question for validation and introspection
    """
    q_model_name = question.model.__name__
    q_object = getattr(registration, q_model_name)
    return question(instance=q_object)


class BaseConsumer:

    def __init__(self, blueprint):

        self.blueprint = blueprint

class BaseQuestionConsumer(BaseConsumer):

    def get_question_errors(self):

        self.question = instantiate_question(
            self.registration,
            self.question,
        )

        errors = self.question.errors
        info(f'Errors in question {self.question}: {errors}')

        return errors

class BasicDetailsConsumer(BaseConsumer):

    def consume(self):

        if self.check_details():
            self.blueprint.desired_next = TraversalQuestion
        else:
            return []

        return [TraversalConsumer]

    def check_details(self):

        registration = self.blueprint.registration

        for field in [registration.title,
                      registration.faculty,
                      ]:
            info(field)

        return fields_not_empty(
            [registration.title,
             registration.faculty,
            ]
        )

class TraversalConsumer(BaseQuestionConsumer):

    question = TraversalQuestion

    def consume(self):

        if self.check_details():
            self.blueprint.desired_next = FacultyQuestion

        return []

    def check_details(self):

        return fields_not_empty(self.question.Meta.fields)

        

        
def fields_not_empty(fields):
    for f in fields:
        if f in ['', None]:
            info(f, 'was not filled in')
            return False
    return True
