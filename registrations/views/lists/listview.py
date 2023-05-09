from django.views import generic
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
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

    def get_form(self,):
        return self.form_class(initial=self.request.GET)

class MyRegistrationsForm(forms.Form,):

    search = forms.CharField(
        max_length=200,
        required=False,
    )
    include_drafts = forms.BooleanField(
        label=_("lists:registrations:filter_label_drafts"),
        required=False,
    )
    include_submitted = forms.BooleanField(
        label=_("lists:registrations:filter_label_submitted"),
        required=False,
    )
    include_registered = forms.BooleanField(
        label=_("lists:registrations:filter_label_registered"),
        required=False,
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
        qs = Registration.objects.filter(created_by=user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OwnListForm(forms.Form):

    search = forms.CharField(
        max_length=200,
        required=False,
    )
    include_gw = forms.BooleanField(
        label="GW",
        required=False,
    )
    include_rebo = forms.BooleanField(
        label="REBO",
        required=False,
    )

class RSOListForm(OwnListForm):

    rso_officer = forms.ChoiceField(
        choices=[("", "Show all"), ],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_rso_choices()
        self.set_widget_attrs()

    def set_widget_attrs(self):
        widget = self.fields["rso_officer"].widget
        widget.attrs.update({
            "class": "form-control",
        })

    def set_rso_choices(self):
        from django.contrib.auth.models import Group
        try:
            rso = Group.objects.get(name="RSO")
        except Exception as e:
            raise ImproperlyConfigured("RSO group not found: create the group in django settings.")
        officers = rso.user_set.all()

        options = [(o.pk, nameget(o)) for o in officers]
        self.fields["rso_officer"].choices += options


class GrantAppList(
        LoginRequiredMixin,
        SearchableListView,
):
    model = None
    form_class = RSOListForm
    template_name = "lists/rso_list.html"
    paginate_by = 5
    rso_filter = True

    def sort(self, qs):
        return qs.order_by("-time_created")

    def filter_faculties(self, qs):
        "Return a base QS for selected faculties"
        faculty_dict = {"include_gw": "gw", "include_rebo": "rebo"}
        include = [value for key, value in faculty_dict.items() if key in self.request.GET.keys()]
        if len(include) != 1:
            # If none or both are checked, we include all
            return qs
        # There's only one faculty checked
        faculty = include[0]
        return qs.filter(faculty=faculty)

    def filter_officer(self, qs):
        officer = self.request.GET.get("rso_officer")
        if officer in ["", None]:
            return qs
        try:
            user_pk = int(officer)
        except Exception as e:
            breakpoint()
            return qs
        qs = qs.filter(
            rso_officer__pk=user_pk,
        )
        return qs

    def get_queryset(self,):
        return self.filter_qs(GrantApp.objects.all())

    def filter_qs(self, qs):
        "Filter faculties, then search the remainder and return a sorted QS"
        qs = self.filter_faculties(qs)
        qs = self.filter_officer(qs)
        qs = self.sort(qs)
        # Now check for search terms
        if "search" in self.request.GET.keys():
            search = self.request.GET["search"]
            if search != "":
                return grantapp_search(qs, search)
        return [GrantAppBlueprint(grantapp) for grantapp in qs]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(
            {"rso_filter": self.rso_filter}
        )
        return context


class GrantAppOwnList(GrantAppList):

    template_name = "lists/own_list.html"
    form = OwnListForm
    rso_filter = False

    def get_queryset(self,):
        qs = GrantApp.objects.filter(created_by=self.request.user)
        return self.filter_qs(qs)


def grantapp_search(qs, query):
    query = query.lower().split()
    results = set()

    def diminish(results, remaining):
        if remaining.count() == 0:
            return results
        bp = GrantAppBlueprint(remaining[0])
        txt = bp.full_text().lower()
        for q in query:
            if q not in txt:
                return diminish(results, remaining[1:])
        results.add(bp)
        return diminish(results, remaining[1:])
    return list(diminish(results, qs))
