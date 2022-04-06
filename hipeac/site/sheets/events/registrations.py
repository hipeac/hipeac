from typing import Dict, List

from hipeac.services.excel import ModelExcelWriter


class RegistrationsSheet(ModelExcelWriter):
    def get_sheets(self) -> List[Dict]:
        qs = self.queryset.select_related("user__profile__institution", "coupon").prefetch_related(
            "sessions", "user__profile__gender", "user__profile__meal_preference"
        )
        base_data = ["uuid", "email", "first_name", "last_name", "affiliation", "country", "gender"]

        sheets = [
            {
                "title": "Registrations",
                "data": [
                    base_data
                    + [
                        "base_fee",
                        "extra_fees",
                        "manual_extra_fees",
                        "coupon",
                        "invoice_requested",
                        "invoice_sent",
                        "paid",
                        "paid_via_invoice",
                        "saldo",
                        "created_at",
                        "updated_at",
                    ]
                ],
            },
            {
                "title": "Dietary",
                "data": [
                    base_data
                    + [
                        "dietary_requirements",
                    ]
                ],
            },
            {
                "title": "Visum",
                "data": [
                    base_data
                    + [
                        "visa_requested",
                        "visa_sent",
                    ]
                ],
            },
            {
                "title": "Sessions",
                "data": [base_data],
            },
        ]

        event = qs.first().event
        session_ids = []
        session_fields = []

        for session in event.sessions.all():
            session_ids.append(session.id)
            session_fields.append(session.title)

        sheets[3]["data"][0] = sheets[3]["data"][0] + session_fields

        for obj in qs:
            uuid = str(obj.uuid)
            user_sessions = {s.id for s in obj.sessions.all()}
            user_base_data = [
                uuid,
                obj.user.email,
                obj.user.first_name,
                obj.user.last_name,
                str(obj.user.profile.institution),
                obj.user.profile.country.name,
                str(obj.user.profile.gender),
            ]

            # Registrations

            sheets[0]["data"].append(
                user_base_data
                + [
                    obj.base_fee,
                    obj.extra_fees,
                    obj.manual_extra_fees,
                    str(obj.coupon),
                    obj.invoice_requested,
                    obj.invoice_sent,
                    obj.paid,
                    obj.paid_via_invoice,
                    obj.saldo,
                    obj.created_at.replace(tzinfo=None),
                    obj.updated_at.replace(tzinfo=None),
                ]
            )

            # Dietary

            sheets[1]["data"].append(
                user_base_data
                + [
                    str(obj.user.profile.meal_preference),
                ]
            )

            # Visum

            if obj.visa_requested:
                sheets[2]["data"].append(
                    user_base_data
                    + [
                        obj.visa_requested,
                        obj.visa_sent,
                    ]
                )

            # Sessions

            session_data = []

            for session_id in session_ids:
                session_data.append(session_id in user_sessions)

            sheets[3]["data"].append(user_base_data + session_data)

        return sheets
