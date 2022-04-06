var VARS = document.querySelector('#vars').dataset;
var USER_IS_AUTHENTICATED = (+(document.querySelector('html').dataset.user) > 0);

var EventModule = {
  namespaced: true,
  state: {
    event: null,
    attendees: [],
    keynotes: [],
    registration: null
  },
  mutations: {
    getEvent: function (state) {
      Hipeac.api.request('GET', VARS.eventUrl).then(function (res) {
        state.event = Object.freeze(Hipeac.map.event(res.data));
        Quasar.Loading.hide();
      });
    },
    getAttendees: function (state) {
      if (!USER_IS_AUTHENTICATED) return;

      Hipeac.api.request('GET', VARS.attendeesUrl).then(function (res) {
        state.attendees = Object.freeze(res.data.map(function (obj) {
          return Hipeac.map.user(obj.user);
        }));
      });
    },
    getKeynotes: function (state) {
      if (!state.keynotes.length) {
        Hipeac.api.request('GET', VARS.sessionsUrl, null, {session_type: 69}).then(function (res) {
          state.keynotes = Object.freeze(res.data.map(function (obj) {
            return Hipeac.map.session(obj);
          }));
        });
      }
    },
    getRegistration: function (state) {
      if (!USER_IS_AUTHENTICATED) return;

      Hipeac.api.request('GET', VARS.registrationUrl).then(function (res) {
        var reg = _.findWhere(res.data, {event: +VARS.eventId});

        if (reg) {
          state.registration = Object.freeze(Hipeac.map.registration(reg));
        } else {
          state.registration = null;
        }
      });
    },
    updateRegistration: function (state, payload) {
      state.registration = Object.freeze(Hipeac.map.registration(payload));
    }
  }
};
