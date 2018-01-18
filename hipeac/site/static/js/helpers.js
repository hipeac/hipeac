var isIE = function () {
    var ua = window.navigator.userAgent;
    return ua.indexOf('MSIE ') > -1 || ua.indexOf('Trident/') > -1;
};

var isSmallDevice = function () {
    return $(window).width() < 768;
};

var filterMultiple = function (data, q, separator) {
    if (q == '') return data;
    var queries = q.toLowerCase().split(separator || ' ');

    return data.filter(function (obj) {
        var matches = 0;
        _.each(queries, function (q) {
            if (obj.q.indexOf(q) !== -1) matches++;
        });
        return matches == queries.length;
    });
};

var sortInt = function (a, b) {
    return a - b;
};

var sortText = function (a, b) {
    var a = a.toLowerCase();
    var b = b.toLowerCase();
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
};
