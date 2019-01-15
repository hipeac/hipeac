import plotly.graph_objs as pgo
import plotly.offline as poff

from collections import OrderedDict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import generic
from django_countries import countries

from hipeac.models import Event, Registration, Institution


class EventStats(generic.TemplateView):
    """
    Shows general stats for a Event.
    """
    template_name = 'events/event/stats.html'
    Event = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, start_date__year=kwargs.get('year'), type=Event.CONFERENCE)
        if not (self.event.can_be_viewed_by(request.user) or request.user.is_staff):
            messages.error(request, 'You don\'t have the necessary permissions to view this page.')
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['plots'] = {}

        def get_basic_layout(title='Title'):
            return {
                # 'title': title,
                'height': 380,
                'margin': pgo.Margin(l=30, r=10, b=80, t=20, pad=5),
                'legend': {'x': 0, 'y': 1},
                'orientation': 0
            }

        def get_registrations_data(event):
            c = 0
            x = []
            y_dict = {}
            for r in Registration.objects \
                                 .filter(event_id=event.id) \
                                 .extra({'date': 'DATE(created_at)'}) \
                                 .values('date') \
                                 .order_by('date') \
                                 .annotate(count=Count('id')):
                c += r['count']
                delta = (r['date'] - event.start_date).days
                x.append(delta)
                y_dict[delta] = (c, r['count'])

            return [x, y_dict]

        def fill_the_gaps(range_days, data):
            """Returns an array for a range of dates, filling the gaps with existing data."""
            output = []
            c = 0
            last_day = sorted(data.keys())[-1]

            for d in range_days:
                c = data[d][0] if d in data else c

                if d > last_day:
                    break

                output.append(c)

            return output

        previous_conf = Event.objects.get(start_date__year=self.event.year - 1, type=self.event.type)
        registrations = {
            'previous': get_registrations_data(previous_conf),
            'current': get_registrations_data(self.event),
        }

        #
        # Show data with plot.ly
        #
        color_primary = '#1976D2'  # Blue 700
        color_secondary = '#B0BEC5'  # Blue Grey 200

        # -------------
        # REGISTRATIONS
        # -------------
        sorted_x = sorted(list(set(registrations['previous'][0] + registrations['current'][0])))
        sorted_x = list(range(sorted_x[0], sorted_x[-1] + 1))

        previous_trace = pgo.Scatter(
            x=sorted_x,
            y=fill_the_gaps(sorted_x, registrations['previous'][1]),
            name=previous_conf.year,
            line=dict(color=color_secondary, width=2, dash='dot')
        )
        current_trace = pgo.Scatter(
            x=sorted_x,
            y=fill_the_gaps(sorted_x, registrations['current'][1]),
            name=self.event.year,
            line=dict(color=color_primary, width=4)
        )

        layout = get_basic_layout('Registrations')
        layout.update({
            'annotations': [
                dict(
                    x=-(previous_conf.start_date.day - 1),
                    y=150,
                    xref='x',
                    yref='y',
                    text='Jan 1 %s' % previous_conf.year,
                    showarrow=True,
                    arrowhead=6,
                    arrowcolor=color_secondary,
                    ax=1,
                    ay=-40
                ),
                dict(
                    x=-(self.event.start_date.day - 1),
                    y=0,
                    xref='x',
                    yref='y',
                    text='Jan 1 %s' % self.event.year,
                    showarrow=True,
                    arrowhead=6,
                    arrowcolor=color_primary,
                    ax=1,
                    ay=-40
                )
            ]
        })

        figure = pgo.Figure(data=[current_trace, previous_trace], layout=layout)
        context['plots']['registrations'] = poff.plot(figure, auto_open=False, output_type='div')

        # ------
        # GENDER
        # ------

        def get_gender_data(event):
            y_dict = {1: 0, 2: 0, None: 0}
            for r in Registration.objects \
                                 .select_related('user') \
                                 .filter(event_id=event.id) \
                                 .values('user__profile__gender') \
                                 .order_by('user__profile__gender') \
                                 .annotate(count=Count('id')):
                y_dict[r['user__profile__gender']] = r['count']

            return [y_dict[1], y_dict[2], y_dict[None]]

        genders = ['Female', 'Male', '(not set)']

        previous_trace = pgo.Bar(
            x=genders,
            y=get_gender_data(previous_conf),
            name=previous_conf.year,
            marker=dict(color=color_secondary),
            opacity=0.6
        )
        current_trace = pgo.Bar(
            x=genders,
            y=get_gender_data(self.event),
            name=self.event.year,
            marker=dict(color=color_primary)
        )

        layout = get_basic_layout('Gender distribution')
        layout.update({
            'barmode': 'group',
            'xaxis': dict(tickangle=30),
        })

        figure = pgo.Figure(data=[current_trace, previous_trace], layout=layout)
        context['plots']['gender'] = poff.plot(figure, auto_open=False, output_type='div')

        # ----------
        # MEMBERSHIP
        # ----------

        def get_membership_data(event):
            y_dict = OrderedDict([
                ('MEMB', 0),
                ('ASSO', 0),
                ('AFFI', 0),
                ('APHD', 0),
                ('STAF', 0),
                (None, 0)
            ])
            for r in Registration.objects \
                                 .select_related('user') \
                                 .filter(event_id=event.id) \
                                 .values('user__profile__membership_tags') \
                                 .order_by('user__profile__membership_tags') \
                                 .annotate(count=Count('id')):
                y_dict[r['user__profile__membership_tags']] = r['count']

            return list(y_dict)

        membership_types = ['Member', 'Assoc. member', 'Affil. member', 'Affil. PhD', 'Staff', '(none)']

        previous_trace = pgo.Bar(
            x=membership_types,
            y=get_membership_data(previous_conf),
            name=previous_conf.year,
            marker=dict(color=color_secondary),
            opacity=0.6
        )
        current_trace = pgo.Bar(
            x=membership_types,
            y=get_membership_data(self.event),
            name=self.event.year,
            marker=dict(color=color_primary)
        )

        layout = get_basic_layout('Membership')
        layout.update({
            'barmode': 'group',
            'xaxis': dict(tickangle=30),
        })

        figure = pgo.Figure(data=[current_trace, previous_trace], layout=layout)
        context['plots']['membership'] = poff.plot(figure, auto_open=False, output_type='div')

        # ---------
        # COUNTRIES
        # ---------
        country_names = dict(countries)
        country_names['GB'] = 'UK'
        country_names['US'] = 'USA'

        def get_countries_data(event):
            y_odict = []
            for r in Registration.objects \
                                 .select_related('user__profile__institution') \
                                 .filter(event_id=event.id) \
                                 .values('user__profile__institution__country') \
                                 .order_by('-count', 'user__profile__institution__country') \
                                 .annotate(count=Count('id')):
                try:
                    y_odict.append((country_names[r['user__profile__institution__country']], r['count']))
                except Exception:
                    y_odict.append(('(not set)', r['count']))

            return OrderedDict(y_odict)

        previous_data = get_countries_data(self.event)
        previous_trace = pgo.Bar(
            x=list(previous_data.keys()),
            y=list(previous_data.values()),
            name=self.event.year,
            marker=dict(color=color_primary),
        )

        layout = get_basic_layout('Countries (institutions)')
        layout.update({
            'margin': pgo.Margin(l=20, r=0, b=100, t=20, pad=5),
            'barmode': 'group',
            'xaxis': dict(tickangle=-90),
        })

        figure = pgo.Figure(data=[previous_trace], layout=layout)
        context['plots']['countries'] = poff.plot(figure, auto_open=False, output_type='div')

        # -----------------
        # INSTITUTION TYPES
        # -----------------
        def get_institution_types_data(event):
            y_dict = OrderedDict([
                (Institution.SME, 0),
                (Institution.INDUSTRY, 0),
                (Institution.UNIVERSITY, 0),
                (Institution.LAB, 0),
                (Institution.INNOVATION, 0),
                (Institution.OTHER, 0)
            ])

            for r in Registration.objects \
                                 .select_related('user__profile__institution') \
                                 .filter(event_id=event.id) \
                                 .values('user__profile__institution__type') \
                                 .order_by('user__profile__institution__type') \
                                 .annotate(count=Count('id')):
                y_dict[r['user__profile__institution__type']] = r['count']

            return y_dict

        keys = ['SMEs', 'Industry', 'Universities', 'Labs', 'Innovation', 'Other']
        previous_trace = pgo.Bar(
            x=keys,
            y=list(get_institution_types_data(previous_conf).values()),
            name=previous_conf.year,
            marker=dict(color=color_secondary),
            opacity=0.6
        )
        current_trace = pgo.Bar(
            x=keys,
            y=list(get_institution_types_data(self.event).values()),
            name=self.event.year,
            marker=dict(color=color_primary)
        )

        layout = get_basic_layout('Institution types')
        layout.update({
            'barmode': 'group',
            'xaxis': dict(tickangle=30),
        })

        figure = pgo.Figure(data=[current_trace, previous_trace], layout=layout)
        context['plots']['institution_types'] = poff.plot(figure, auto_open=False, output_type='div')

        return context
