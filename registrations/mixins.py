from django.core.exceptions import PermissionDenied
from cdh.questions.views import BlueprintMixin


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

    def check_membership(self, groups):
        """ Check required group(s) """
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

        if not authorized:
            raise PermissionDenied

        return super(UsersOrGroupsAllowedMixin, self).dispatch(
            request, *args, **kwargs)


