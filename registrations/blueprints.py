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
        self.completed = []
        self.progress_bar = RegistrationProgressBar(self)

        self.starting_consumers = [BasicDetailsConsumer]
        self.errors = dict()
        self.registration = registration
        self.desired_next = None

        self.evaluate(self.starting_consumers)

    def evaluate(self, consumers):
        """Go through the list of consumers and try to satisfy their needs"""

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
        debug(f'Errors in question {self.question}: {errors}')

        return errors

    def complete(self):

        self.blueprint.completed.append(self.question)

class BasicDetailsConsumer(BaseQuestionConsumer):

    question = NewRegistrationQuestion

    def consume(self):

        if self.check_details():
            self.blueprint.desired_next = FacultyQuestion
            self.complete()
        else:
            return []

        return [FacultyConsumer]

    def check_details(self):

        registration = self.blueprint.registration

        empty = has_empty_fields(
            [
                registration.title,
             ]
        )
        self.blueprint.errors[self.question] = empty

        return not empty

class FacultyConsumer(BaseQuestionConsumer):

    question = FacultyQuestion

    def consume(self):

        if self.check_details():
            self.blueprint.desired_next = TraversalQuestion
            self.complete()
        else:
            return []

        return [TraversalConsumer]

    def check_details(self):

        registration = self.blueprint.registration

        empty = has_empty_fields(
            [registration.title,
             registration.faculty,
            ]
        )

        if empty:
            self.blueprint.errors[self.question] = empty
            return False
        else:
            return True

        


class TraversalConsumer(BaseQuestionConsumer):

    question = TraversalQuestion

    def consume(self):

        if self.check_details():
            self.blueprint.desired_next = TraversalQuestion
            self.complete()

        return []

    def check_details(self):
        
        registration = self.blueprint.registration

        empty = has_empty_fields(
            [registration.date_start,
             registration.date_end,
            ]
        )

        if empty:
            self.blueprint.errors[self.question] = empty
            return False
        else:
            return True

        return fields_not_empty(self.question.Meta.fields)

        
def has_empty_fields(fields):
    errors = []
    for f in fields:
        if f in ['', None]:
            debug(f, 'was not filled in')
            errors.append(f)

    if errors != []:
        return errors
    else:
        return False
