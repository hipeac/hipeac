var SessionMixin = {
  props: ['id'],
  data: function () {
    return {
      dialogVisible: false,
      session: null,
      sessionAttendees: [],
      tab: 'main',
      rerouteName: 'program',
    };
  },
  computed: {
    registered: function () {
      if (!this.registration) return false;
      return _.contains(this.registration.sessions, +this.id);
    },
    room: function () {
      if (!this.event || !this.session) return null;
      var rooms = {};
      _.each(this.event.venues, function (venue) {
        _.each(venue.rooms, function (room) {
          rooms[room.id] = room;
        });
      });
      return rooms[this.session.room] || null;
    },
    showDialog: {
      get: function () {
        return this.session != null;
      },
      set: function (val) {
        if (this.dialogVisible) {
          this.dialogVisible = false;
          EventEmitter.emit('session-dialog-hide');
        }
      }
    }
  },
  methods: {
    reroute: function () {
      this.$router.push({name: this.rerouteName});
    },
    clearSession: function () {
      this.session = null;
    },
    findSession: function () {
      var self = this;

      if (!this.event) {
        return null;
      };

      return _.findWhere(this.event.sessions, {id: +this.id});
    },
    getSession: function () {
      var self = this;
      var session = this.findSession();

      if (!session) {
        setTimeout(function () { self.getSession() }, 25);
        return;
      };

      Hipeac.api.request('GET', session.self).then(function (res) {
        self.session = Hipeac.map.session(res.data);

        Hipeac.api.request('GET', res.data.rel_attendees).then(function (res) {
          self.sessionAttendees = Object.freeze(res.data.map(function (obj) {
            return Hipeac.map.user(obj.user);
          }));
        });
      });
    }
  },
  created: function () {
    this.getSession();
    EventEmitter.on('session-dialog-hide', this.clearSession);
  },
  beforeUnmount: function () {
    EventEmitter.off('session-dialog-hide');
  }
};
