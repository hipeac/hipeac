from django.http import HttpResponse
from openpyxl import Workbook
from tempfile import NamedTemporaryFile
from typing import Dict, List


class ExcelResponse(HttpResponse):
    def __init__(self, *args, filename: str = "", **kwargs):
        kwargs.setdefault(
            "content_type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet; charset=utf-8"
        )
        super().__init__(*args, **kwargs)
        self["Content-Disposition"] = f'attachment; filename="{filename}"'


class ModelExcelWriter:
    def __init__(self, *, queryset, filename: str):
        self.queryset = queryset
        self.filename = filename

    def get_sheets(self) -> List[Dict]:
        raise NotImplementedError

    @property
    def response(self) -> ExcelResponse:
        wb = Workbook(write_only=True)

        for sheet in self.get_sheets():
            ws = wb.create_sheet(title=sheet["title"])
            for entry in sheet["data"]:
                ws.append(entry)

        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()

        return ExcelResponse(stream, filename=self.filename)
