from django.urls import reverse
from .questions import QUESTIONS

import logging


from cdh.questions.blueprints import Blueprint

from .models import Registration, Involved
# from .progress import RegistrationProgressBar
from .consumers import TopQuestionsConsumer, NewRegistrationConsumer, \
    FacultyConsumer


info = logging.info
debug = logging.debug



class BlueprintErrors():

    def __init__(self):
        self.all_errors = []

    def add(self, *args):
        self.all_errors.append(args)

    def search(self, *args):
        result = []
        for e in self.all_errors:
            if self.rfilter2(e, args)[-1] != EndStop:
                result.append(e)
        return result

    def __getitem__(self, *args):
        return self.search(*args)

    def rfilter2(self, sample, args, depth=0):
        """Sequentially filter a list of items through a list of filters"""
        # First, the case in which we've exhausted our samples
        if len(sample) == 0:
            # If there are no more args, then it's a perfect match
            if len(args) == 0:
                return [sample]
            # If there are still unmatched filters, add an EndStop
            # to mark the failure
            else:
                return [EndStop]
        # Below is the general case in which we still have samples left
        if len(args) == 0:
            # No more filters, so all we have left matches by default
            return [sample]
        # Define current filter from args
        else:
            if not callable(args[0]):
                # Non-callable just wants an exact match
                def current(x):
                    return x == args[0]
            else:
                # Current filter was already callable
                current = args[0]
        if not current(sample[0]):
            # Filter doesn't match, so stop matching here
            return [ EndStop ]
        # Default result, return current match and filtered remainder
        return [sample[0]] + self.rfilter2(sample[1:], args[1:])


class EndStop:
    pass
        

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
        # self.progress_bar = RegistrationProgressBar(self)
        self.desired_next = []
        self.top_questions = []
        # These are the selected groups of subjects such as consent,
        # non-consent, etc.
        self.selected_groups = []
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

    def get_question(self, slug=None, question_pk=False, extra_filter=None,
                     always_list=False,):
        """
        Get questions matching kwargs from this blueprints list of
        instantiated questions.
        """
        match = []
        # Basic matching on attributes
        for q in self.questions:
            if slug is not None:
                if q.slug != slug:
                    continue
            if not isinstance(question_pk, bool):
                # We want a question with a specific pk,
                # which may include None to specifically
                # find a question with an unsaved instance
                if q.instance.pk != question_pk:
                    continue
            if question_pk is True:
                # We don't care about the instance pk other
                # than that it's defined
                if q.instance.pk is None:
                    continue
            match.append(q)
        # Extra arbitrary filter
        if extra_filter:
            match = list(
                filter(extra_filter, match)
            )
        size = len(match)
        if size == 0:
            if always_list:
                return []
            else:
                return None
        if size == 1:
            if always_list:
                return match
            else:
                return match[0]
        else:
            return match

    def get_involved_groups(
            self,
            group_type=None,
            hide_unselected=True,
    ):
        """
        Return a dict of group types to list of involved
        group instances.
        """

        if hide_unselected is True:
            group_types = self.object.list_involved_types()
        else:
            group_types = [
                "knowingly",
                "not_knowingly",
                "guardian",
                "other",
            ]

        def make_question_filter(our_involved):
            """Return a filtering function determining if given question
            has given involved group as instance"""
            def filter_function(question):
                question_model = getattr(question, "model", False)
                if question_model:
                    if question_model is Involved:
                        return question.instance is our_involved
                return False
            return filter_function

        out = dict()
        for key in group_types:
            qs = Involved.objects.filter(
                registration=self.object,
                group_type=key,
            )
            out[key] = {
                "group_type": "models:involved:group_type_" + key,
                "groups": [involved for involved in qs],
                "questions": {
                    involved: self.get_question(
                        extra_filter=make_question_filter(involved),
                        always_list=True,
                    )
                    for involved in qs
                }
            }
        return out

    def get_questions_for_involved(self, involved):

        def make_question_filter(our_involved):
            """Return a filtering function determining if given question
            has given involved group as instance"""
            def filter_function(question):
                try:
                    return question.instance == our_involved
                except AttributeError:
                    return False
                return False
            return filter_function

        return self.get_question(
            extra_filter=make_question_filter(involved),
            always_list=True,
        )

    def any_involved_group_available(self):
        """Return True if there is any involved group available to populate
        that section of the progress bar."""
        for inv_type in self.get_involved_groups().values():
            if len(inv_type["groups"]) > 0:
                return True
        return False

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
                registration=self.object,
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

