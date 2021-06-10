var FETCH_WAIT = 250;


function extractInstitutions(users) {
  if (!users) return [];
  return _.uniq(users.filter(function (obj) { return obj.profile && obj.profile.institution; }).map(function (obj) {
    return obj.profile.institution;
  }), function (obj) {
    return obj.id;
  });
}

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
        Hipeac.api.getArticles().then(function (res) {
          state.articles = Object.freeze(mapper().articles(res));
        });
      }
    }, FETCH_WAIT),
    fetchQuotes: _.debounce(function (state) {
      if (!state.quotes.length) {
        Hipeac.api.getQuotes().then(function (res) {
          state.quotes = Object.freeze(res);
        });
      }
    }, FETCH_WAIT),
    fetchMetadata: _.debounce(function (state) {
      if (!state.metadata.length) {
        Hipeac.api.getMetadata().then(function (res) {
          state.metadata = Object.freeze(res);
        });
      }
    }, FETCH_WAIT),
    fetchInstitutions: _.debounce(function (state) {
      if (!state.institutions.length) {
        Hipeac.api.getAllInstitutions().then(function (res) {
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
        Hipeac.api.getAllProjects().then(function (res) {
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
    }
  }
});

var EditLink = Vue.extend({
  data: function () {
    return {
      show: false
    }
  },
  props: {
    url: {
      type: String
    }
  },
  created: function () {
    var self = this;
    if (USER_IS_AUTHENTICATED) {
      Hipeac.api.request('head', this.url).then(function (res) {
        if (res.status == 200) self.show = true;
      });
    }
  }
});

Vue.component('editor-link', EditLink.extend({
  template: '' +
    '<li v-if="show" class="nav-item">' +
      '<a class="nav-link" :href="url"><i class="material-icons mr-1">edit</i>Edit</a>' +
    '</li>' +
  ''
}));

Vue.component('private-btn', EditLink.extend({
  props: {
    icon: {
      type: String,
      default: 'edit'
    }
  },
  template: '<q-btn v-if="show" flat round :icon="icon" type="a" :href="url"></q-btn>'
}));

Vue.component('hipeac-search-box', {
  data: function () {
    return {
      q: ''
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
  template: `
    <q-input filled v-model="q" :placeholder="placeholder" :dense="true">
      <template v-slot:append>
        <q-icon v-if="q !== ''" name="clear" @click="q = ''" class="cursor-pointer"></q-icon>
        <q-icon name="search"></q-icon>
      </template>
    </q-input>
  `,
  watch: {
    'q': _.debounce(function (val, oldVal) {
      if (val != oldVal) {
        if (val != '') {
          if (val != this.$route.query.q) {
            this.$router.replace({query: {q: val}});
          }
        } else this.$router.replace({name: this.$route.name});

        this.$root.$emit(this.eventName, val);
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
      this.$root.$emit(this.eventName, this.q);
    }
  }
});

var HipeacCardsComponent = Vue.extend({
  props: {
    url: {
      type: String
    },
    type: {
      type: String,
      default: 'latest'
    },
    limit: {
      type: [Number, Boolean],
      default: false
    },
    dense: {
      type: Boolean,
      default: false
    }
  },
  data: function () {
    return {
      loading: true,
      next: null,
      items: [],
      mapper: null
    };
  },
  template: `
    <div>
      <div v-if="items.length" class="row q-col-gutter-lg">
        <div class="col-12 col-md-4" v-for="obj in obj_list" :key="obj.id">
          <div :is="component" :obj="obj" :dense="dense" class="full-height"></div>
        </div>
        <div v-if="!limit && next" class="col-12">
          <q-btn unelevated size="xl" :loading="loading" color="grey-2" text-color="grey" @click="loadItems()" icon="add_circle" class="full-width q-pa-md" />
        </div>
      </div>
      <div v-if="loading" class="row q-col-gutter-lg">
        <div class="col-12 col-md-4" v-for="n in 3" :key="n">
          <skeleton-card :dense="dense"></skeleton-card>
        </div>
      </div>
    </div>
  `,
  computed: {
    obj_list: function () {
      var items = (this.items && this.limit)
        ? _.shuffle(this.items).slice(0, this.limit)
        : this.items;

      return items;
    }
  },
  methods: {
    loadItems: function () {
      var self = this;
      var url = this.next || this.url;
      Hipeac.api.get(url).then(function (res) {
        self.next = Object.freeze(res.data.next);
        self.items = Object.freeze(self.items.concat(res.data.results.map(function (obj) {
          return self.mapper(obj);
        })));
        self.loading = false;
      });
    }
  },
  created: function () {
    this.loadItems();
  }
});

Vue.component('skeleton-card', {
  props: {
    dense: {
      type: Boolean,
      default: false
    }
  },
  template: `
    <q-card class="q-pt-sm">
      <q-item v-if="!dense">
        <q-item-section avatar>
          <q-skeleton type="QAvatar" size="64px" />
        </q-item-section>
      </q-item>
      <q-card-section class="q-py-sm q-mb-xl">
        <q-skeleton type="text" class="text-subtitle1" />
        <q-skeleton type="text" width="60%" class="text-subtitle1 q-mb-sm" />
        <q-skeleton type="text" width="75%" class="text-caption" />
      </q-card-section>
      <q-card-actions class="q-pa-md">
        <q-skeleton type="QChip" />
        <q-space />
        <q-skeleton type="QBtn" />
      </q-card-actions>
    </q-card>
  `
});

Vue.component('skeleton-text', {
  props: {
    lines: {
      type: Number,
      default: 3
    }
  },
  template: `
    <div>
      <q-skeleton v-for="n in range" :key="n" type="text" class="text-subtitle1" />
      <q-skeleton type="text" width="60%" class="text-subtitle1 q-mb-sm" />
    </div>
  `,
  computed: {
    range: function () {
      return _.range(1, this.lines);
    }
  }
});

Vue.component('hipeac-profile-item', {
  props: {
    profile: {
      required: true,
      type: Object
    },
    dense: {
      type: Boolean,
      default: false
    },
    showAvatar: {
      type: Boolean,
      default: true
    }
  },
  template: `
    <q-item :dense="dense" class="q-pa-none">
      <q-item-section avatar v-if="showAvatar">
        <q-avatar v-if="profile.avatar_url" size="64px">
          <img :src="profile.avatar_url">
        </q-avatar>
      </q-item-section>
      <q-item-section>
        <q-item-label>{{ profile.name }}</q-item-label>
        <q-item-label v-if="profile.institution" caption>{{ profile.institution.name }}<span v-if="profile.institution.country">, {{ profile.institution.country.name }}</span></q-item-label>
      </q-item-section>
    </q-item>
  `
});

Vue.component('hipeac-progress', {
  props: ['value'],
  template: '<q-linear-progress rounded size="10px" :value="value" :color="color" track-color="grey-4" />',
  computed: {
    color: function () {
      if (this.value < 0.40) return 'orange-5';
      if (this.value < 0.70) return 'lime-5';
      return 'light-green-5';
    }
  }
});

Vue.component('hipeac-social-media', {
  props: {
    size: {
      type: Number,
      default: 20
    }
  },
  template: `
    <p class="row q-gutter-sm hipeac__social-media">
      <a href="//twitter.com/hipeac" target="_blank" rel="noopener"><svg xmlns="http://www.w3.org/2000/svg" :height="size" :width="size" viewBox="0 0 24 24"><defs/><path d="M24 4.56a9.83 9.83 0 01-2.83.77 4.93 4.93 0 002.17-2.72 9.86 9.86 0 01-3.13 1.2 4.92 4.92 0 00-3.6-1.56 4.93 4.93 0 00-4.8 6.04A13.98 13.98 0 011.68 3.15 4.93 4.93 0 003.2 9.72a4.9 4.9 0 01-2.23-.61A4.93 4.93 0 004.91 14a4.93 4.93 0 01-2.22.08 4.93 4.93 0 004.6 3.42A9.9 9.9 0 010 19.54a13.94 13.94 0 007.55 2.21c9.14 0 14.3-7.72 14-14.64A10.03 10.03 0 0024 4.56z"/></svg></a>
      <a href="//www.youtube.com/channel/UCKnHdjNxf9dyawiLfjPaHhw/videos" target="_blank" rel="noopener"><svg xmlns="http://www.w3.org/2000/svg" :height="size" :width="size" viewBox="0 0 24 24"><defs/><path d="M19.6 3.2C16 2.9 8 2.9 4.4 3.2.4 3.5 0 5.8 0 12c0 6.2.5 8.5 4.4 8.8 3.6.3 11.6.3 15.2 0 4-.3 4.4-2.6 4.4-8.8 0-6.2-.5-8.5-4.4-8.8zM9 16V8l8 4-8 4z"/></svg></a>
      <a href="//www.linkedin.com/company/hipeac/" target="_blank" rel="noopener"><svg xmlns="http://www.w3.org/2000/svg" :height="size" :width="size" viewBox="0 0 24 24"><defs/><path d="M19 0H5a5 5 0 00-5 5v14a5 5 0 005 5h14a5 5 0 005-5V5a5 5 0 00-5-5zM8 19H5V8h3v11zM6.5 6.73a1.76 1.76 0 010-3.53c.97 0 1.75.8 1.75 1.77S7.47 6.73 6.5 6.73zM20 19h-3v-5.6c0-3.37-4-3.12-4 0V19h-3V8h3v1.76a3.8 3.8 0 017 2.48V19z"/></svg></a>
    </p>
  `
});

Vue.component('marked', {
  props: {
    text: {
      type: String,
      default: ''
    }
  },
  template: '<div class="marked" v-html="compiledMarkdown"></div>',
  computed: {
    compiledMarkdown: function () {
      if (!this.text) return '';
      return CommonMarkWriter.render(CommonMarkReader.parse(this.text));
    }
  }
});

Vue.component('display-1', {
  template: '<h2 class="text-h4 text-weight-light"><span><slot></slot></span></h2>'
});

Vue.component('display-2', {
  template: '<h3 class="text-h5"><span><slot></slot></span></h3>'
});

Vue.component('display-3', {
  template: '<h5 class="text-h6"><span><slot></slot></span></h5>'
});

Vue.component('display-4', {
  template: '<h6><span><slot></slot></span></h6>'
});

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

Vue.component('country-flag', {
  props: {
    code: {
      type: String
    }
  },
  template: '<i :class="css"></i>',
  computed: {
    css: function () {
      if (!this.code) return '';
      return [
        "flag-sprite",
        "flag-" + this.code[0],
        "flag-_" + this.code[1],
      ].join(' ').toLowerCase()
    }
  }
});
