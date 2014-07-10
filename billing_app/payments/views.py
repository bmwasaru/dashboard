from accounting import managers
import billing
from billing_app.models import Card  # noqa
from billing_app.models import MobileMoneyNumber  # noqa
from billing_app.payments import forms as payment_forms  # noqa
from billing_app.payments import tables as payment_tables  # noqa
from django.conf import settings
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tables as horizon_tables  # noqa


class MobileNumberTableEntry():

    def __init__(self, id, number):
        self.id = id
        self.number = number
        self.name = number


class CardTableEntry():

    def __init__(self, id, name, default):
        self.id = id
        self.name = name
        self.default = default


class PaymentViewBase(forms.ModalFormView):
    success_url = urlresolvers.reverse_lazy('horizon:billing:payments:index')


class IndexView(horizon_tables.MultiTableView):
    template_name = 'billing_app/payments/index.html'
    table_classes = (payment_tables.StripeCardCustomerTable,
                     payment_tables.MobileMoneyTable)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['stripe_obj'] = billing.get_integration('stripe')
        if not managers.AccountManager().has_sufficient_balance(
                self.request.user.tenant_id):
            messages.warning(self.request,
                          u'You need at least {0} USD to launch an instance'.
                          format(settings.MINIMUM_BALANCE))
        return context

    def get_mobile_money_data(self):
        try:
            mobile_numbers = [MobileNumberTableEntry(
                x.id,
                x.number)
                for x in MobileMoneyNumber.objects.filter(
                    keystone_id__exact=self.request.user.id)]
        except Exception:
            mobile_numbers = []
            exceptions.handle(self.request,
                              _('Unable to retrieve numbers.'))
        return mobile_numbers

    def get_cards_data(self):
        try:
            cards = [CardTableEntry(
                     x.id,
                     x.name,
                     x.default)
                     for x in Card.objects.filter(
                     tenant_id__exact=self.request.user.tenant_id).order_by(
                         'default', 'id').reverse()]
        except Exception:
            cards = []
            exceptions.handle(self.request,
                              _('Unable to retrieve cards.'))
        return cards


class AddCardView(PaymentViewBase):
    form_class = payment_forms.AddCardForm
    template_name = "billing_app/payments/add_card.html"

    def get_context_data(self, **kwargs):
        context = super(AddCardView, self).get_context_data(**kwargs)
        context['stripe_obj'] = billing.get_integration('stripe')
        return context


class CardPayView(PaymentViewBase):
    form_class = payment_forms.CardPayForm
    template_name = "billing_app/payments/card_pay.html"

    def get_context_data(self, **kwargs):
        context = super(CardPayView, self).get_context_data(**kwargs)
        context['stripe_obj'] = billing.get_integration('stripe')
        return context


class AddMobileNumberView(PaymentViewBase):
    form_class = payment_forms.AddMobileNumberForm
    template_name = "billing_app/payments/add_number.html"


class EnterTransactionCodeView(PaymentViewBase):
    form_class = payment_forms.MobileTransactionCodeForm
    template_name = "billing_app/payments/mobile_transaction_code_entry.html"


class K2srv_v1(forms.ModalFormView):
    form_class = payment_forms.AddCardForm
    template_name = "billing_app/payments/k2v1.html"
