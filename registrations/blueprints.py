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


info = logging.info
debug = logging.debug


class RegistrationBlueprint(Blueprint):
    """
    The blueprint for a ProcReg registration.

    This class provides information on current progress,
    error messages, nexT question, and validation information.
    """
    model = Registration
    primary_questions = [NewRegistrationQuestion, ]
    desired_next = []

    def __init__(self, registration):
        """Initialize the progress bar and continue"""
        self.progress_bar = RegistrationProgressBar(self)
        return super().__init__(registration)

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
        self.blueprint.questions += [self.instantiate()]
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

        # Fetch relevant consumer and manager for user selection
        consumers, managers = self._get_selected()

        # Append relevant managers here for progress bar
        for m in managers:
            self.blueprint.extra_pages.append(m)

        # Finally, return 
        if consumers != []:
            return self.complete(consumers + [StorageConsumer])
        else:
            return self.complete([])

    def no_group_selected(self):

        return []

    def _get_selected(self):
        """Return the appropriate lists of consumers and managers for the
        booleans set on the registration"""
        
        registration = self.blueprint.registration
        selected = []
        managers = []
        consumer_dict = {
            'involves_consent': (ConsentGroupConsumer, "consent"),
            'involves_non_consent': (NonConsentGroupConsumer, "non_consent"),
            'involves_guardian_consent': (GuardianGroupConsumer, "guardian_consent"),
            'involves_other_people': (OtherGroupConsumer, "other"),
        }
        # Importing here to prevent circular import
        from .views import InvolvedManager
        for group in self.question.Meta.fields:
            if getattr(registration, group) is True:
                consumer, group_type = consumer_dict[group]
                # These consumers will be added to this function's output
                selected.append(consumer)
                # Add managers to progress bar
                manager = InvolvedManager(
                    registration=self.blueprint.registration,
                    group_type=group_type,
                )
                managers.append(manager)
        return selected, managers


class GroupManagerConsumer(BaseConsumer):
    """This consumer is added when at least one group of a type
    is needed, and succeeds if at least one group of the type
    is correctly filled in."""

    group_type = None
    success_list = []

    def __init__(self, *args, **kwargs):

        return super().__init__(*args, **kwargs)

    @property
    def group_qs(self):
        registration = self.blueprint.registration
        return Involved.objects.filter(
            registration=registration,
            group_type=self.group_type,
        )
    
    def get_manager(self):

        from .views import InvolvedManager
        return InvolvedManager(
            registration=self.blueprint.registration,
            group_type=self.group_type,
        )

    def consume(self):
        return self.success()

    def success(self):
        manager = self.get_manager()
        self.blueprint.extra_pages.append(manager)
        return self.success_list
        

class ConsentManagerConsumer(GroupManagerConsumer):

    group_type = "consent"


class BaseGroupConsumer(BaseConsumer):

    question = NewInvolvedQuestion
    group_type = None
    success_list = []

    def __init__(self, *args, **kwargs):

        return super().__init__(*args, **kwargs)

    @property
    def group_qs(self):
        registration = self.blueprint.registration
        return Involved.objects.filter(
            registration=registration,
            group_type=self.group_type,
        )

    def instantiate(self):
        if len(self.group_qs) > 0:
            iq = self.question(
                instance=self.group_qs.first(),
                registration=self.blueprint.registration,
            )
        else:
            iq = self.question(
                group_type=self.group_type,
                registration=self.blueprint.registration,
            )
        return iq

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
        return []


class ConsentGroupConsumer(BaseGroupConsumer):

    group_type = "consent"


class NonConsentGroupConsumer(BaseGroupConsumer):

    group_type = "non_consent"


class GuardianGroupConsumer(BaseGroupConsumer):

    group_type = "guardian_consent"


class OtherGroupConsumer(BaseGroupConsumer):

    group_type = "other"


class PurposeConsumer(BaseQuestionConsumer):

    question = PurposeQuestion


class StorageConsumer(BaseQuestionConsumer):

    question = StorageQuestion

    def consume(self):

        if self.empty_fields == []:
            self.complete()
        return []


class ConfirmInformationUseConsumer(BaseQuestionConsumer):

    questions = [ConfirmInformationUseQuestion]
    question = ConfirmInformationUseQuestion

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
        
