import csv

from django.http import HttpResponse


class CsvResponse(HttpResponse):

    def __init__(self, *args, filename: str = '', **kwargs):
        kwargs.setdefault('content_type', 'text/csv; charset=utf-8')
        super().__init__(*args, **kwargs)
        self['Content-Disposition'] = f'attachment; filename="{filename}"'


class CsvWriter:

    def __init__(self, *, filename: str):
        self._response = CsvResponse(filename=filename)
        self.writer = csv.writer(self._response)
        self.write_csv()

    def write_csv(self):
        raise NotImplementedError

    @property
    def response(self) -> CsvResponse:
        return self._response


class ModelCsvWriter(CsvWriter):
    model = None
    custom_fields = ()
    exclude = ()
    metadata_fields = ()

    def __init__(self, *, queryset, filename: str):
        self.queryset = self.optimize_queryset(queryset)
        super().__init__(filename=filename)

    def optimize_queryset(self, queryset):
        return queryset

    def get_value(self, obj, field):
        if field in self.metadata_fields:
            return obj.get_metadata_display(field)
        if field == 'country':
            return getattr(obj, field).name
        return getattr(obj, field)

    def get_fields(self):
        return list(self.custom_fields) + [f.name for f in self.model._meta.get_fields() if f.name not in self.exclude]

    def write_csv(self):
        fields = self.get_fields()
        self.writer.writerow(fields)

        for obj in self.queryset:
            self.writer.writerow([self.get_value(obj, f) for f in fields])
