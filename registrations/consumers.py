from cdh.questions.blueprints import BaseConsumer, BaseQuestionConsumer

from .forms import NewRegistrationQuestion, FacultyQuestion, \
    UsesInformationQuestion, InvolvedPeopleQuestion, NewInvolvedQuestion, \
    PurposeQuestion, StorageQuestion, ConfirmInformationUseQuestion
from .models import Involved


class RegistrationConsumer(BaseQuestionConsumer):

    def get_question_data(self):
        question_data = super().get_question_data()
        question_data["registration"] = self.blueprint.object
        return question_data


class TopQuestionsConsumer(BaseConsumer):

    def consume(self):
        "If both top questions are filled out, append the next consumer"
        required = [NewRegistrationQuestion, FacultyQuestion]
        for q in required:
            if len(self.blueprint.errors[q.slug]) != 0:
                return []
        self.enable_summary()
        return [InvolvedPeopleConsumer]

    def enable_summary(self):
        from .views import RegistrationSummaryView
        view = RegistrationSummaryView(
            reg_pk=self.blueprint.object.pk,
        )
        self.blueprint.questions.append(view)


class NewRegistrationConsumer(RegistrationConsumer):

    question_class = NewRegistrationQuestion

    def consume(self):
        self.blueprint.top_questions.append(
            self.question,
        )
        self.get_errors()
        self.blueprint.completed.append(self.question)
        # TopQuestionsConsumer checks for our errors, so we can just return
        return []

    def get_errors(self):
        self.errors = self.get_django_errors()
        for f in self.empty_fields:
            self.errors.append(f"Field {f} is empty")
        for field, error in self.errors.items():
            self.blueprint.errors.add(self.question.slug, field, error)


class FacultyConsumer(RegistrationConsumer):

    question_class = FacultyQuestion

    def consume(self):
        self.blueprint.top_questions.append(
            self.question,
        )
        self.get_errors()
        self.blueprint.completed.append(self.question)
        # TopQuestionsConsumer checks for our errors, so we can just return
        return []

    def get_errors(self):
        self.errors = self.get_django_errors()
        for f, v in self.errors.items():
            self.blueprint.errors.add(
                self.question.slug, f, v,
            )
        for f in self.empty_fields:
            self.blueprint.errors.add(
                self.question.slug,
                f,
                f"Field {f} is empty",
            )


class UsesInformationConsumer(RegistrationConsumer):

    question_class = UsesInformationQuestion

    def consume(self):
        # This consumer blocks if unanswered
        self.blueprint.desired_next.append(self.question)
        if self.filled_in_fields == []:
            return []
        answer = self.blueprint.object.uses_information
        if answer is False:
            return [ConfirmInformationUseConsumer]
        elif answer is True:
            return [InvolvedPeopleConsumer]


class InvolvedPeopleConsumer(BaseQuestionConsumer):

    question_class = InvolvedPeopleQuestion

    def consume(self):
        """For each involved group, add the relevant consumer."""
        registration = self.blueprint.object
        self.blueprint.desired_next.append(self.question)
        self.blueprint.questions.append(self.question)
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
            self.blueprint.progress_bar.ingest(m)
        # Finally, return
        if consumers != []:
            return consumers + [StorageConsumer]
        else:
            return []

    def no_group_selected(self):
        return []

    def _get_selected(self):
        """Return the appropriate lists of consumers and managers for the
        booleans set on the registration"""
        registration = self.blueprint.object
        selected = []
        managers = []
        consumer_dict = {
            'involves_consent':
            (ConsentGroupConsumer, "consent"),
            'involves_non_consent':
            (NonConsentGroupConsumer, "non_consent"),
            'involves_guardian_consent':
            (GuardianGroupConsumer, "guardian_consent"),
            'involves_other_people':
            (OtherGroupConsumer, "other"),
        }
        for group in self.question.Meta.fields:
            if getattr(registration, group) is True:
                consumer, group_type = consumer_dict[group]
                # These consumers will be added to this function's output
                selected.append(consumer)
                # These managers should show up in the progress bar
                managers.append(self._construct_manager_view(group_type))
        return selected, managers

    def _construct_manager_view(self, group_type):
        # Importing here to prevent circular import
        from .views import InvolvedManager
        return InvolvedManager(
            registration=self.blueprint.object,
            group_type=group_type,
        )


class GroupManagerConsumer(RegistrationConsumer):
    """This consumer is added when at least one group of a type
    is needed, and succeeds if at least one group of the type
    is correctly filled in."""

    group_type = None
    success_list = []

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    @property
    def group_qs(self):
        registration = self.blueprint.object
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
        return []
        

class ConsentManagerConsumer(GroupManagerConsumer):

    group_type = "consent"


class BaseGroupConsumer(BaseConsumer):

    question_class = NewInvolvedQuestion
    group_type = None
    success_list = []

    def __init__(self, *args, **kwargs):

        return super().__init__(*args, **kwargs)

    @property
    def group_qs(self):
        registration = self.blueprint.object
        return Involved.objects.filter(
            registration=registration,
            group_type=self.group_type,
        )

    def instantiate(self):
        if len(self.group_qs) > 0:
            iq = self.question_class(
                instance=self.group_qs.first(),
                registration=self.blueprint.object,
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


class StorageConsumer(RegistrationConsumer):

    question_class = StorageQuestion

    def consume(self):

        if self.empty_fields == []:
            return []
        return []


class ConfirmInformationUseConsumer(BaseQuestionConsumer):

    question_class = ConfirmInformationUseQuestion

    def consume(self):
        self.blueprint.desired_next.append(self.question)
        return []
