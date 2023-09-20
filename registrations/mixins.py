from django.core.exceptions import PermissionDenied
from cdh.questions.views import BlueprintMixin
from .blueprints import RegistrationBlueprint




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

    def get_question_pk(self,):
        self.question_pk = self.kwargs.get("question_pk", None)
        if not self.question_pk:
            if hasattr(self, "instance"):
                self.question_pk = self.instance.pk
        return self.question_pk

    def get_question(self, extra_filter=None):
        """Use the provided kwarg to get the instatiated question
        from our blueprint."""
        blueprint = self.get_blueprint()
        slug = self.kwargs.get(self.question_class_kwarg)
        question_pk = self.get_question_pk()
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
                f"""Got multiple possible questions for given query: 
                {slug} with pk {question_pk} ({search})""",
            )
        else:
            return search

    def get_object(self,):
        """Using this mixin, the questions provided by the
        Blueprint should already be instantiated. So we can
        just grab the object from the form."""
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



class GroupTypeMixin():
    """Pass group type on to question"""

    def get_question(self):
        group_type = self.kwargs.get("group_type")
        if not group_type:
            return super().get_question()

        def group_type_filter(question):
            result = question.instance.group_type == group_type
            return result

        return super().get_question(extra_filter=group_type_filter)

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        group_type = self.kwargs.get("group_type")
        if group_type:
            form_kwargs.update(
                {"group_type": group_type}
            )
        return form_kwargs


class RegistrationMixin(
        GroupTypeMixin,
        QuestionFromBlueprintMixin,
        BlueprintMixin,
        UsersOrGroupsAllowedMixin,
):

    blueprint_class = RegistrationBlueprint
    blueprint_pk_kwarg = "reg_pk"
    registration = None

    """Allow the owner of a registration to access and edit it.
    In the future, this will include collaborators."""

    def get_registration(self):
        return self.get_blueprint_object()

    def allowed_user_test(self, user):
        return user.is_staff

    def get_allowed_users(self):
        allowed = [self.get_registration().created_by]
        allowed.append(super().get_allowed_users())
        return allowed

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['registration'] = self.get_registration()
        return context
