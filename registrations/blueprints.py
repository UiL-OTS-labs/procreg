from django.urls import reverse
import logging

info = logging.info
debug = logging.debug

from cdh.questions.blueprints import Blueprint

from .models import Registration
from .progress import RegistrationProgressBar
from .forms import NewRegistrationQuestion, CategoryQuestion, \
    TraversalQuestion, QUESTIONS, FacultyQuestion, \
    UsesInformationQuestion, ConfirmInformationUseQuestion, \
    SubmitQuestion



class RegistrationBlueprint:
    """The blueprint for a ProcReg registration. 
    This class provides information on current progress,
    error messages, next question, and validation information."""

    model = Registration
    primary_questions = [NewRegistrationQuestion,
    ]

    def __init__(self, registration):
        "Set up starting values for blueprint evaluation"
        
        self.required = []
        self.completed = []
        self.registration = registration


        # This is messy, subject to change
        self.progress_bar = RegistrationProgressBar(self)

        # Starting point for validation
        self.starting_consumers = [BasicDetailsConsumer]

        # This will probably be analogous to Django's own
        # errors dict, with field references spanning multiple
        # objects
        self.errors = dict()
        self.desired_next = None

        self.evaluate(self.starting_consumers)

    def evaluate(self, consumers):
        """This recursive function goes through the list
        of consumers and presents them with this blueprint
        object. The consumers look at the current state of
        the blueprint to see if it satisfies their needs.

        Consumers should return a list of new consumers to
        append to the end of the list. This list may be empty.

        While in this loop, consumers may modify
        blueprint state by adding errors and setting
        desired_next."""

        # We've run out of consumers. Finally.
        if consumers == []:
            return True

        # Instantiate consumer with self
        current = consumers[0](self)

        # Run consumer logic, and add the list of consumers
        # it returns to the list of consumers to be run
        next_consumers = current.consume() + consumers[1:]

        return self.evaluate(consumers=next_consumers)

    def get_desired_next_url(self):
        """Turn the desired_next Question into a URL.
        Probably a QuestionEditView."""
        
        if self.desired_next in QUESTIONS.values():
            question = self.desired_next(instance=self.registration)
            return question.get_edit_url()
        return reverse(
            "registrations:overview",
            kwargs={
                "reg_pk": self.registration.pk,
            })


def instantiate_question(registration, question):
    """Take a question and registration, and return an
    instantiated question for validation and introspection.

    This is a stupid hack until we get questions to bootstrap
    themselves based on a registration or blueprint object.
    """
    q_model_name = question.model.__name__
    q_object = getattr(registration, q_model_name)
    return question(instance=q_object)


class BaseConsumer:

    def __init__(self, blueprint):

        self.blueprint = blueprint

    def complete(self, out_list):

        return out_list
    
    def consume(self):
        """Returns a list of new consumers depending on
        the state of our blueprint."""

        return []

class BaseQuestionConsumer(BaseConsumer):

    questions = []

    def get_question_errors(self):
        "Get Django form errors"

        self.question = instantiate_question(
            self.registration,
            self.question,
        )

        errors = self.question.errors
        debug(f'Errors in question {self.question}: {errors}')

        return errors

    def complete(self, out_list=[]):

        self.blueprint.completed += self.questions

        return super().complete(out_list)


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

    questions = [
        NewRegistrationQuestion,
        FacultyQuestion,
        ]

    def consume(self):

        if self.check_details():
            self.blueprint.desired_next = TraversalQuestion
            self.complete()
        else:
            return self.complete([])

        return [UsesInformationConsumer]

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

    questions = [TraversalQuestion]

    def consume(self):

        if self.check_details():
            self.blueprint.desired_next = UsesInformationQuestion
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



class UsesInformationConsumer(BaseQuestionConsumer):

    questions = [UsesInformationQuestion]

    def consume(self):

        if not self.check_details():
            return []

        answer = self.blueprint.registration.uses_information
        if answer  == False:
            self.blueprint.desired_next = ConfirmInformationUseQuestion
            return []
        elif answer == True:
            self.blueprint.desired_next = TraversalQuestion

        return []

    def check_details(self):

        return fields_not_empty(self.questions[0].Meta.fields)




class ConfirmInformationUseConsumer(BaseQuestionConsumer):

    questions = [ConfirmInformationUseQuestion]

    def consume(self):

        return []

    def check_details(self):

        return fields_not_empty(self.questions[0].Meta.fields)

def has_empty_fields(fields):
    "Check if any of these fields are empty"
    errors = []
    for f in fields:
        if f in ['', None]:
            debug(f, 'was not filled in')
            errors.append(f)

    if errors != []:
        return errors
    else:
        return False

def fields_not_empty(fields):

    if has_empty_fields(fields) == False:
        return True

    return False
        
