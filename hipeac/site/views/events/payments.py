from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic

from hipeac.models import Event, Coupon, Registration, AcacesRegistration, ConferenceRegistration, CswRegistration
from hipeac.services.payments.ingenico import Ingenico
from hipeac.site.emails.events import PaymentReminderEmail


def get_registration_object(id, *, key: str = "pk"):
    if key == "pk":
        reg = get_object_or_404(Registration.objects.select_related("event"), pk=id)
    elif key == "uuid":
        reg = get_object_or_404(Registration.objects.select_related("event"), uuid=id)

    RegistrationClass = {
        Event.ACACES: AcacesRegistration,
        Event.CONFERENCE: ConferenceRegistration,
        Event.CSW: CswRegistration,
    }[reg.event.type]

    return RegistrationClass.objects.get(pk=reg.id)


class RegistrationPaymentBaseView(generic.TemplateView):
    def dispatch(self, request, *args, **kwargs):
        if not self.get_object().event.allows_payments():
            messages.error(request, "Payments are not active for this event.")
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None) -> Registration:
        if not hasattr(self, "object"):
            self.object = get_registration_object(self.kwargs.get("pk"))
        return self.object

    def get_ingenico_result_url(self) -> str:
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        registration = self.get_object()
        ingenico = Ingenico(
            pspid=registration.event.wbs_element,
            salt=registration.event.ingenico_salt,
            test_mode=settings.DEBUG,
        )
        ingenico_parameters = {
            "AMOUNT": registration.remaining_fee,
            "ORDERID": registration.id,
            "RESULTURL": self.get_ingenico_result_url(),
        }
        context = super().get_context_data(**kwargs)
        context["registration"] = registration
        context["event"] = registration.event
        context["ingenico_url"] = ingenico.get_url()
        context["ingenico_parameters"] = ingenico.process_parameters(ingenico_parameters, registration.user)
        return context


class RegistrationPaymentView(RegistrationPaymentBaseView):
    """
    Perform payments using `payment.ugent.be` or coupons.
    """

    template_name = "__v3__/events/payments/registration_payment_form.html"

    def get_ingenico_result_url(self) -> str:
        return self.get_object().get_payment_result_url()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not self.get_object().editable_by_user(request.user):
            messages.error(request, "You don't have the necessary permissions to update this registration.")
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Check if the selected coupon is valid and update registration.
        """
        registration = self.get_object()
        try:
            coupon = Coupon.objects.get(code=request.POST.get("coupon"), event_id=registration.event_id)
            registration.coupon = coupon
            registration.save()
            messages.success(request, "Your coupon has been correctly applied.")
        except Coupon.DoesNotExist:
            messages.error(request, "Please check your coupon code. We can't find the one you've introduced.")
        except IntegrityError:
            messages.error(request, "Sorry but the coupon you have introduced has already been used.")
        except Exception as e:
            messages.error(request, "Error %s (%s)" % (e.message, type(e).__name__))
        return redirect(registration.get_payment_url())


class RegistrationPaymentDelegatedView(RegistrationPaymentBaseView):
    """
    Allows third parties to pay for a registration, without login.
    """

    template_name = "__v3__/events/payments/registration_payment_delegated_form.html"

    def get_object(self, queryset=None) -> Registration:
        if not hasattr(self, "object"):
            self.object = get_object_or_404(Registration.objects.select_related("event"), uuid=self.kwargs.get("uuid"))
        return self.object

    def get_ingenico_result_url(self) -> str:
        return self.get_object().get_payment_delegated_result_url()

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().secret != kwargs.get("secret"):
            messages.error(request, "You don't have access to this registration.")
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class RegistrationPaymentResultBaseView(generic.TemplateView):
    """
    Perform actions depending on the result of the payment process.
    """

    def get_object(self, queryset=None) -> Registration:
        if not hasattr(self, "object"):
            self.object = get_registration_object(self.kwargs.get("pk"))
        return self.object

    def dispatch(self, request, *args, **kwargs):
        registration = self.get_object()
        status = request.GET.get("STATUS")

        # Success
        if status in Ingenico.SUCCESS_STATUSES:
            if Ingenico.validate_out_parameters(request.GET, outsalt=registration.event.ingenico_salt):
                registration.paid = registration.paid + int(request.GET.get("AMOUNT"))
                registration.save()
                messages.success(request, "Your payment was succesful.")
            else:
                messages.error(request, "Invalid query parameters.")

        # Exception
        elif status in Ingenico.EXCEPTION_STATUSES:
            messages.warning(request, "We will revise your payment and let you know when it is authorized.")

        # Decline
        elif status in Ingenico.DECLINE_STATUSES:
            messages.error(request, "Your payment was declined.")

        # Cancel
        elif status in Ingenico.CANCEL_STATUSES:
            messages.warning(request, "Your payment has been canceled.")

        # ...and redirect
        return redirect(self.get_redirect_url())


class RegistrationPaymentResultView(RegistrationPaymentResultBaseView):
    def get_redirect_url(self) -> str:
        return self.get_object().get_payment_url()


class RegistrationPaymentDelegatedResultView(RegistrationPaymentResultBaseView):
    def get_object(self, queryset=None) -> Registration:
        if not hasattr(self, "object"):
            self.object = get_registration_object(self.kwargs.get("uuid"), key="uuid")
        return self.object

    def get_redirect_url(self) -> str:
        return reverse("done")


class RegistrationInvoiceRequestView(generic.RedirectView):
    def get_object(self, queryset=None) -> Registration:
        if not hasattr(self, "object"):
            self.object = get_registration_object(self.kwargs.get("pk"))
        return self.object

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        registration = self.get_object()
        if not registration.editable_by_user(request.user):
            messages.error(request, "You don't have the necessary permissions to update this registration.")
            raise PermissionDenied
        if not registration.event.allows_invoices:
            messages.error(request, "We cannot issue invoices for this event.")
            raise PermissionDenied
        registration.invoice_requested = True
        registration.save()
        PaymentReminderEmail(instance=registration).send()
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return self.get_object().get_payment_url()
