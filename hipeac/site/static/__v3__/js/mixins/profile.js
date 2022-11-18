var ProfileMixin = {
  computed: _.extend(
    Vuex.mapState('user', ['user', 'cache']), {
    countryName: function () {
      return this.user.profile.country.name;
    },
    hasCase: function () {
      return (/^[A-Z]*$/).test(this.user.first_name)
        || (/^[A-Z]*$/).test(this.user.last_name);
    }
  }),
  methods: {
    updateUser: function () {
      this.$store.commit('user/updateUser', this.user);
    }
  }
};
