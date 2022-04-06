var RegistrationMixin = {
  props: ['id'],
  data: function () {
    return {
      authenticated: +(document.querySelector('html').dataset.user) > 0,
      create_url: document.querySelector('#vars').dataset.registrationUrl,
      now: moment(),
      obj: null,
      poster_limit: 3,
      poster_fields: [
        {"id": "type", "type": "select", "label": "Type", "options": ["project", "industry", "student"]},
        {"id": "title", "type": "text", "label": "Poster title"}
      ]
    };
  },
  computed: _.extend(
    Vuex.mapState('events', ['event', 'registration']), {
    program: function () {
      if (!this.event) return null;

      var sessions = _.clone(this.event.sessions).map(function (s) {
        s.iso_day = moment(s.start).format('YYYY-MM-DD');
        return s;
      });
      var days = _.uniq(sessions.map(function (obj) {
        return obj.iso_day;
      }));
      var sessionsMap = _.groupBy(sessions, 'iso_day');
      var program = days.map(function (day) {
        return {
          day: day,
          date: moment(day),
          sessions: sessionsMap[day]
        };
      });
      return _.indexBy(program, 'day');
    },
    conflicts: function () {
      if (!this.event || !this.registration) return false;
      var registration = this.registration;
      var times = _.pluck(this.event.sessions.filter(function (obj) {
        return _.contains(registration.sessions, obj.id)
      }), 'start_at');
      return times.length > _.uniq(times).length;
    }
  }),
  methods: {
    createOrUpdate: function () {
      var self = this;

      if (_.has(this.obj, 'self')) {
        Hipeac.api.update(this.obj, function (res) {
          self.$store.commit('events/updateRegistration', res.data);
        }, 'Registration updated.');
      } else {
        Hipeac.api.create(this.create_url, this.obj, function (res) {
          self.$store.commit('events/updateRegistration', res.data);
        }, 'Registration created.');
      }
    },
    sync: function () {
      var self = this;

      if (!this.event || this.registration === undefined) {
        setTimeout(function () { self.sync() }, 25);
        return;
      }

      if (this.registration) {
        this.obj = _.clone(this.registration);
      } else {
        this.obj = _.clone({
          event: this.event.id,
          sessions: []
        });
      }
    }
  },
  watch: {
    'registration': function (val) {
      this.obj = val;
    }
  },
  mounted: function () {
    this.sync();
  }
};
