function isIE() {
    var ua = window.navigator.userAgent;
    return ua.indexOf('MSIE ') > -1 || ua.indexOf('Trident/') > -1;
}

function isSmallDevice() {
    return $(window).width() < 768;
}

function filterIntersection(filterIds, items, attr) {
    return (!filterIds.length)
        ? items
        : items.filter(function (obj) {
            return _.intersection(filterIds, obj[attr]).length > 0;
        });
}

function filterMultiple(data, q, separator) {
    if (q == '') return data;
    var queries = q.toLowerCase().split(separator || ' ');

    return data.filter(function (obj) {
        var matches = 0;
        _.each(queries, function (q) {
            if (obj.q.indexOf(q) !== -1) matches++;
        });
        return matches == queries.length;
    });
}

function sort() {
    return {
        int: function (a, b) {
            return a - b;
        },
        text: function (a, b) {
            var a = a.toLowerCase();
            var b = b.toLowerCase();
            if (a < b) return -1;
            if (a > b) return 1;
            return 0;
        }
    };
}

function extractMetadata(items, field) {
    if (!items) return [];
    return _.uniq(_.flatten(_.map(items, function (obj) {
        return obj[field];
    })), function (obj) {
        return obj.id;
    }).sort(function (a, b) {
        return sort().text(a.value, b.value);
    });
}

function extractInstitutions(users) {
    if (!users) return [];
    return _.uniq(users.filter(function (obj) { return obj.profile && obj.profile.institution; }).map(function (obj) {
        return obj.profile.institution;
    }), function (obj) {
        return obj.id;
    });
}

function storage() {
    var ls = window.localStorage;

    return {
        get: function (key, defaultValue) {
            try {
                var value = ls.getItem(key);
                return (value !== null) ? JSON.parse(value) : defaultValue;
            } catch (e) {
                return this.getCookie(key, defaultValue);
            }
        },
        set: function (key, value, days) {
            try {
                ls.setItem(key, JSON.stringify(value));
            } catch (e) {
                this.setCookie(key, value, days);
            }
        },
        getCookie: function (key, defaultValue) {
            try {
                var data = '; ' + document.cookie;
                var parts = data.split('; ' + key + '=');
                return JSON.parse(parts.pop().split(';').shift());
            } catch (err) {
                return defaultValue;
            }
        },
        setCookie: function (key, value, days) {
            document.cookie = [
                key + '=' + JSON.stringify(value),
                'expires=' + moment().add(days, 'days').toString(),
                'path=/'
            ].join(';');
        }
    };
}
