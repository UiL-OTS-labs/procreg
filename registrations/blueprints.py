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

