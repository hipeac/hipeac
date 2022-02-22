from commonmark import Parser, HtmlRenderer
from datetime import datetime
from django.http import HttpResponse
from django.template.defaultfilters import date as date_filter
from lxml import etree
from typing import List

from hipeac.api.serializers import MetadataListFieldWithEuraxess
from hipeac.models import Institution


class EuraxessXMLGenerator:
    organisation_id_key = "406359-507680"
    datasource_key = "d22ff6df705c4afcc0a7279b6ebd953a"
    encoding = "utf-8"
    no_namespace_schema_location = "https://euraxess.ec.europa.eu/api/schema/JobOpportunitySchema.xsd"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"

    def __init__(self, *, queryset):
        self._response = HttpResponse(content_type="text/xml")
        self.root = etree.Element("job-opportunities", nsmap={"xsi": self.xsi})
        self.root.set(etree.QName(self.xsi, "noNamespaceSchemaLocation"), self.no_namespace_schema_location)
        self.root.set("datasourceKey", self.datasource_key)
        self.add_jobs(queryset=queryset)

    @staticmethod
    def parse_topics(topics: List) -> List[str]:
        """Given a list of topics, it returns a list of unique Euraxess values."""
        output = []
        for topic in topics:
            output.extend(topic["euraxess_value"].split(",") if topic["euraxess_value"] else [])
        return list(set(output))

    def add_jobs(self, *, queryset) -> None:
        metadata = MetadataListFieldWithEuraxess()
        md_parser = Parser()
        md_renderer = HtmlRenderer()

        for job in (
            queryset.filter(add_to_euraxess=True)
            .select_related("institution")
            .prefetch_related("links", "institution__links", "project__programme")
        ):
            el = etree.SubElement(self.root, "job-opportunity")
            el.set("organisationIDKey", self.organisation_id_key)
            el.set("lastmodifieddate", date_filter(job.updated_at, "c"))
            etree.SubElement(el, "job-id").text = str(job.id)

            # description

            desc = etree.SubElement(el, "description")
            etree.SubElement(desc, "job-title").text = job.title
            etree.SubElement(desc, "job-description").text = md_renderer.render(md_parser.parse(job.description))

            job_topics = self.parse_topics(metadata.to_representation(job.topics))
            if len(job_topics) == 0:
                field = etree.SubElement(desc, "research-field")
                etree.SubElement(field, "main-research-field").text = "Computer science"
                etree.SubElement(field, "sub-research-field").text = "Other"
            else:
                for topic in job_topics:
                    field = etree.SubElement(desc, "research-field")
                    etree.SubElement(field, "main-research-field").text = "Computer science"
                    etree.SubElement(field, "sub-research-field").text = topic

            researcher_profiles = self.parse_topics(metadata.to_representation(job.career_levels))
            if len(researcher_profiles) == 0:
                etree.SubElement(desc, "researcher-profile").text = "Established Researcher (R3)"  # TODO: check default
            else:
                for profile in researcher_profiles:
                    etree.SubElement(desc, "researcher-profile").text = profile

            etree.SubElement(desc, "type-of-contract").text = "To be defined"
            etree.SubElement(desc, "job-status").text = "Negotiable"
            etree.SubElement(desc, "application-deadline").text = date_filter(
                datetime.combine(job.deadline, datetime.min.time()), "c"
            )

            # additional-information

            extra_info = etree.SubElement(el, "additional-information")
            etree.SubElement(extra_info, "info-website").text = f"https://www.hipeac.net{job.get_absolute_url()}"

            # eu-funding

            eu_funding = etree.SubElement(el, "eu-funding")
            if job.project and job.project.programme:
                etree.SubElement(eu_funding, "framework-programme").text = job.project.programme.euraxess_value
            else:
                etree.SubElement(eu_funding, "framework-programme").text = "No"

            # work-location

            location = etree.SubElement(el, "work-location")
            etree.SubElement(location, "nr-job-positions").text = str(job.positions)
            etree.SubElement(location, "job-organisation-institute").text = job.institution.name
            etree.SubElement(location, "job-country").text = job.country.name
            etree.SubElement(location, "job-city").text = job.location

            # hiring-org-inst

            organisation_type = {
                Institution.UNIVERSITY: "Higher Education Institute",
                Institution.LAB: "Research Laboratory",
                Institution.INNOVATION: "Public Research Institution",
                Institution.INDUSTRY: "Large Company",
                Institution.SME: "Small Medium Enterprise, Start-up",
                Institution.OTHER: "Other",
            }[job.institution.type]

            institution = etree.SubElement(el, "hiring-org-inst")
            etree.SubElement(institution, "organisation-institute").text = job.institution.name
            etree.SubElement(institution, "organisation-institute-type").text = organisation_type
            etree.SubElement(institution, "country").text = job.institution.country.name
            if job.institution.location:
                etree.SubElement(institution, "city").text = job.institution.location
            if job.institution.recruitment_email:
                etree.SubElement(institution, "e-mail").text = job.institution.recruitment_email
            for link in job.institution.links.all():
                etree.SubElement(institution, "website").text = link.url

            # application-details

            application_website = None

            for link in job.links.all():
                if link.type == "website":
                    application_website = link.url

            if application_website:
                application_details = etree.SubElement(el, "application-details")
                etree.SubElement(application_details, "how-to-apply").text = "website"
                etree.SubElement(application_details, "application-website").text = application_website
            elif job.email:
                application_details = etree.SubElement(el, "application-details")
                etree.SubElement(application_details, "how-to-apply").text = "e-mail"
                etree.SubElement(application_details, "application-email").text = job.email

    @property
    def response(self) -> str:
        xml = etree.tostring(self.root, encoding=self.encoding, xml_declaration=True, pretty_print=True)
        self._response.filename = "euraxess.xml"
        self._response.as_attachment = True
        self._response.write(xml)
        return self._response
