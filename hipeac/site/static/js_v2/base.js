var NICE_DATE_FORMAT = 'dddd, MMM D';
var DJANGO_VARS = document.querySelector('html').dataset;
var LANGUAGE = DJANGO_VARS.lang;
var USER_IS_AUTHENTICATED = JSON.parse(DJANGO_VARS.auth);
var USER_TZ = moment.tz.guess(true);


var CommonMarkReader = new commonmark.Parser({safe: true, smart: true});
var CommonMarkWriter = new commonmark.HtmlRenderer();

var make_local = function (dt) {
  return moment.utc(dt).local();
};

var Hipeac = {
  api: {
    request: function (method, url, data, headers) {
      var headers = headers || {};
      headers["X-CSRFTOKEN"] = DJANGO_VARS.csrfToken;

      var d = (method == 'get')
        ? { params: data}
        : { data: data}

      return axios(_.extend(d, {
        method: method,
        url: url,
        headers: headers
      }));
    },
    get: function (url, data, headers) {
      return this.request('get', url, data, headers);
    },
    post: function (url, data, headers) {
      return this.request('post', url, data, headers);
    },
    put: function (url, data, headers) {
      return this.request('put', url, data, headers);
    },
    getAllProjects: function () {
      return this.get('/api/v1/network/projects/all/');
    },
    getAllInstitutions: function () {
      return this.get('/api/v1/network/institutions/all/');
    },
    getArticles: function () {
      return this.get('/api/v1/communication/articles/');
    },
    getClippings: function () {
      return this.get('/api/v1/communication/clippings/');
    },
    getQuotes: function () {
      return this.get('/api/v1/communication/quotes/');
    },
    getEvents: function () {
      return this.get('/api/v1/events/events/');
    },
    getCourseAttendees: function (id) {
      return this.get('/api/v1/events/courses/' + id + '/attendees/');
    },
    getSession: function (id) {
      return this.get('/api/v1/events/sessions/' + id + '/');
    },
    getSessionAttendees: function (id) {
      return this.get('/api/v1/events/sessions/' + id + '/attendees/');
    },
    getNotifications: function () {
      return this.get('/api/v1/user/notifications/');
    },
    getMetadata: function () {
      return this.get('/api/v1/metadata/');
    }
  },
  map: {
    break: function (obj) {
      obj.icon = {
        'cofee': 'coffee',
        'lunch': 'restaurant'
      }[obj.type] || 'coffee';
      obj.startAt = make_local(obj.start_at);
      obj.endAt = make_local(obj.end_at);
      obj.isoDay = obj.startAt.format('YYYY-MM-DD');;
      obj.duration = moment.duration(obj.endAt.diff(obj.startAt));
      return obj;
    },
    course: function (obj) {
      var mapSession = this.session;

      obj.color = ['white', 'blue', 'red', 'green', 'orange', 'purple', 'cyan'][obj.custom_data.slot || 1],
      obj.sessions = obj.sessions.map(function (s) {
        s.session_type = {
          value: 'Course'
        };
        s.keywords = obj.teachers.map(function (o) {
          return o.profile.name.toLowerCase();
        }).concat([obj.title]);
        s.application_areas = [];
        s.topics = obj.topics;
        return mapSession(s);
      }).sort(function (a, b) {
        return a.startAt.unix() - b.startAt.unix() || a.session_type.position - b.session_type.position;
      });

      return obj;
    },
    job: function (obj) {
      return obj;
    },
    event: function (obj) {
      var mapBreak = this.break;
      var mapSession = this.session;

      obj.registrations_round = (obj.registrations_count)
        ? Math.floor(obj.registrations_count / 10) * 10
        : 0;

      obj.dates = obj.dates.map(function (date) {
        return make_local(date);
      });

      obj.startDate = make_local(obj.start_date);
      obj.endDate = make_local(obj.end_date);
      obj.days = obj.endDate.diff(obj.startDate, 'days') + 1;
      obj.year = obj.startDate.year();

      if (obj.breaks && obj.breaks.length) {
        obj.breaks = obj.breaks.map(function (s) {
          return mapBreak(s);
        }).sort(function (a, b) {
          return a.startAt.unix() - b.startAt.unix();
        });
      }

      if (obj.sessions && obj.sessions.length) {
        obj.sessions = obj.sessions.map(function (s) {
          return mapSession(s);
        }).sort(function (a, b) {
          return a.startAt.unix() - b.startAt.unix() || a.session_type.position - b.session_type.position;
        });

        obj.virtualExhibition = _.find(obj.sessions, function (o) {
          return o.title.toLowerCase().includes("virtual exhibition");
        });
      }

      obj.sortedSponsors = _.sortBy(obj.sponsors.map(function (o) {
        return {
          id: o.id,
          name: (o.institution) ? o.institution.name : o.project.acronym + ' (EU project)'
        };
      }), 'name');

      return obj;
    },
    registration: function (obj) {
      obj.createdAt = make_local(obj.created_at);
      obj.updatedAt = make_local(obj.updated_at);
      obj.fee = obj.base_fee + obj.extra_fees + obj.manual_extra_fees;
      obj.isPaid = obj.saldo >= 0;
      return obj;
    },
    session: function (obj) {
      obj.startAt = make_local(obj.start_at);
      obj.endAt = make_local(obj.end_at);
      obj.isoDay = obj.startAt.format('YYYY-MM-DD');
      obj.isPast = obj.endAt.isBefore(moment());
      obj.duration = moment.duration(obj.endAt.diff(obj.startAt));
      obj.isKeynote = obj.session_type.value == 'Keynote';
      obj.metadata = _.union(
        _.pluck(obj.application_areas, 'id'),
        _.pluck(obj.topics, 'id'),
        [obj.session_type.id]
      ).sort();
      obj.tags = {
        areas: obj.application_areas.map(function (o) { return o.value; }),
        topics: obj.topics.map(function (o) { return o.value; })
      };

      obj.color = {
        'Course': 'teal',
        'Keynote': 'primary',
        'Paper Track': 'light-blue',
        'Poster Session': 'cyan',
        'Industrial Session': 'deep-purple',
        'Workshop': 'green',
        'Tutorial': 'teal',
        'Social Event': 'yellow'
      }[obj.session_type.value] || 'grey-7';

      obj.q = [
        obj.title,
        obj.session_type.value,
        obj.keywords.join(' ')
      ].join(' ').toLowerCase();

      return obj;
    },
    user: function (obj) {
      institution = obj.profile.institution;
      second_institution = obj.profile.second_institution || null;
      obj.q = [
        obj.profile.name,
        (institution)
          ? [institution.name, institution.local_name, institution.short_name].join(' ')
          : '',
        (institution && institution.country)
          ? institution.country.name
          : '',
        (second_institution)
          ? second_institution.name
          : '',
      ].join(' ').toLowerCase();

      return obj;
    }
  },
  utils: {
    filterMultiple: function (data, q, separator) {
      if (q == '') return data;
      var queries = q.toLowerCase().split(separator || ' ');

      return data.filter(function (obj) {
          var matches = 0;
          _.each(queries, function (q) {
              if (obj.q.indexOf(q) !== -1) matches++;
          });
          return matches == queries.length;
      });
    },
    notifyApiError: function (error) {
      var types = {
        400: 'warning',
        401: 'warning',
        500: 'negative'
      }
      Quasar.plugins.Notify.create({
        position: 'bottom-left',
        timeout: 5000,
        type: types[error.response.status] || 'warning',
        message: error.response.data.message || null,
        caption:
          [error.response.status, ' ', error.response.statusText]
            .join('')
            .toUpperCase() || null,
        icon: null
      })
    },
    notifySuccess: function (msg) {
      Quasar.plugins.Notify.create({
        position: 'bottom-left',
        timeout: 2500,
        message: msg,
        icon: null
      })
    },
    sortText: function (a, b) {
      var a = a.toLowerCase();
      var b = b.toLowerCase();
      if (a < b) return -1;
      if (a > b) return 1;
      return 0;
    }
  }
};
