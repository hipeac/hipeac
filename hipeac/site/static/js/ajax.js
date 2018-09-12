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
        getAllProjects: function () {
            return ajax().get('/api/v1/network/projects/all/');
        },
        getAllInstitutions: function () {
            return ajax().get('/api/v1/network/institutions/all/');
        },
        getArticles: function () {
            return ajax().get('/api/v1/communication/articles/');
        },
        getQuotes: function () {
            return ajax().get('/api/v1/communication/quotes/');
        },
        getEvents: function () {
            return ajax().get('/api/v1/events/events/');
        },
        getSession: function (id) {
            return ajax().get('/api/v1/events/sessions/' + id + '/');
        },
        getMetadata: function () {
            return ajax().get('/api/v1/metadata/');
        }
    };
};
