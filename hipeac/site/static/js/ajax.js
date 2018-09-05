var ajax = function () {
    return {
        head: function (url) {
            return $.ajax({
                method: 'HEAD',
                url: url
            });
        },
        options: function (url) {
            return $.ajax({
                method: 'OPTIONS',
                url: url
            });
        },
        get: function (url) {
            return $.ajax({
                method: 'GET',
                url: url
            });
        },
        post: function (url, data) {
            return $.ajax({
                method: 'POST',
                url: url,
                data: JSON.stringify(data),
                contentType: 'application/json; charset=utf-8',
                headers: {
                    'X-CSRFTOKEN': CSRF_TOKEN
                }
            });
        },
        put: function (url, data) {
            return $.ajax({
                method: 'PUT',
                url: url,
                data: JSON.stringify(data),
                contentType: 'application/json; charset=utf-8',
                headers: {
                    'X-CSRFTOKEN': CSRF_TOKEN
                }
            });
        },
        upload: function (url, formData) {
            return $.ajax({
                method: 'POST',
                url: url,
                data: formData,
                cache: false,
                contentType: false,
                enctype: 'multipart/form-data',
                processData: false,
                headers: {
                    'X-CSRFTOKEN': CSRF_TOKEN
                }
            });
        },
        delete: function (url) {
            return $.ajax({
                method: 'DELETE',
                url: url,
                headers: {
                    'X-CSRFTOKEN': CSRF_TOKEN
                }
            });
        }
    };
};

var api = function () {
    return {
        getQuotes: function (url) {
            return ajax().get('/api/v1/communication/quotes/');
        },
        getMetadata: function (url) {
            return ajax().get('/api/v1/metadata/');
        },
        getProjects: function (url) {
            return ajax().get('/api/v1/network/projects/');
        }
    };
};
