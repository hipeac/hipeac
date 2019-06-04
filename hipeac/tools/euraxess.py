from commonmark import Parser, HtmlRenderer
from django.http import HttpResponse
from django.template.defaultfilters import date as date_filter
from lxml import etree

from hipeac.api.serializers import MetadataListField


class EuraxessXMLGenerator:
    organisation_id_key = '9999999-999999'
    datasource_key = 'datasource_key'
    encoding = 'utf-8'
    no_namespace_schema_location = 'http://euraxess.intrasoft-intl.com/api/schema/JobOpportunitySchema.xsd'
    xsi = 'http://www.w3.org/2001/XMLSchema-instance'

    def __init__(self, *, queryset):
        self._response = HttpResponse(content_type='text/xml')
        self.root = etree.Element('job-opportunities', nsmap={
            'xsi': self.xsi
        })
        self.root.set(etree.QName(self.xsi, 'noNamespaceSchemaLocation'), self.no_namespace_schema_location)
        self.root.set('datasourceKey', self.datasource_key)
        self.add_jobs(queryset=queryset)

    def add_jobs(self, *, queryset) -> None:
        metadata = MetadataListField()
        md_parser = Parser()
        md_renderer = HtmlRenderer()

        for job in queryset.select_related('institution').prefetch_related('links', 'institution__links'):
            el = etree.SubElement(self.root, 'job-opportunity')
            el.set('organisationIDKey', self.organisation_id_key)
            el.set('lastmodifieddate', date_filter(job.updated_at, 'c'))
            etree.SubElement(el, 'job-id').text = str(job.id)

            desc = etree.SubElement(el, 'description')
            extra_info = etree.SubElement(el, 'additional-information')
            institution = etree.SubElement(el, 'hiring-org-inst')
            location = etree.SubElement(el, 'work-location')
            email = etree.SubElement(el, 'application-details')

            # description

            etree.SubElement(desc, 'job-title').text = job.title
            etree.SubElement(desc, 'job-description').text = md_renderer.render(md_parser.parse(job.description))
            etree.SubElement(desc, 'job-status').text = str(job.employment_type)
            etree.SubElement(desc, 'application-deadline').text = date_filter(job.deadline, 'c')

            for topic in metadata.to_representation(job.topics):
                field = etree.SubElement(desc, 'research-field')
                etree.SubElement(field, 'main-research-field').text = 'Computer Science'
                etree.SubElement(field, 'sub-research-field').text = topic['value']

            for profile in metadata.to_representation(job.career_levels):
                etree.SubElement(desc, 'researcher-profile').text = profile['value']

            # additional-information

            etree.SubElement(extra_info, 'info-website').text = f'https://www.hipeac.net{job.get_absolute_url()}'

            # hiring-org-inst

            etree.SubElement(institution, 'organisation-institute').text = job.institution.name
            # etree.SubElement(institution, 'organisation-institute-type').text = str(job.institution.type)
            etree.SubElement(institution, 'country').text = job.institution.country.name
            if job.institution.location:
                etree.SubElement(institution, 'city').text = job.institution.location
            if job.institution.recruitment_email:
                etree.SubElement(institution, 'email').text = job.institution.recruitment_email
            for link in job.institution.links.all():
                etree.SubElement(institution, 'website').text = link.url

            # work-location

            etree.SubElement(location, 'nr-job-positions').text = str(job.positions)
            etree.SubElement(location, 'job-country').text = job.country.name
            etree.SubElement(location, 'job-city').text = job.location

            # application-details

            if job.email:
                etree.SubElement(email, 'how-to-apply').text = 'email'
                etree.SubElement(email, 'application-email').text = job.email

    @property
    def response(self) -> str:
        xml = etree.tostring(self.root, encoding=self.encoding, xml_declaration=True, pretty_print=True)
        self._response.filename = 'euraxess.xml'
        self._response.as_attachment = True
        self._response.write(xml)
        return self._response
