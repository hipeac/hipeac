import csv

from django.http import HttpResponse


class CsvResponse(HttpResponse):

    def __init__(self, *args, filename: str = '', **kwargs):
        kwargs.setdefault('content_type', 'text/csv; charset=utf-8')
        super().__init__(*args, **kwargs)
        self['Content-Disposition'] = f'attachment; filename="{filename}"'


class CsvWriter:

    def __init__(self, *, queryset, filename: str):
        self._response = CsvResponse(filename=filename)
        self.queryset = queryset
        self.writer = csv.writer(self._response)
        self.write_csv()

    def write_csv(self):
        raise NotImplementedError

    @property
    def response(self) -> CsvResponse:
        return self._response


class ModelCsvWriter(CsvWriter):
    model = None
    exclude = ()
    metadata_fields = ()

    def get_value(self, obj, field):
        if field in self.metadata_fields:
            return obj.get_metadata_display(field)
        return getattr(obj, field)

    def get_fields(self):
        return [f.name for f in self.model._meta.get_fields() if f.name not in self.exclude]

    def write_csv(self):
        fields = self.get_fields()
        self.writer.writerow(fields)

        for obj in self.queryset:
            self.writer.writerow([self.get_value(obj, f) for f in fields])
