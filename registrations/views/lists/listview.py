from django.views import generic
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin, \
    UserPassesTestMixin, PermissionDenied
from django.core.exceptions import ImproperlyConfigured
from django import forms

from registrations.models import Registration

def nameget(user):
    if "" in [user.first_name, user.last_name]:
        return user.username
    return user.get_full_name()

class SearchableListView(
        generic.ListView,
        generic.FormView,
):
    context_object_name = "results"
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # To construct page numbers with other GET parameters, we use the tag
        # concat_get_params which needs the current querydict to work.
        # It must be a copy or else it's immutable
        context["current_get_params"] = self.request.GET.copy()
        return context

    def get_form_kwargs(self,):
        """To make the checkboxes stateful, we set initial to the GET data,
        and also add hidden inputs in the template to always pass a value even
        the box is unchecked."""
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "initial": self.request.GET,
            }
        )
        return kwargs


class MyRegistrationsForm(forms.Form,):

    search = forms.CharField(
        max_length=200,
        required=False,
        initial="",
    )
    include_drafts = forms.BooleanField(
        label=_("lists:registrations:filter_label_drafts"),
        required=False,
        initial=True,
    )
    include_submitted = forms.BooleanField(
        label=_("lists:registrations:filter_label_submitted"),
        required=False,
        initial=True,
    )
    include_registered = forms.BooleanField(
        label=_("lists:registrations:filter_label_registered"),
        required=False,
        initial=True,
    )
    include_favourites = forms.BooleanField(
        label=_("lists:registrations:filter_label_favourites"),
        required=False,
        initial=True,
    )

    def __init__(self, *args, **kwargs):
        """Set correct CSS classes and attributes on form """
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if type(field.widget) == forms.widgets.CheckboxInput:
                field.widget.attrs["class"] = "form-check-input"
            if type(field.widget) == forms.widgets.TextInput:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = _(
                    "lists:registrations:placeholder_search"
                )



class MyRegistrationsList(
        LoginRequiredMixin,
        SearchableListView,
):
    model = Registration
    form_class = MyRegistrationsForm
    template_name = "lists/my_registrations.html"
    paginate_by = 10

    def get_queryset(self,):
        user = self.request.user
        self.starting_qs = Registration.objects.filter(created_by=user)
        return self.apply_filters(self.starting_qs)

    def apply_filters(self, qs,):
        def favs(qs):
            """Once implemented, this will filter a user's favourites"""
            return Registration.objects.none()

        def drafts(qs):
            return qs.filter(status="draft")

        def submitted(qs):
            return qs.filter(status="submitted")

        def registered(qs):
            return qs.filter(status="registered")

        filters = {
            "include_favourites": favs,
            "include_drafts": drafts,
            "include_submitted": submitted,
            "include_registered": registered,
        }
        form = self.get_form()
        checkboxes = {
            name: form[name].value() for name in filters.keys()
        }
        to_be_applied = [
            filters[f](qs) for f in filters if checkboxes[f] is not None
        ]

        output_qs = Registration.objects.none()
        while to_be_applied != []:
            f = to_be_applied.pop()
            output_qs = output_qs | f

        return self.apply_search(output_qs)

    def apply_search(self, qs):
        form = self.get_form()
        query = form["search"].value()
        query = query.strip().split()
        if query in ["", None]:
            return qs
        filters = []
        for w in query:
            # The order of operations here is deliberate.
            # Each word may occur in either of these fields.
            filters += [
                Q(title__icontains=w) | \
                Q(created_by__first_name__icontains=w) | \
                Q(created_by__last_name__icontains=w)
            ]
        while filters != []:
            # And finally all the OR'ed filters get AND'ed together.
            # Every word must match in at least one of the fields.
            f = filters.pop(0)
            qs = qs.filter(f)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PORegistrationsList(
        MyRegistrationsList,
        UserPassesTestMixin,
):
    template_name = "lists/po_list.html"

    def get_queryset(self):
        self.starting_qs = Registration.objects.all()
        return self.apply_filters(self.starting_qs)

    def test_func(self):
        user = self.request.user
        if "PO" in [g.name for g in user.groups.all()]:
            return True


