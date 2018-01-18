from collections import namedtuple
from django.db.models import Q

from hipeac.apps.core.models import User, Institution, Profile


class Subscriber(namedtuple('Subscriber', 'email full_name')):
    def __str__(self):
        if self.full_name:
            return '%s %s'.format(self.email, self.full_name)
        else:
            return self.email


class SympaGenerator(object):
    def __init__(self):
        self.subscribers = []

    def get_subscribers(self, mailing_list):
        if mailing_list == 'industry':
            users = User.objects.active() \
                                .filter(membership_type__isnull=False, membership_revocation_date__isnull=True) \
                                .filter(Q(institution__institution_type__in=Institution.ALL_INDUSTRY) |
                                        Q(second_institution__institution_type__in=Institution.ALL_INDUSTRY))

        elif mailing_list == 'members':
            EC_id = 3132  # European Commission ID in our database; this won't ever change
            users = User.objects.active() \
                                .filter(Q(membership_type__isnull=False, membership_revocation_date__isnull=True) |
                                        Q(stakeholder_membership_date__isnull=False,
                                          stakeholder_membership_revocation_date__isnull=True) |
                                        Q(institution_id=EC_id, is_subscribed=True))

        elif mailing_list == 'phd':
            users = User.objects.active() \
                                .filter(is_subscribed=True) \
                                .filter(Q(profile_id=Profile.PHD_STUDENT) |
                                        Q(membership_type=User.MEMBERSHIP_AFFILIATED_PHD))

        elif mailing_list == 'publicity':
            users = User.objects.active().filter(is_subscribed=True)

        else:
            return []

        for user in users:
            self.subscribers.append(Subscriber(user.email, user.full_name))

        return [str(s) for s in self.subscribers]
