from django.contrib import admin, messages
from django.db.models import Count
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from hipeac.forms import ApplicationAreasChoiceField, TopicsChoiceField
from hipeac.models import Profile, Event, Coupon, Registration, Roadshow, Break, Session, Sponsor, Venue, Room
from .generic import ImagesInline, LinksInline, PermissionsInline
from .users import ProfileCsvWriter


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
    actions = ('select_export_users_csv',)
    date_hierarchy = 'start_date'
    list_display = ('id', 'start_date', 'end_date', 'name', 'type', 'sessions_link', 'registrations_link',
                    'is_active', 'is_open')
    list_filter = ('type',)
    list_per_page = 20
    search_fields = ('city', 'country', 'start_date__year')

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

    def select_export_users_csv(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, 'Please select only one event.')
            return
        ids = queryset.first().registrations.values_list('user_id', flat=True)
        return ProfileCsvWriter(filename='hipeac-jobs.csv', queryset=Profile.objects.filter(user_id__in=ids)).response
    select_export_users_csv.short_description = '[CSV] Export attendees data for an event'


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
    list_display = ('id', 'created_at', 'name', 'fee', 'is_paid', 'with_coupon', 'invoice_requested', 'invoice_sent',
                    'visa_requested', 'visa_sent')
    list_filter = (RegistrationIsPaidFilter, 'invoice_requested', 'invoice_sent', 'visa_requested', 'visa_sent',
                   'event')
    search_fields = ('id', 'user__email', 'user__username', 'user__first_name', 'user__last_name')

    raw_id_fields = ('coupon',)
    readonly_fields = ('event', 'user', 'base_fee', 'extra_fees', 'paid', 'saldo')
    fieldsets = (
        (None, {
            'fields': ('event', ('user', 'visa_requested', 'visa_sent')),
        }),
        ('PAYMENT', {
            'fields': ('fee_type', 'base_fee', 'extra_fees', ('paid_via_invoice', 'invoice_requested', 'invoice_sent'),
                       'coupon', 'paid', 'saldo'),
        }),
        ('EXTRA INFORMATION', {
            'fields': ('with_booth',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user__profile__institution', 'coupon') \
                                            .prefetch_related('event')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        instance = Registration.objects.get(pk=object_id)
        extra_context = extra_context or {}
        extra_context['is_paid'] = instance.is_paid
        extra_context['base_fee'] = instance.base_fee
        extra_context['remaining_fee'] = instance.remaining_fee
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def name(self, obj):
        institution = obj.user.profile.institution.short_name if obj.user.profile.institution else '-'
        url = reverse('admin:hipeac_profile_changelist')
        return format_html(
            f'<a href="{url}{obj.user_id}/" target="admin_user">{obj.user.profile.name}</a>, {institution}'
        )

    def fee(self, obj):
        return format_html(f'{obj.base_fee}&nbsp;+&nbsp;{obj.extra_fees}')

    def is_paid(self, obj) -> bool:
        return obj.is_paid
    is_paid.boolean = True
    is_paid.short_description = 'Paid'

    def with_coupon(self, obj):
        return obj.coupon is not None
    with_coupon.boolean = True
    with_coupon.short_description = 'Coupon'


@admin.register(Roadshow)
class RoadshowAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_date'
    list_display = ('id', 'name', 'country', 'start_date', 'end_date')

    inlines = (ImagesInline, LinksInline)


class SessionAdminForm(ModelForm):
    application_areas = ApplicationAreasChoiceField(required=False)
    topics = TopicsChoiceField(required=False)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    form = SessionAdminForm

    actions = ('select_export_users_csv',)
    date_hierarchy = 'date'
    list_display = ('id', 'title', 'date', 'start_at', 'end_at', 'session_type', 'registrations_count')
    list_filter = ('session_type', 'event')
    search_fields = ('title',)

    autocomplete_fields = ('event', 'projects')
    radio_fields = {'session_type': admin.VERTICAL}
    raw_id_fields = ('main_speaker',)
    inlines = [LinksInline, PermissionsInline]
    fieldsets = (
        (None, {
            'fields': ('event', ('date', 'start_at', 'end_at'), 'session_type', 'title', 'is_private'),
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
        return super().get_queryset(request).prefetch_related('event', 'session_type') \
                                            .annotate(Count('registrations', distinct=True))

    def registrations_count(self, obj):
        return obj.registrations__count if obj.registrations__count > 0 else '-'
    registrations_count.short_description = 'Registrations'

    def select_export_users_csv(self, request, queryset):
        if queryset.count() > 1:
            messages.error(request, 'Please select only one session.')
            return
        ids = queryset.first().registrations.values_list('user_id', flat=True)
        return ProfileCsvWriter(filename='hipeac-jobs.csv', queryset=Profile.objects.filter(user_id__in=ids)).response
    select_export_users_csv.short_description = '[CSV] Export attendees data for a session'


class RoomsInline(admin.TabularInline):
    model = Room
    extra = 0


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'country')
    search_fields = ('name', 'city', 'country')

    inlines = (ImagesInline, LinksInline)
