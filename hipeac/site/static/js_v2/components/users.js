Vue.component('user-contact-dialog', {
  data: function () {
    return {
      dialog: false,
      user: null,
      msg: ''
    }
  },
  template: `
    <q-dialog v-model="dialog" transition-show="scale" transition-hide="scale">
      <q-card v-if="user" class="q-pa-sm" style="width: 500px">
        <q-toolbar>
          <q-toolbar-title class="q-ml-xs">Contact form</q-toolbar-title>
          <q-space></q-space>
          <q-btn flat round @click="dialog = false" icon="close"></q-btn>
        </q-toolbar>
        <q-card-section class="text-body2">
          <p>For privacy reasons we cannot share other users' emails. Please use this form to send a message to <strong>{{ user.profile.name }}</strong><span v-if="user.profile.institution"> ({{ user.profile.institution.name }})</span>: we will share your email address with {{ user.profile.name }} so you can get a direct response.</p>
          <q-input v-model="msg" filled type="textarea" class="q-mb-md"></q-input>
          <q-btn @click="sendMessage" outline color="primary" label="Send message"></q-btn>
        </q-card-section>
        <q-card-section class="text-caption q-pb-lg">
          <span>Please note that {{ user.profile.name }} can choose to discard your message.</span>
        </q-card-section>
      </q-card>
    </q-dialog>
  `,
  methods: {
    showDialog: function (user) {
      this.user = user;
      this.dialog = true;
    },
    sendMessage: function () {
      var self = this;
      Hipeac.api.post('/api/contact/', {
        user_id: this.user.id,
        message: this.msg
      }).then(function (res) {
        Hipeac.utils.notifySuccess('Message sent.');
        self.dialog = false;
      }).catch(function (error) {
        Hipeac.utils.notifyApiError(error);
      });
    }
  },
  created: function () {
    this.$store.commit('fetchMetadata');
    this.$root.$on('show-contact-dialog', this.showDialog);
  },
  beforeDestroy: function () {
    this.$root.$off('show-contact-dialog');
  }
});

Vue.component('user-viewer', {
  store: ComponentStore,
  data: function () {
    return {
      selectedUser: 0,
      filters: {
        countries: [],
        topics: [],
        institutionTypes: []
      },
      q: '',
      institutionTypes: {
        university: 'University',
        lab: 'Government Lab',
        innovation: 'Innovation Center',
        industry: 'Industry',
        sme: 'SME',
        other: 'Other'
      }
    }
  },
  props: {
    eventName: {
      type: String,
      default: 'users-query-changed'
    },
    embedSearch: {
      type: Boolean,
      default: true
    },
    isMemberList: {
      type: Boolean,
      default: false
    },
    showContactForm: {
      type: Boolean,
      default: true
    },
    showProfileLink: {
      type: Boolean,
      default: false
    },
    showTopics: {
      type: Boolean,
      default: true
    },
    showInColumns: {
      type: Boolean,
      default: true
    },
    users: {
      type: Array
    },
    institutions: {
      type: Array
    }
  },
  template: `
    <div v-if="users.length">
      <user-contact-dialog></user-contact-dialog>
      <hipeac-search-box v-if="embedSearch && users.length > 10" :event-name="eventName" placeholder="Search by name, affiliation, country..." class="q-mb-lg"></hipeac-search-box>
      <div class="row q-col-gutter-lg">
        <div class="col-12 text-body2" :class="{'col-lg': showInColumns}">
          <display-2 v-if="embedSearch" v-html="overviewText" class="q-mb-lg"></display-2>
          <div class="q-mb-md">
            <display-5 class="display-inline">Institution types</display-5>
            <q-checkbox v-for="(name, code) in institutionTypes" v-model="filters.institutionTypes" :key="code" :val="code" :label="name" size="xs"></q-checkbox>
          </div>
          <div v-if="showTopics && topics.length" class="q-mb-md">
            <display-5 class="display-inline">Research topics</display-5>
            <q-checkbox v-for="topic in topics" v-model="filters.topics" :key="topic.id" :val="topic.id" :label="topic.value" size="xs"></q-checkbox>
          </div>
          <display-5 class="display-inline">Countries</display-5>
          <q-checkbox v-for="country in countries" v-model="filters.countries" :key="country.code" :val="country.code" :label="country.name" size="xs"></q-checkbox>
        </div>
        <div class="col-12" :class="{'col-lg': showInColumns}">
          <display-5 v-if="!embedSearch" v-html="overviewText" class="mb-4"></display-5>
          <q-markup-table flat dense class="text-body-2">
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td v-if="selectedUser == user.id" @click="selectedUser = 0" class="pointer">
                  <q-icon name="expand_less"></q-icon>
                  {{ user.profile.name }}
                  <user-viewer-detail v-if="selectedUser == user.id" :user="user" :show-affiliates="isMemberList"></user-viewer-detail>
                </td>
                <td v-else @click="selectedUser = user.id" class="pointer">
                  <q-icon name="expand_more"></q-icon>
                  {{ user.profile.name }}
                  <span v-if="user.profile.institution">, <institution-icon :type="user.profile.institution.type" class="q-mx-xs"></institution-icon><small>{{ user.profile.institution.short_name }}</small></span>
                  <small v-if="user.profile.second_institution">
                    / {{ user.profile.second_institution.short_name }}
                  </small>
                </td>
                <td v-if="showContactForm" @click="contactUser(user)" class="min-width pointer">
                  <q-icon name="forward_to_inbox"></q-icon>
                </td>
                <td v-if="showProfileLink" class="min-width">
                  <a v-if="user.href" :href="user.href" target="_blank">
                    <q-icon name="open_in_new"></q-icon>
                  </a>
                </td>
              </tr>
            </tbody>
          </q-markup-table>
        </div>
      </div>
    </div>
    <div v-else>
      <q-skeleton type="QBtn" class="full-width q-mb-lg"></q-skeleton>
      <div class="row q-col-gutter-lg">
        <div class="col-12" :class="{'col-lg': showInColumns}">
          <skeleton-text></skeleton-text>
        </div>
        <div class="col-12" :class="{'col-lg': showInColumns}">
          <skeleton-text :lines="10"></skeleton-text>
        </div>
      </div>
    </div>
  `,
  computed: _.extend(
    Vuex.mapGetters(['groupedMetadata']), {
    topics: function () {
      if (!this.groupedMetadata || !_.has(this.groupedMetadata, 'topic') || !this.userTopics.length) return [];
      var userTopics = this.userTopics;
      return this.groupedMetadata['topic'].filter(function (obj) {
        return userTopics.indexOf(obj.id) != -1;
      });
    },
    sortedUsers: function () {
      if (!this.users) return [];
      return this.users.slice().map(function (obj) {
        obj.itypes = [];
        if (obj.profile.institution) obj.itypes.push(obj.profile.institution.type);
        if (obj.profile.second_institution) obj.itypes.push(obj.profile.second_institution.type);
        return obj;
      }).sort(function (a, b) {
        return Hipeac.utils.sortText(a.profile.name, b.profile.name);
      });
    },
    countries: function () {
      if (!this.institutions) return [];
      return _.uniq(_.pluck(this.institutions, 'country'), function (obj) {
        return obj.code;
      }).sort(function (a, b) {
        return Hipeac.utils.sortText(a.name, b.name);
      });
    },
    userTopics: function () {
      if (!this.users) return [];
      return _.uniq(_.flatten(this.users.map(function (obj) {
        return obj.profile.topics;
      })));
    },
    filteredUsers: function () {
      if (!this.users) return [];
      var filters = this.filters;
      var users = this.sortedUsers;

      if (filters.countries.length) {
        users = users.filter(function (obj) {
          return obj.profile.institution && obj.profile.institution.country
            && filters.countries.indexOf(obj.profile.institution.country.code || null) != -1;
        });
      }

      if (filters.institutionTypes.length) {
        users = users.filter(function (obj) {
          return _.intersection(filters.institutionTypes, obj.itypes).length > 0;
        });
      }

      if (filters.topics.length) {
        users = users.filter(function (obj) {
          return _.intersection(filters.topics, obj.profile.topics).length > 0;
        });
      }

      if (this.q == '') return users;
      else return Hipeac.utils.filterMultiple(users, this.q);
    },
    counters: function () {
      var countries = _.without(_.keys(_.groupBy(this.filteredUsers, function (obj) {
        return (obj.profile.institution && obj.profile.institution.country) ? obj.profile.institution.country.name : '--none--';
      })), '--none--');
      var institutions = _.without(_.keys(_.groupBy(this.filteredUsers, function (obj) {
        return (obj.profile.institution) ? obj.profile.institution.name : '--none--';
      })), '--none--');

      return {
        users: this.filteredUsers.length,
        affiliates: _.reduce(this.filteredUsers, function (memo, obj) {
          return memo + ((obj.affiliates) ? obj.affiliates.length : 0);
        }, 0),
        institutions: institutions.length,
        institution: (institutions.length == 1) ? institutions[0] : null,
        countries: countries.length,
        country: (countries.length == 1) ? countries[0] : null
      }
    },
    overviewText: function () {
      if (!this.users || (this.ids && this.ids.length == 0)) {
        return (!this.isMemberList) ? 'No attendees found.' : 'No members found.';
      }

      var userText = (!this.isMemberList) ? 'attendees' : 'members';

      return [
        '<strong class="text-no-wrap">',
        (this.counters.users == 1)
          ? 'One ' + userText.substring(0, userText.length - 1)
          : this.counters.users + ' ' + userText + (
            (this.listType == 'members' && this.counters.affiliates)
              ? ' (' + this.counters.affiliates + ' affiliates)'
              : ''
            ),
        '</strong> from <span class="text-no-wrap">',
        (this.counters.institution)
          ? this.counters.institution
          : this.counters.institutions + ' institutions',
        '</span> in <span class="text-no-wrap">',
        (this.counters.country)
          ? this.counters.country
          : this.counters.countries + ' countries',
        '</span>.'
      ].join('');
    }
  }),
  methods: {
    contactUser: function (user) {
      this.$root.$emit('show-contact-dialog', user);
    },
    updateQuery: function (val) {
      this.q = val;
    }
  },
  created: function () {
    this.$store.commit('fetchMetadata');
    this.$root.$on(this.eventName, this.updateQuery);
  },
  beforeDestroy: function () {
    this.$root.$off(this.eventName);
  }
});
