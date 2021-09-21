var SessionMixin = {
  props: ['id'],
  data: function () {
    return {
      dialogVisible: false,
      session: null,
      tab: 'main'
    };
  },
  computed: {
    registered: function () {
      if (!this.registration) return false;
      return _.contains(this.registration.sessions, +this.id);
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
      this.$router.push({name: 'program'});
    },
    clearSession: function () {
      this.session = null;
    },
    getSession: function () {
      var self = this;

      if (!this.event) {
        setTimeout(function () { self.getSession() }, 25);
        return;
      };

      var session = _.findWhere(this.event.sessions, {id: +this.id});
      Hipeac.api.request('GET', session.self).then(function (res) {
        self.session = Hipeac.map.session(res.data);
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
