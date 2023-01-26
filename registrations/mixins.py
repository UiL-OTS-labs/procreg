from django.core.exceptions import PermissionDenied
from cdh.questions.views import BlueprintMixin
from .blueprints import RegistrationBlueprint


class ProgressItemMixin():
    """Provides the basic attributes for a view or question
    to be displayed in a progress bar"""

    title = "registrations:mixins:progress_item"
    slug = "progress_item"

    def __init__(self, *args, **kwargs):
        self.complete = False
        self.current = False
        self.disabled = False
        self.incomplete = False
        return super().__init__(*args, **kwargs)

    def get_edit_url(self):
        return "#"


class UsersOrGroupsAllowedMixin():

    def get_group_required(self):
        """Is overwritten to provide a dynamic list of
        groups which have access"""
        if not isinstance(self.group_required, (list, tuple)):
            self.group_required = (self.group_required,)
        return self.group_required

    def get_allowed_users(self):
        """Is overwritten to provide a dynamic list of
        users who have access."""
        if not isinstance(self.allowed_users, (list, tuple)):
            self.allowed_users = (self.allowed_users,)
        return self.allowed_users

    def allowed_user_test(self, user):
        """Given a user object, return True if they are allowed"""
        return False

    def check_membership(self, groups):
        """ Check required group(s) """
        # We do a superuser check here because this method
        # should never get overwritten
        if self.current_user.is_superuser:
            return True
        return set(groups).intersection(set(self.current_user_groups))

    def dispatch(self, request, *args, **kwargs):
        authorized = False
        self.current_user = request.user
        self.current_user_groups = set(self.current_user.groups.values_list("name", flat=True))

        # Default allowed groups and users
        try: group_required = self.group_required
        except AttributeError:
            self.group_required = None

        try: allowed_users = self.allowed_users
        except AttributeError:
            self.allowed_users = None

        if self.current_user.is_authenticated:
            if self.current_user in self.get_allowed_users():
                authorized = True
            elif self.check_membership(self.get_group_required()):
                authorized = True

        if self.allowed_user_test(self.current_user):
            authorized = True

        if not authorized:
            raise PermissionDenied

        return super(UsersOrGroupsAllowedMixin, self).dispatch(
            request, *args, **kwargs)




class QuestionFromBlueprintMixin(
):
    """Get the question to edit from the blueprint."""

    question_class_kwarg = "question"

    def get_question(self, extra_filter=None):
        """Use the provided kwarg to get the instatiated question
        from our blueprint."""
        blueprint = self.get_blueprint()
        slug = self.kwargs.get(self.question_class_kwarg)
        question_pk = self.kwargs.get("question_pk")
        search = blueprint.get_question(
            slug,
            question_pk=question_pk,
            extra_filter=extra_filter,
        )
        if search is None:
            raise RuntimeError(
                f"No Question found in blueprint for given args: \
                {slug} with pk {question_pk}",
            )
        elif type(search) is list:
            raise RuntimeError(
                f"Got multiple possible questions for given query: \
                {slug} with pk {question_pk} ({search})",
            )
        else:
            return search

    def get_question_object(self):
        return self.get_question().instance

    def get_form(self):
        if self.request.method in ('POST', 'PUT'):
            return super().get_form()
        return self.get_question()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {"blueprint": self.get_blueprint()}
        )
        return kwargs

    def get_question_class(self):
        return type(self.get_question())


