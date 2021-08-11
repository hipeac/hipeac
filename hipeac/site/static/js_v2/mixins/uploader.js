var UploaderMixin = {
  computed: {
    humanMaxFileSize: function () {
      var u = 0;
      var bytes = _.clone(this.maxFileSize);
      var units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];

      while (parseInt(bytes, 10) >= 1024 && u < units.length - 1) {
        bytes /= 1024;
        ++u;
      }

      return `${ bytes.toFixed(1) }${ units[ u ] }`;
      // return Quasar.humanStorageSize(this.maxFileSize);
    },
    uploadUrl: function () {
      if (!this.obj) return null;
      return this.obj.rel_files;
    }
  },
  methods: {
    removeFile: function (obj) {
      alert('NotImplementedError');
    },
    updateObj: function (obj) {
      alert('NotImplementedError');
    },
    uploaderFactory: function (files) {
      var filename = slugify(files[0].name).toLowerCase();
      return {
        url: this.uploadUrl,
        method: 'POST',
        sendRaw: true,
        headers: [
          { name: 'Content-Disposition', value: 'attachment; filename=' + filename },
          { name: 'X-CSRFTOKEN', value: document.querySelector('html').dataset.csrfToken }
        ]
      };
    },
    uploaded: function (data) {
      this.updateObj(JSON.parse(data.xhr.response));
      this.$refs.uploader.reset();
      Hipeac.utils.notifySuccess('File uploaded.');
    },
    uploadFailed: function (data) {
      Hipeac.utils.notifyApiError({
        response: {
          status: data.xhr.status,
          statusText: data.xhr.statusText,
          data: JSON.parse(data.xhr.response) || {}
        }
      });
    },
    uploadRejected: function (errors) {
      var hmfs = this.humanMaxFileSize;
      var res = errors.map(function (err) {
        return '"' + err.file.name + '" ' + ({
          'max-file-size': 'is too big (max. ' + hmfs + ').'
        }[err.failedPropValidation] || 'could not be uploaded.');
      });

      Hipeac.utils.notifyApiError({
        response: {
          status: 400,
          statusText: 'Bad Request',
          data: {
            files: res
          }
        }
      });
    }
  },
  mounted: function () {
    EventEmitter.on('hipeac-file-removed', this.removeFile);
  },
  unmounted: function () {
    EventEmitter.off('hipeac-file-removed');
  }
};
