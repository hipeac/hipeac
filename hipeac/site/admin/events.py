from django.contrib import admin
from django.db.models import Count
from django.forms import ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe

from hipeac.forms import ApplicationAreasChoiceField, TopicsChoiceField
from hipeac.models import Event, Coupon, Registration, Roadshow, Break, Session, Sponsor
from .generic import ImagesInline, LinksInline, PermissionsInline


class BreaksInline(admin.TabularInline):
    model = Break
    classes = ('collapse',)
    extra = 0


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'value', 'notes')
    list_filter = ('event',)
    search_fields = ('code', 'notes')


class CouponsInline(admin.TabularInline):
    model = Coupon
    classes = ('collapse',)
    extra = 0


class SponsorsInline(admin.TabularInline):
    model = Sponsor
    classes = ('collapse',)
    extra = 0
    raw_id_fields = ('institution', 'project')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_date'
    list_display = ('id', 'start_date', 'end_date', 'name', 'type', 'sessions_link', 'registrations_link',
                    'is_active', 'is_open')
    list_filter = ('type',)
    list_per_page = 20

    readonly_fields = ('registrations_count',)
    inlines = (BreaksInline, SponsorsInline, CouponsInline, LinksInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(Count('sessions', distinct=True)) \
                                            .annotate(Count('registrations', distinct=True))

    def is_active(self, obj) -> bool:
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = 'Active'

    def is_open(self, obj) -> bool:
        return obj.is_open_for_registration()
    is_open.boolean = True
    is_open.short_description = 'Open'

    def registrations_link(self, obj):
        if obj.registrations__count == 0:
            return '-'
        url = reverse('admin:hipeac_registration_changelist')
        return mark_safe(f'<a href="{url}?event__id__exact={obj.id}">{obj.registrations__count}</a>')
    registrations_link.short_description = 'Registrations'

    def sessions_link(self, obj):
        if obj.sessions__count == 0:
            return '-'
        url = reverse('admin:hipeac_session_changelist')
        return mark_safe(f'<a href="{url}?event__id__exact={obj.id}">{obj.sessions__count}</a>')
    sessions_link.short_description = 'Sessions'


class RegistrationIsPaidFilter(admin.SimpleListFilter):
    title = 'payment status'
    parameter_name = 'paid'

    def lookups(self, request, model_admin):
        return (
            ('y', 'Paid'),
            ('c', 'Paid, using a coupon'),
            ('n', 'Not paid, no invoice'),
            ('i', 'Not paid, but requested invoice'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'y':
            return queryset.filter(saldo__gte=0)
        elif self.value() == 'c':
            return queryset.filter(saldo__gte=0, coupon__isnull=False)
        elif self.value() == 'n':
            return queryset.filter(saldo__lt=0, invoice_requested=False)
        elif self.value() == 'i':
            return queryset.filter(saldo__lt=0, invoice_requested=True)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('id', 'created_at', 'user', 'fee', 'with_coupon', 'invoice_requested', 'invoice_sent',
                    'visa_requested', 'visa_sent')
    list_filter = (RegistrationIsPaidFilter, 'invoice_requested', 'invoice_sent', 'visa_requested', 'visa_sent',
                   'event')

    raw_id_fields = ('coupon',)
    readonly_fields = ('event', 'user', 'base_fee', 'extra_fees', 'paid', 'saldo')
    fieldsets = (
        (None, {
            'fields': ('event', ('user', 'visa_requested', 'visa_sent')),
        }),
        ('PAYMENT', {
            'fields': ('fee_type', 'base_fee', 'extra_fees', ('paid_via_invoice', 'invoice_requested', 'invoice_sent'), 'coupon',
                       'paid', 'saldo'),
        }),
        ('EXTRA INFORMATION', {
            'fields': ('with_booth',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user__profile', 'coupon').prefetch_related('event')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        instance = Registration.objects.get(pk=object_id)
        extra_context = extra_context or {}
        extra_context['is_paid'] = instance.is_paid
        extra_context['base_fee'] = instance.base_fee
        extra_context['remaining_fee'] = instance.remaining_fee
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def fee(self, obj):
        return f'{obj.base_fee} + {obj.extra_fees}'

    def with_coupon(self, obj):
        return obj.coupon is not None
    with_coupon.boolean = True


@admin.register(Roadshow)
class RoadshowAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_date'
    list_display = ('id', 'name', 'country', 'start_date', 'end_date')

    inlines = (ImagesInline, LinksInline)


class SessionAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField()
    topics = TopicsChoiceField()


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    form = SessionAdminForm

    date_hierarchy = 'date'
    list_display = ('id', 'title', 'date', 'start_at', 'end_at', 'session_type')
    list_filter = ('session_type', 'event')
    search_fields = ('title',)

    autocomplete_fields = ('projects',)
    radio_fields = {'session_type': admin.VERTICAL}
    raw_id_fields = ('main_speaker',)
    inlines = [LinksInline, PermissionsInline]
    fieldsets = (
        (None, {
            'fields': (('date', 'start_at', 'end_at'), 'session_type', 'title', 'is_private'),
        }),
        ('INFO', {
            'fields': ('main_speaker', 'summary', 'projects', 'organizers'),
        }),
        ('METADATA', {
            'classes': ('collapse',),
            'fields': ('application_areas', 'topics'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('event', 'session_type')
