from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

Menu.add_item("main", MenuItem(_('main:menu:home'),
                               reverse('main:home'),
                               exact_url=True
                               ))

Menu.add_item("main", MenuItem(_('main:menu:my_list'),
                               reverse('registrations:my_list'),
                               exact_url=True
                               ))

Menu.add_item("main", MenuItem(_('main:menu:po_list'),
                               reverse('registrations:po_list'),
                               exact_url=True,
                               check=lambda x: "PO" in [
                                   g.name for g in x.user.groups.all()
                               ],
                               ))


Menu.add_item("footer", MenuItem(_('main:footer:login'),
                                 reverse('main:login'),
                                 check=lambda x: not x.user.is_authenticated
                                 ))

Menu.add_item("footer", MenuItem(_('main:footer:logout'),
                                 reverse('main:logout'),
                                 check=lambda x: x.user.is_authenticated
                                 ))
