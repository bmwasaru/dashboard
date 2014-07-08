from django.utils.translation import ugettext_lazy as _

import horizon

from billing_app import dashboard


class Transactions(horizon.Panel):
    name = _("Transaction History")
    slug = "history"


dashboard.Billing_App.register(Transactions)
