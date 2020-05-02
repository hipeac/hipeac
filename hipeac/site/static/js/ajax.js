function ajax() {
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
        get: function (url, data) {
            return $.ajax({
                method: 'GET',
                url: url,
                data: data
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
}

function api() {
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
        getClippings: function () {
            return ajax().get('/api/v1/communication/clippings/');
        },
        getQuotes: function () {
            return ajax().get('/api/v1/communication/quotes/');
        },
        getEvents: function () {
            return ajax().get('/api/v1/events/events/');
        },
        getCourseAttendees: function (id) {
          return ajax().get('/api/v1/events/courses/' + id + '/attendees/');
        },
        getSession: function (id) {
            return ajax().get('/api/v1/events/sessions/' + id + '/');
        },
        getSessionAttendees: function (id) {
            return ajax().get('/api/v1/events/sessions/' + id + '/attendees/');
        },
        getNotifications: function () {
            return ajax().get('/api/v1/user/notifications/');
        },
        getMetadata: function () {
            return ajax().get('/api/v1/metadata/');
        }
    };
}
