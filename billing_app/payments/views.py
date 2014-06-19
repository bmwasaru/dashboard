import billing
from billing_app.models import MobileMoneyNumber  # noqa
from billing_app.models import StripeCustomer  # noqa
from billing_app.payments import forms as payment_forms  # noqa
from billing_app.payments import tables as payment_tables  # noqa
# from django.views import generic
# from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tables as horizon_tables  # noqa
#from horizon.views import APIView

stripe_obj = billing.get_integration("stripe")


class MobileNumberTableEntry():

    def __init__(self, id, number):
        self.id = id
        self.number = number
        self.name = number


class CardTableEntry():

    def __init__(self, id, name, is_default):
        self.id = id
        self.name = name
        self.default = is_default


class IndexView(horizon_tables.MultiTableView):
    template_name = 'billing_app/payments/index.html'
    table_classes = (payment_tables.StripeCardCustomerTable,
                     payment_tables.MobileMoneyTable)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['stripe_obj'] = stripe_obj
        return context

    def get_mobile_money_data(self):
        self._more = False
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
        self._more = False
        try:
            cards = [CardTableEntry(
                     x.id,
                     x.name,
                     x.is_default)
                     for x in StripeCustomer.objects.filter(
                     keystone_id__exact=self.request.user.id).order_by(
                         'is_default', 'id').reverse()]
        except Exception:
            cards = []
            exceptions.handle(self.request,
                              _('Unable to retrieve cards.'))
        return cards


class AddCardView(forms.ModalFormView):
    form_class = payment_forms.AddCardForm
    template_name = "billing_app/payments/add_card.html"
    success_url = "/billing/"

    def get_context_data(self, **kwargs):
        context = super(AddCardView, self).get_context_data(**kwargs)
        context['stripe_obj'] = stripe_obj
        return context


class CardPayView(forms.ModalFormView):
    form_class = payment_forms.CardPayForm
    template_name = "billing_app/payments/card_pay.html"
    success_url = "/billing/"

    def get_context_data(self, **kwargs):
        context = super(CardPayView, self).get_context_data(**kwargs)
        context['stripe_obj'] = stripe_obj
        return context


class AddMobileNumberView(forms.ModalFormView):
    form_class = payment_forms.AddMobileNumberForm
    template_name = "billing_app/payments/add_number.html"
    success_url = "/billing/"

    def get_context_data(self, **kwargs):
        context = super(AddMobileNumberView, self).get_context_data(**kwargs)
        context['stripe_obj'] = stripe_obj
        return context


class EnterTransactionCodeView(forms.ModalFormView):
    form_class = payment_forms.MobileTransactionCodeForm
    template_name = "billing_app/payments/mobile_transaction_code_entry.html"
    success_url = "/billing/"

    def get_context_data(self, **kwargs):
        context = super(
            EnterTransactionCodeView, self).get_context_data(**kwargs)
        context['stripe_obj'] = stripe_obj
        return context


class K2srv_v1(forms.ModalFormView):
    form_class = payment_forms.AddCardForm
    template_name = "billing_app/payments/k2v1.html"

    def get_context_data(self, **kwargs):
        context = super(K2srv_v1, self).get_context_data(**kwargs)
        return context
