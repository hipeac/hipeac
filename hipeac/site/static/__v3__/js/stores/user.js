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
          EventEmitter.emit('update:user:rel_metadata', {
            'application_area': res.data.profile.rel_application_areas,
            'topic': res.data.profile.rel_topics,
          });
          EventEmitter.emit('update:user:rel_objects', {
            'institution': res.data.profile.rel_institutions,
            'project': res.data.profile.rel_projects,
          });
          Hipeac.utils.notify('Profile updated.');
        }).catch(function (error) {
          Hipeac.utils.notifyApiError(error);
        });
      },
      replaceUser: function (state, obj) {
        state.user = obj;
      },
    }
  }
};
