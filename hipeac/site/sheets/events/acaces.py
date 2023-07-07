from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify
from typing import Dict, List

from hipeac.models.events.acaces import AcacesBus
from hipeac.services.excel import ModelExcelWriter


class AcacesBusSheet(ModelExcelWriter):
    destination = None

    def get_sheets(self) -> List[Dict]:
        acaces = self.queryset
        base_data = ["attendee", "num_people", "phone_number", "extra_info"]
        sheets = []

        if self.destination == AcacesBus.DESTINATION_HOME:
            base_data += ["hotel"]

        for bus in AcacesBus.objects.filter(event_id=acaces.id, destination=self.destination):
            data = [[bus.name], [], base_data]
            registrations = {
                AcacesBus.DESTINATION_SCHOOL: bus.registrations_arriving.filter(accepted=True),
                AcacesBus.DESTINATION_HOME: bus.registrations_departing.filter(accepted=True),
            }[self.destination]
            total_people = 0

            for registration in (
                registrations.select_related("user")
                .prefetch_related("accompanying_persons", "assigned_hotel")
                .order_by("user__first_name", "user__last_name")
            ):
                num_people = 1 + registration.accompanying_persons.count()
                total_people += num_people
                data.append(
                    [
                        f"{registration.user.first_name} {registration.user.last_name}",
                        num_people,
                        registration.phone_number,
                        registration.arrival_flight
                        if self.destination == AcacesBus.DESTINATION_SCHOOL
                        else registration.departure_flight,
                        registration.user.email
                        if self.destination == AcacesBus.DESTINATION_SCHOOL
                        else f"{registration.assigned_hotel}",
                    ]
                )

            data.append(["", total_people])

            sheets.append({"title": slugify(bus.name)[:30], "data": data})

        no_bus = {
            AcacesBus.DESTINATION_SCHOOL: acaces.registrations.filter(
                acacesregistration__accepted=True, acacesregistration__arrival_bus=None
            ),
            AcacesBus.DESTINATION_HOME: acaces.registrations.filter(
                acacesregistration__accepted=True, acacesregistration__departure_bus=None
            ),
        }[self.destination]
        no_bus_data = [["(Not set)"], [], base_data]

        for registration in no_bus.select_related("user").order_by("user__first_name", "user__last_name"):
            no_bus_data.append(
                [
                    f"{registration.user.first_name} {registration.user.last_name}",
                    1 + registration.accompanying_persons.count(),
                    "",
                    "",
                ]
            )

        sheets.append({"title": "--not-set--", "data": no_bus_data})

        return sheets


class AcacesArrivalBusSheet(AcacesBusSheet):
    destination = AcacesBus.DESTINATION_SCHOOL


class AcacesDepartureBusSheet(AcacesBusSheet):
    destination = AcacesBus.DESTINATION_HOME


class AcacesHotelSheet(ModelExcelWriter):
    def get_sheets(self) -> List[Dict]:
        acaces = self.queryset

        base_data = ["attendee", "phone_number"]
        sheets = []

        for hotel in acaces.hotels.all():
            data = [
                [hotel.name],
                [],
                ["attendee", "phone_number", "roommate"] if "twin" in hotel.name.lower() else base_data,
            ]

            added = set()

            for registration in hotel.registrations.filter(accepted=True).order_by(
                "user__first_name", "user__last_name"
            ):
                if registration.id in added:
                    continue

                if registration.roommate:
                    data.append(
                        [
                            f"{registration.user.first_name} {registration.user.last_name}",
                            registration.phone_number,
                            f"{registration.roommate.user.first_name} {registration.roommate.user.last_name}",
                        ]
                    )
                    added.add(registration.roommate_id)
                else:
                    data.append(
                        [
                            f"{registration.user.first_name} {registration.user.last_name}",
                            registration.phone_number,
                        ]
                    )

            sheets.append({"title": hotel.code, "data": data})

        return sheets


class AcacesLunchSheet(ModelExcelWriter):
    def get_sheets(self) -> List[Dict]:
        acaces = self.queryset

        base_data = ["attendee", "dietary_requirements"]
        sheets = []
        accompanying_data = [[""], ["Accompanying persons"], ["name", "dietary_requirements"]]

        data = [
            ["Dietary requirements"],
            [],
            ["Attendees"],
            base_data,
        ]

        for registration in (
            acaces.registrations.filter(acacesregistration__accepted=True)
            .order_by("user__first_name", "user__last_name")
            .select_related("user__profile")
            .prefetch_related("user__profile__meal_preference")
        ):
            data.append(
                [
                    f"{registration.user.first_name} {registration.user.last_name}",
                    f"{registration.user.profile.meal_preference}",
                ]
            )

            if registration.accompanying_persons.count() > 0:
                for person in registration.accompanying_persons.prefetch_related("meal_preference"):
                    accompanying_data.append(
                        [
                            person.name,
                            f"{person.meal_preference}",
                        ]
                    )

        data.extend(accompanying_data)

        sheets.append({"title": "Dietary requirements", "data": data})

        return sheets


class AcacesCourseSheet(ModelExcelWriter):
    def get_sheets(self) -> List[Dict]:
        acaces = self.queryset

        base_data = ["attendee", "email"]
        sheets = []

        for course in acaces.courses.all():
            data = [
                [f"Slot {course.slot}: {course.title}"],
                [],
                base_data,
            ]

            for registration in (
                course.registrations.filter(accepted=True)
                .order_by("user__first_name", "user__last_name")
                .select_related("user")
            ):
                data.append(
                    [
                        f"{registration.user.first_name} {registration.user.last_name}",
                        registration.user.email,
                    ]
                )

            sheets.append({"title": slugify(f"slot-{course.slot}-{course.title}")[:30], "data": data})

        return sheets


class AcacesRegistrationsSheet(ModelExcelWriter):
    def get_sheets(self) -> List[Dict]:
        acaces = self.queryset

        data = [
            [
                "badge_1",
                "badge_2",
                "country",
                "poster_title",
                "poster_authors",
                "s1c1",
                "l1",
                "s2c1",
                "l2",
                "s3c1",
                "l3",
                "s4c1",
                "l4",
            ]
        ]
        sheets = []

        for registration in acaces.registrations.filter(
            acacesregistration__status=1, acacesregistration__accepted=True
        ):
            user_data = [
                registration.user.profile.name,
                str(registration.user.profile.institution),
                registration.user.profile.institution.country.name
                if registration.user.profile.institution and registration.user.profile.institution.country
                else "",
            ]

            try:
                poster = registration.acacesregistration.poster
            except ObjectDoesNotExist:
                poster = None

            if poster:
                user_data.append(poster.title)
                user_data.append(poster.authors)
            else:
                user_data.append("")
                user_data.append("")

            for slot in range(1, 5):
                course = registration.acacesregistration.courses.filter(slot=slot).first()
                if course:
                    user_data.append(course.title)
                    user_data.append(", ".join([user.profile.name for user in course.teachers]))
                else:
                    user_data.append("")
                    user_data.append("")

            data.append(user_data)

        sheets.append({"title": "Courses", "data": data})

        return sheets
