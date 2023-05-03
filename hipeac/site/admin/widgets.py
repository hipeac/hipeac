from django import forms


class MarkdownEditorWidget(forms.Textarea):
    template_name = "admin/widgets/toast_editor.html"

    class Media:
        ver = "3.2.2"
        js = (
            f"__v3__/vendor/toast-ui-editor@{ver}/toastui-editor-all.min.js",
            f"__v3__/vendor/toast-ui-editor@{ver}/django.js",
        )
        css = {"screen": (f"__v3__/vendor/toast-ui-editor@{ver}/toastui-editor.min.css",)}
