var DJANGO_VARS = document.querySelector('html').dataset;
var USER_IS_AUTHENTICATED = (+(DJANGO_VARS.user) > 0);


var getMoment = function (dt, tz) {
  return moment.utc(dt).tz(tz || 'Europe/Brussels');
};


function modelFromUrl(url) {
  var m = url.split('/api/v1/')[1].split('/')[0];
  m = m.substring(0, 1).toUpperCase() + m.substring(1);
  m = (m.substring(m.length - 1) == 's') ? m.slice(0, -1) : m;
  return m;
}


var EventEmitter = new TinyEmitter();
window['moment-range'].extendMoment(moment);


var Hipeac = {
  api: {
    request: function (method, url, data, params, headers) {
      var headers = headers || {};
      headers["X-CSRFTOKEN"] = DJANGO_VARS.csrfToken;
      return axios({
        method: method,
        url: url,
        data: data,
        params: params,
        headers: headers
      });
    },
    create: function (url, obj, callbackFn, customMsg) {
      this.request('post', url, obj).then(function (res) {
        if (callbackFn) callbackFn(res);
        Hipeac.utils.notify((customMsg) ? customMsg : modelFromUrl(res.data.self || url) + ' created.');
      }).catch(function (error) {
        Hipeac.utils.notifyApiError(error);
      });
    },
    update: function (obj, callbackFn, customMsg) {
      this.request('put', obj.self, obj).then(function (res) {
        if (callbackFn) callbackFn(res);
        Hipeac.utils.notify((customMsg) ? customMsg : modelFromUrl(obj.self) + ' updated.');
      }).catch(function (error) {
        Hipeac.utils.notifyApiError(error);
      });
    },
    remove: function (obj, callbackFn, customMsg) {
      this.request('delete', obj.self).then(function (res) {
        if (callbackFn) callbackFn(res);
        Hipeac.utils.notify((customMsg) ? customMsg : modelFromUrl(obj.self) + ' deleted.');
      }).catch(function (error) {
        Hipeac.utils.notifyApiError(error);
      });
    }
  },
  map: {
    break: function (obj, tz) {
      obj.icon = {
        'cofee': 'coffee',
        'lunch': 'restaurant'
      }[obj.type] || 'coffee';
      obj.start = getMoment(obj.start_at, tz);
      obj.end = getMoment(obj.end_at, tz);
      obj.duration = moment.duration(obj.end.diff(obj.start));
      return obj;
    },
    event: function (obj) {
      var mapBreak = this.break;
      var mapSession = this.session;

      obj.tz = (obj.is_virtual) ? moment.tz.guess(true) : 'Europe/Brussels';

      if (obj.sessions.length) {
        obj.start = getMoment(obj.sessions[0].start_at, obj.tz);
        obj.end = getMoment(obj.sessions[obj.sessions.length - 1].end_at, obj.tz);
      } else {
        obj.start = getMoment(obj.start_date, obj.tz);
        obj.end = getMoment(obj.end_date, obj.tz);
      }

      obj.payments = (obj.payments_activation) ? getMoment(obj.payments_activation, obj.tz) : null;
      obj.year = moment(obj.start_date).year();
      obj.registration_start = getMoment(obj.registration_start_date, obj.tz);
      obj.registrations_round = (obj.registrations_count)
        ? Math.floor(obj.registrations_count / 10) * 10
        : 0;
      obj.google_mid = null;

      if (obj.links && obj.links.length) {
        var gmaps = _.findWhere(obj.links, {type: "google_maps"});
        obj.google_mid = (gmaps) ? gmaps.url.match(/id=([^&]+)/)[1] : null;
      }

      if (obj.breaks && obj.breaks.length) {
        obj.breaks = obj.breaks.map(function (s) {
          return mapBreak(s, obj.tz);
        }).sort(function (a, b) {
          return a.start.unix() - b.start.unix();
        });
      }

      if (obj.sessions && obj.sessions.length) {
        obj.sessions = obj.sessions.map(function (s) {
          return mapSession(s, obj.tz);
        }).sort(function (a, b) {
          return a.start.unix() - b.start.unix() || a.type.position - b.type.position;
        });
      }

      return obj;
    },
    job: function (obj) {
      return obj;
    },
    jobfair: function (obj) {
      obj.tz = (obj.is_virtual) ? moment.tz.guess(true) : 'Europe/Brussels';
      obj.start = getMoment(obj.start_date, obj.tz);
      obj.end = getMoment(obj.end_date, obj.tz);
      obj.year = moment(obj.start_date).year();

      /*obj.registration_start = getMoment(obj.registration_start_date, obj.tz);
      obj.registrations_round = (obj.registrations_count)
        ? Math.floor(obj.registrations_count / 10) * 10
        : 0;
      obj.google_mid = null;*/

      return obj;
    },
    metadata: function (obj) {
      obj._q = [
        obj.value,
        obj.keywords.join(' '),
      ].join(' ').toLowerCase();

      return obj;
    },
    notification: function (obj) {
      obj.icon = {
        'membership_industry': 'accessibility_new',
        'membership_researcher': 'accessibility_new',
        'linkedin_account': 'swap_horizontal_circle',
        'research_topics_pending': 'developer_board',
        'long_time_no_see': 'waving_hand'
      }[obj.category] || 'notification_important';

      return obj;
    },
    registration: function (obj) {
      obj.fee = obj.base_fee + obj.extra_fees + obj.manual_extra_fees;
      obj.is_paid = obj.saldo >= 0;

      this.qBooleans(obj, [
        ['paid', 'is_paid'],
        ['coupon', 'coupon'],
        ['invoice.requested', 'invoice_requested'],
        ['invoice.sent', 'invoice_sent'],
        ['visa.requested', 'visa_requested'],
        ['visa.sent', 'visa_sent'],
      ]);

      return obj;
    },
    session: function (obj, tz) {
      obj.start = getMoment(obj.start_at, tz);
      obj.end = getMoment(obj.end_at, tz);
      obj.duration = moment.duration(obj.end.diff(obj.start));
      obj.is_keynote = obj.type.value == 'Keynote';
      obj.is_social_event = obj.type.value == 'Social Event';
      obj.has_ended = obj.end.isBefore(moment());

      obj.color = {
        'Course': 'teal',
        'Keynote': 'primary',
        'Paper Track': 'light-blue',
        'Poster Session': 'cyan',
        'Industrial Session': 'deep-purple',
        'Workshop': 'green',
        'Tutorial': 'teal',
        'Social Event': 'yellow'
      }[obj.type.value] || 'grey-7';

      obj._q = [
        obj.title,
        obj.keywords.join(' '),
        'day:' + obj.start.format('dddd'),
        'type:' + slugify(obj.type.value),
      ].join(' ').toLowerCase();

      /*this.qBooleans(obj, [
        ['private', 'is_private']
      ]);*/

      return obj;
    },
    user: function (obj) {
      obj.name = obj.profile.name;
      obj._q = [
        obj.profile.name,
        (obj.profile.institution) ? obj.profile.institution.name : '',
        (obj.profile.institution && obj.profile.institution.country) ? obj.profile.institution.country.name : '',
      ].join(' ').toLowerCase();
      return obj;
    },
    vision: function (obj) {
      obj.year = obj.download_url.match(/\d+/)[0] || null;
      return obj;
    },
    qBooleans: function (obj, fields) {
      if (!obj._q) obj._q = '';
      var qs = [];
      _.each(fields, function (f) {
        qs.push(f[0] + ':' + (obj[f[1]] ? 'yes' : 'no'));
      });
      obj._q +=  (' ' + qs.join(' ')).toLowerCase();
    }
  },
  utils: {
    filter: function (data, q, skipN) {
      if (q == '') return data;
      var skipN = skipN || false;
      var queries = q.toLowerCase().split(' ');

      return data.filter(function (obj) {
        var matches = 0;
        _.each(queries, function (q) {
          if (skipN) {
            if (obj._q.indexOf(q) !== -1 && obj._q.indexOf('-' + q) === -1) matches++;
          } else {
            if (obj._q.indexOf(q) !== -1) matches++;
          }
        });
        return matches == queries.length;
      });
    },
    confirmAction: function (msg, okCallbackFn, cancelCallbackFn) {
      Quasar.Dialog.create({
        message: msg,
        class: 'hipeac-confirm-dialog q-pa-sm',
        focus: 'none',
        cancel: {
          'flat': true,
          'color': 'grey-8'
        },
        ok: {
          'unelevated': true,
          'color': 'primary'
        }
      }).onOk(okCallbackFn || function () {}).onCancel(cancelCallbackFn || function () {});
    },
    notifyApiError: function (error) {
      var types = {
        400: 'warning',
        401: 'warning',
        403: 'warning',
        500: 'negative'
      }

      var textColors = {
        400: 'grey-8',
        401: 'grey-8',
        403: 'grey-8',
        500: 'white'
      }

      var caption = [error.response.status, ' ', error.response.statusText].join('').toUpperCase() || null;
      var msg = null;

      // 400 Bad Request
      if (error.response.status == 400) {
        var errors = [];
        _.each(_.keys(error.response.data), function (k) {
          errors.push('<strong>' + k + '</strong>: ' + error.response.data[k].join(' '))
        });
        msg = errors.join('<br>') || null;
      }

      // 403 Forbidden || 500 Internal Server Error
      if (error.response.status == 403 || error.response.status == 500) {
        msg = error.response.data.message || null;
      }

      Quasar.Notify.create({
        timeout: 10000,
        progress: true,
        html: true,
        message: msg,
        caption: caption,
        type: types[error.response.status] || 'warning',
        actions: [
          {
            label: 'Dismiss',
            color: textColors[error.response.status] || 'grey-8',
            handler: function () {}
          }
        ],
        attrs: {
          role: 'alert'
        }
      });
    },
    notify: function (msg, type) {
      Quasar.Notify.create({
        timeout: 2000,
        message: msg,
        type: type || 'positive'
      });
    },
    registerComponents: function (app, collectionList) {
      _.each(collectionList, function (componentCollection) {
        _.each(componentCollection, function (config, componentName) {
          app.component(componentName, config);
        });
      });
    },
    registerStoreModules: function (app, moduleCollection) {
      var modules = {};
      _.each(moduleCollection, function (mod) {
        modules = _.extend(modules, mod);
      });
      app.use(Vuex.createStore({
        modules: modules
      }));
    },
    sortText: function (a, b) {
      var a = a.toLowerCase();
      var b = b.toLowerCase();
      if (a < b) return -1;
      if (a > b) return 1;
      return 0;
    }
  },
  cookies: {
    consent: function (msg, acceptBtnText, privacyBtnText, privacyUrl) {
      var cookie = 'cookieconsent';
      if (!Quasar.Cookies.has(cookie)) {
        Quasar.Notify.create({
          timeout: 0,
          message: msg || 'We use cookies to ensure you get the best experience on our website.',
          position: 'bottom-right',
          color: 'primary',
          classes: 'hipeac-cookies-notify',
          multiLine: true,
          actions: [
            {
              label: acceptBtnText || 'Accept',
              color: 'yellow-7',
              handler: function () {
                Quasar.Cookies.set(cookie, true, {
                  path: '/'
                });
              }
            },
            {
              label: privacyBtnText || 'Learn more',
              color: 'white',
              handler: function () {
                Quasar.openURL(privacyUrl || '/privacy/');
              }
            }
          ]
        });
      }
    }
  }
};
