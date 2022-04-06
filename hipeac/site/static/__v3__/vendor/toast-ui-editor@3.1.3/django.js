window.django_toast_editor = {
  initEditor: function (textarea, target) {
    var textareaEl = document.querySelector(textarea);
    textareaEl.style.display = 'none';

    var editor = new toastui.Editor({
      el: document.querySelector(target),
      initialValue: textareaEl.value,
      initialEditType: 'markdown',
      previewStyle: 'vertical',
      toolbarItems: [
        ['bold', 'italic', 'strike'],
        ['quote'],
        ['ul', 'ol'],
        ['image', 'link'],
      ]
    });

    editor.on('change', function () {
      textareaEl.value = editor.getMarkdown();
    });

    return editor;
  }
};
