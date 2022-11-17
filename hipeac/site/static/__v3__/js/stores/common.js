var HipeacCommonStoreModule = {
  common: {
    namespaced: true,
    state: {
      countriesStorageKey: 'countries',
      countries: null,
      metadataStorageKey: 'metadata',
      metadata: null
    },
    mutations: {
      getCountries: _.once(function (state) {
        state.countries = Object.freeze(HipeacStorage.cache.get(state.countriesStorageKey));

        if (!state.countries) {
          Hipeac.api.request('GET', '/api/countries/').then(function (res) {
            state.countries = Object.freeze(res.data);

            try {
              HipeacStorage.cache.set(state.countriesStorageKey, res.data, 604800);  // 1 week
            } catch (e) {}
          });
        }
      }),
      getMetadata: _.once(function (state) {
        state.metadata = Object.freeze(HipeacStorage.cache.get(state.metadataStorageKey));

        if (!state.metadata) {
          Hipeac.api.request('GET', '/api/v1/metadata/').then(function (res) {
            state.metadata = Object.freeze(res.data.sort(function (a, b) {
              return a.position - b.position || Hipeac.utils.sortText(a.value, b.value);
            }).map(function (obj) {
              return Hipeac.map.metadata(obj);
            }));

            try {
              HipeacStorage.cache.set(state.metadataStorageKey, state.metadata, 1800);  // 30 minutes
            } catch (e) {}
          });
        }
      }),
      getNotifications: _.once(function (state) {
        var key = 'notifications';
        var ttl = 30;
        var self = this;

        state.notifications = Object.freeze(HipeacStorage.cache.get(key));

        if (state.notifications == undefined) {
          Hipeac.api.request('get', '/api/v1/user/notifications/').then(function (res) {
            state.notifications = Object.freeze(res.data.map(function (obj) {
              return Hipeac.map.notification(obj);
            }));
            HipeacStorage.cache.set(key, state.notifications, ttl);
          });
        }

        setTimeout(function () {
          self.commit('common/getNotifications');
        }, 1000 * 30);
      })
    }
  }
};
