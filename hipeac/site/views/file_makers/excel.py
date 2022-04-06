import json

from typing import Dict, List

from hipeac.services.excel import ModelExcelWriter


class AbstractsSheet(ModelExcelWriter):
    def get_sheets(self) -> List[Dict]:
        qs = self.queryset.select_related("user__profile")
        base_data = ["uuid", "email", "first_name", "last_name", "affiliation", "country"]

        sheets = [
            {
                "title": "Abstract submissions",
                "data": [
                    base_data
                    + [
                        "title",
                        "authors",
                        "created_at",
                        "updated_at",
                        "is_accepted",
                    ]
                ],
            }
        ]

        custom_fields = []

        for obj in qs:
            for k in obj.custom_data.keys():
                if k not in custom_fields:
                    custom_fields.append(k)

        if custom_fields:
            sheets[0]["data"][0] = sheets[0]["data"][0] + custom_fields

        for obj in qs:
            uuid = str(obj.uuid)
            user_base_data = [
                uuid,
                obj.user.email,
                obj.user.first_name,
                obj.user.last_name,
                obj.user.profile.affiliation,
                obj.user.profile.country.name,
            ]

            # Abstract submissions

            abstract_data = [
                obj.title,
                obj.authors,
                obj.created_at.replace(tzinfo=None),
                obj.updated_at.replace(tzinfo=None),
                obj.is_accepted,
            ]

            # Custom fields

            if custom_fields:
                custom_data = []

                for f in custom_fields:
                    v = obj.custom_data[f] if f in obj.custom_data else None
                    custom_data.append(json.dumps(v) if type(v) in {dict, list} else v)

            sheets[0]["data"].append(user_base_data + abstract_data + custom_data)

        return sheets


class RegistrationsSheet(ModelExcelWriter):
    def get_sheets(self) -> List[Dict]:
        qs = self.queryset.select_related("user__profile", "coupon").prefetch_related("sessions")
        base_data = ["uuid", "email", "first_name", "last_name", "affiliation", "country"]

        sheets = [
            {
                "title": "Registrations",
                "data": [
                    base_data
                    + [
                        "fee_type",
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
                        "special_needs",
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
            {
                "title": "Custom fields",
                "data": [base_data],
            },
        ]

        event = None
        custom_fields = []
        session_ids = []
        session_fields = []

        for obj in qs:
            event = obj.event
            for k in obj.custom_data.keys():
                if k not in custom_fields:
                    custom_fields.append(k)

        if custom_fields:
            sheets[4]["data"][0] = sheets[3]["data"][0] + custom_fields
        else:
            del sheets[4]

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
                obj.user.profile.affiliation,
                obj.user.profile.country.name,
            ]

            # Registrations

            sheets[0]["data"].append(
                user_base_data
                + [
                    obj.fee_type,
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
                    obj.user.profile.custom_data.get("dietary", None),
                    obj.user.profile.custom_data.get("special_needs", None),
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

            # Custom fields

            if custom_fields:
                custom_data = []

                for f in custom_fields:
                    v = obj.custom_data[f] if f in obj.custom_data else None
                    custom_data.append(json.dumps(v) if type(v) in {dict, list} else v)

                sheets[4]["data"].append(user_base_data + custom_data)

            # Sessions

            session_data = []

            for session_id in session_ids:
                session_data.append(session_id in user_sessions)

            sheets[3]["data"].append(user_base_data + session_data)

        return sheets
