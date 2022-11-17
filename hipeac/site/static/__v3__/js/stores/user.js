var HipeacUserStoreModule = {
  user: {
    namespaced: true,
    state: {
      user: null
    },
    mutations: {
      getUser: function (state) {
        Hipeac.api.request('GET', '/api/v1/user/account/').then(function (res) {
          state.user = Hipeac.map.user(res.data);
          Quasar.Loading.hide();
        });
      },
      updateUser: function (state, payload) {
        Hipeac.api.request('PUT', '/api/v1/user/account/', payload).then(function (res) {
          state.user = Hipeac.map.user(res.data);
          EventEmitter.emit('update:user:rel_cache', {
            'application_area': res.data.profile.rel_application_areas,
            'topic': res.data.profile.rel_topics,
          });
          Hipeac.utils.notify('Profile updated.');
        }).catch(function (error) {
          Hipeac.utils.notifyApiError(error);
        });
      }
    }
  }
};
