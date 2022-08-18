from django.urls import reverse
import logging


from cdh.questions.blueprints import Blueprint

from .models import Registration, Involved
from .progress import RegistrationProgressBar
from .forms import NewRegistrationQuestion, CategoryQuestion, \
    TraversalQuestion, QUESTIONS, FacultyQuestion, \
    UsesInformationQuestion, ConfirmInformationUseQuestion, \
    SubmitQuestion, InvolvedPeopleQuestion, StorageQuestion, \
    NewInvolvedQuestion


info = logging.info
debug = logging.debug


class RegistrationBlueprint:
    """
    The blueprint for a ProcReg registration.

    This class provides information on current progress,
    error messages, nexT question, and validation information.
    """
    model = Registration
    primary_questions = [NewRegistrationQuestion, ]

    def __init__(self, registration):
        """Set up starting values for blueprint evaluation."""
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

        # For now, "go back" functionality is handled by making
        # the desired next question a stack
        self.desired_next = []

        self.evaluate(self.starting_consumers)

        self.progress_bar.populate()

    def evaluate(self, consumers):
        """
        Evaluate all consumers.

        This recursive function goes through the list
        of consumers and presents them with this blueprint
        object. The consumers look at the current state of
        the blueprint to see if it satisfies their needs.

        Consumers should return a list of new consumers to
        append to the end of the list. This list may be empty.

        While in this loop, consumers may modify
        blueprint state by adding errors and setting
        desired_next.
        """
        # We've run out of consumers. Finally.
        if consumers == []:
            return True

        # Instantiate consumer with self
        current = consumers[0](self)

        # Run consumer logic, and add the list of consumers
        # it returns to the list of consumers to be run
        next_consumers = current.consume() + consumers[1:]

        return self.evaluate(consumers=next_consumers)

    def required(self):
        usual = [NewRegistrationQuestion]

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
                               'reg_pk': self.registration.pk,
                           })        
        if next_question in QUESTIONS.values():
            question = self.instantiate_question(next_question)
            return question.get_edit_url()
        return reverse(
            "registrations:overview",
            kwargs={
                "reg_pk": self.registration.pk,
            })

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
            q_object = self.registration
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
                reg_pk=self.registration.pk,
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


class BaseConsumer:

    def __init__(self, blueprint):
        self.blueprint = blueprint
        self.on_complete = False

    def complete(self, out_list=False):
        if not out_list:
            if not self.on_complete:
                return []
            return self.on_complete
        return out_list
    
    def consume(self):
        """Returns a list of new consumers depending on
        the state of our blueprint."""
        return []


class BaseQuestionConsumer(BaseConsumer):

    def get_question_errors(self):
        "Get Django form errors"
        self.instantiated = self.instantiate()
        errors = self.instantiated.errors
        debug(f'Errors in question {self.question}: {errors}')
        return errors
    
    def instantiate(self):
        return self.blueprint.instantiate_question(self.question)

    @property
    def empty_fields(self):
        empty = []
        question = self.instantiate()
        print(f"\n\n{question} might be instance??\n\n")
        for key in question.Meta.fields:
            value = question[key].value()
            if value in ['', 'None']:
                empty.append(value)
        return empty
            
    def complete(self, *args, **kwargs):
        self.blueprint.completed += [self.question]
        return super().complete(*args, **kwargs)


class BasicDetailsConsumer(BaseQuestionConsumer):
    question = NewRegistrationQuestion

    def consume(self):
        if self.check_details():
            self.blueprint.desired_next.append(FacultyQuestion)
            return self.complete([FacultyConsumer])
        else:
            return []

    def complete(self, next):
        """Don't append to completed."""
        return next
       
    def check_details(self):
        if self.empty_fields != []:
            return False
        return True

    
class FacultyConsumer(BaseQuestionConsumer):
    question = FacultyQuestion

    def consume(self):
        if self.check_details():
            self.blueprint.desired_next.append(TraversalQuestion)
            return self.complete([TraversalConsumer])
        else:
            return []
        return [UsesInformationConsumer]

    def complete(self, next):
        """Don't append to completed."""
        return next
    
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
            self.blueprint.desired_next.append(UsesInformationQuestion)
            return self.complete([UsesInformationConsumer])

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
    question = UsesInformationQuestion

    def consume(self):
        if not self.check_details():
            return []

        answer = self.blueprint.registration.uses_information
        if answer is False:
            self.blueprint.desired_next.append(ConfirmInformationUseQuestion)
            return self.complete([ConfirmInformationUseConsumer])
        elif answer is True:
            self.blueprint.desired_next.append(InvolvedPeopleQuestion)
            return self.complete([InvolvedPeopleConsumer])

        return []

    def check_details(self):

        return fields_not_empty(self.questions[0].Meta.fields)


class InvolvedPeopleConsumer(BaseQuestionConsumer):
    question = InvolvedPeopleQuestion

    def consume(self):
        """For each involved group, add the relevant consumer."""
        registration = self.blueprint.registration

        # Check if one required groups are checked
        if True not in [
                registration.involves_consent,
                registration.involves_non_consent,
        ]:
            return self.no_group_selected()

        selected = []
        consumer_dict = {
            'involves_consent': ConsentGroupConsumer,
            'involves_non_consent': NonConsentGroupConsumer,
            'involves_guardian_consent': GuardianGroupConsumer,
            'involves_other_people': OtherGroupConsumer,
        }
        for group in self.question.Meta.fields:
            if getattr(registration, group) is True:
                selected.append(consumer_dict[group])
        if selected != []:
            return self.complete(selected + [StorageConsumer])
        else:
            return []

    def no_group_selected(self):

        return []


class BaseGroupConsumer(BaseQuestionConsumer):

    group_type = None
    success_list = []

    def __init__(self, *args, **kwargs):

        return super().__init__(*args, **kwargs)

    @property
    def group_qs(self):
        registration = self.blueprint.registration
        return Involved.objects.filter(
            registration=registration,
            type=self.group_type,
        )

    def consume(self):
        if self.has_entries():
            if self.check_details():
                return self.success()
        return self.fail()

    def check_details(self):
        return True

    def has_entries(self):
        return not len(self.group_qs) == 0

    def success(self):
        return self.success_list

    def fail(self):
        self.blueprint.required.append(
            self.blueprint.instantiate_question(
                NewInvolvedQuestion,
                type=self.type,
            )
        )
        return []


class ConsentGroupConsumer(BaseGroupConsumer):

    type = "consent"


class NonConsentGroupConsumer(BaseGroupConsumer):

    type = "non_consent"


class GuardianGroupConsumer(BaseGroupConsumer):

    type = "guardian_consent"


class OtherGroupConsumer(BaseGroupConsumer):

    type = "other"


class StorageConsumer(BaseQuestionConsumer):

    question = StorageQuestion

    def consume(self):

        if self.empty_fields == []:
            self.complete()
        return []


class ConfirmInformationUseConsumer(BaseQuestionConsumer):

    questions = [ConfirmInformationUseQuestion]

    def consume(self):

        return []

    def check_details(self):

        return fields_not_empty(self.questions[0].Meta.fields)


def has_empty_fields(fields):
    """Check if any of these fields are empty."""
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
        
