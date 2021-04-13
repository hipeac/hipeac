var FETCH_WAIT = 250;


var ComponentStore = new Vuex.Store({
  state: {
      options: null,
      articles: null,
      quotes: [],
      metadata: [],
      institutions: [],
      projects: []
  },
  mutations: {
      fetchArticles: _.debounce(function (state) {
          if (!state.articles) {
              api().getArticles().then(function (res) {
                  state.articles = Object.freeze(mapper().articles(res));
              });
          }
      }, FETCH_WAIT),
      fetchQuotes: _.debounce(function (state) {
          if (!state.quotes.length) {
              api().getQuotes().then(function (res) {
                  state.quotes = Object.freeze(res);
              });
          }
      }, FETCH_WAIT),
      fetchMetadata: _.debounce(function (state) {
          if (!state.metadata.length) {
              api().getMetadata().then(function (res) {
                  state.metadata = Object.freeze(res);
              });
          }
      }, FETCH_WAIT),
      fetchInstitutions: _.debounce(function (state) {
          if (!state.institutions.length) {
              api().getAllInstitutions().then(function (res) {
                  state.institutions = Object.freeze(res.map(function (obj) {
                      obj.display = obj.name;
                      obj.q = [
                          obj.name,
                          obj.local_name,
                          obj.short_name
                      ].join(' ').toLowerCase();
                      return obj;
                  }));
              });
          }
      }, FETCH_WAIT),
      fetchProjects: _.debounce(function (state) {
          if (!state.projects.length) {
              api().getAllProjects().then(function (res) {
                  state.projects = Object.freeze(res.map(function (obj) {
                      obj.display = [
                          obj.acronym,
                          (obj.ec_project_id) ? ' #' + obj.ec_project_id : ''
                      ].join('');
                      obj.q = [
                          obj.display,
                          obj.name
                      ].join(' ').toLowerCase();
                      return obj;
                  }));
              });
          }
      }, FETCH_WAIT),
      setOptions: function (state, options) {
          state.options = Object.freeze(options);
      }
  },
  getters: {
      groupedArticles: function (state) {
          if (!state.articles) return null;
          return {
              type: _.groupBy(state.articles, 'type'),
              event: _.groupBy(state.articles, 'event')
          }
      },
      requiredFields: function (state) {
          if (!state.options) return null;
          if (_.has(state.options.actions, 'POST')) return _.keys(state.options.actions.POST);
          if (_.has(state.options.actions, 'PUT')) return _.keys(state.options.actions.PUT);
          return null;
      },
      fields: function (state) {
          if (!state.options) return null;
          if (_.has(state.options.actions, 'POST')) return state.options.actions.POST;
          if (_.has(state.options.actions, 'PUT')) return state.options.actions.PUT;
          return null;
      },
      metadataDict: function (state) {
          return _.indexBy(state.metadata, 'id');
      },
      groupedMetadata: function (state) {
          if (!state.metadata) return null;
          return _.groupBy(state.metadata, 'type');
      },
  }
});


Vue.component('search-box', {
  data: function () {
      return {
          q: '',
          showFilters: false
      }
  },
  props: {
      eventName: {
          type: String,
          default: 'query-changed'
      },
      placeholder: {
          type: String,
          default: ''
      }
  },
  template: '' +
      '<div class="input-group search-bar pr-3">' +
          '<div class="input-group-prepend">' +
              '<div class="input-group-text">' +
                  '<i v-if="q" @click="q = \'\'" class="material-icons text-secondary pointer">&#xE5CD;</i>' +
                  '<i v-else class="material-icons text-primary">&#xE8B6;</i>' +
              '</div>' +
          '</div>' +
          '<input v-model="q" type="text" class="form-control" :placeholder="placeholder">' +
      '</div>' +
  '',
  watch: {
      'q': _.debounce(function (val, oldVal) {
          if (val != oldVal) {
              if (val != '') this.$router.replace({query: {q: val}});
              else this.$router.replace({name: this.$route.name});

              EventHub.$emit(this.eventName, val);
          }
      }, 250)
  },
  methods: {
      updateQuery: function (val) {
          this.q = val;
      }
  },
  created: function () {
      if (this.$route.query.q) {
          this.q = this.$route.query.q;
          EventHub.$emit(this.eventName, this.q);
      }
      EventHub.$on('carousel-query-sent', this.updateQuery);
  }
});

Vue.component('search-card', {
  data: function () {
      return {
          showFilters: false
      }
  },
  props: {
      showFiltersButton: {
          type: Boolean,
          default: false
      },
      placeholder: {
          type: String,
          default: ''
      }
  },
  template: '' +
      '<div class="hipeac-card py-3">' +
          '<div class="d-flex flex-row justify-content-between">' +
              '<search-box :placeholder="placeholder"></search-box>' +
              '<button v-if="showFiltersButton" class="btn btn-sm btn-light text-nowrap" @click="showFilters = !showFilters">' +
                  '<span v-if="showFilters"><icon name="keyboard_arrow_up"></icon><span class="d-none d-md-inline ml-1">Hide filters</span></span>' +
                  '<span v-else><icon name="filter_list"></icon><span class="d-none d-md-inline ml-1">Show filters</span></span>' +
              '</button>' +
          '</div>' +
          '<div v-if="showFilters">' +
              '<hr>' +
              '<slot></slot>' +
          '</div>' +
      '</div>' +
  ''
});

Vue.component('skeleton-table', {
  props: {
      rows: {
          type: Number,
          default: 5
      },
      withHeader: {
          type: Boolean,
          default: false
      }
  },
  template: '' +
      '<table class="table skeleton">' +
          '<tbody>' +
              '<tr v-for="item in skeletons" :key="item">' +
                  '<td class="p-1">' +
                      '<span v-if="withHeader" class="text w-75"></span><br v-if="withHeader">' +
                      '<span class="text sm w-100"></span>' +
                  '</td>' +
              '</tr>' +
          '</tbody>' +
      '</table>' +
  '',
  computed: {
      skeletons: function () {
          return Array.apply(null, {length: this.rows}).map(Number.call, Number);
      }
  }
});


function sort() {
  return {
      int: function (a, b) {
          return a - b;
      },
      text: function (a, b) {
          var a = a.toLowerCase();
          var b = b.toLowerCase();
          if (a < b) return -1;
          if (a > b) return 1;
          return 0;
      }
  };
}

function extractInstitutions(users) {
  if (!users) return [];
  return _.uniq(users.filter(function (obj) { return obj.profile && obj.profile.institution; }).map(function (obj) {
      return obj.profile.institution;
  }), function (obj) {
      return obj.id;
  });
}

Vue.component('icon', {
  props: ['name'],
  template: '<q-icon :name="name"></q-icon>'
});

Vue.component('institution-icon', {
  props: ['type'],
  template: '<q-icon :name="name"></q-icon>',
  computed: {
    name: function () {
      return {
        university: 'account_balance',
        lab: 'layers',
        innovation: 'device_hub',
        industry: 'business',
        sme: 'business',
        other: 'scatter_plot',
      }[this.type];
    }
  }
});

Vue.component('catchphrase', {
  template: '<h5 class="text-h6"><slot></slot></h5>'
});
