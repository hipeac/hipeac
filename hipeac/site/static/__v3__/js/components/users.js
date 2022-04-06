var HipeacUserComponents = {

  'user-contact-dialog': {
    data: function () {
      return {
        dialogVisible: false,
        user: null,
        msg: null
      };
    },
    template: `
      <q-dialog v-model="showDialog" @show="dialogVisible = true">
        <q-card v-if="user" class="q-pa-sm" style="width: 500px">
          <q-toolbar>
            <q-toolbar-title class="q-ml-xs">Contact form</q-toolbar-title>
            <q-space />
            <q-btn v-close-popup flat round icon="close" />
          </q-toolbar>
          <q-card-section class="text-body2">
            <p>For privacy reasons we cannot share other users' emails. Please use this form to send a message to <strong>{{ user.name }}</strong><span v-if="user.affiliation"> ({{ user.affiliation }})</span>: we will share your email address with {{ user.name }} so you can get a direct response.</p>
            <q-input v-model="msg" filled type="textarea" class="q-mb-md"></q-input>
            <q-btn v-close-popup @click="sendMessage" outline color="primary" label="Send message" :disable="!msg" />
          </q-card-section>
          <q-card-section class="text-caption q-pb-lg">
            <span>Please note that {{ user.name }} can choose to discard your message.</span>
          </q-card-section>
        </q-card>
      </q-dialog>
    `,
    computed: {
      showDialog: {
        get: function () {
          return this.user != null;
        },
        set: function (val) {
          if (this.dialogVisible) {
            this.dialogVisible = false;
            this.msg = null;
            this.user = null;
          }
        }
      }
    },
    methods: {
      updateUser: function (user) {
        this.user = user;
      },
      sendMessage: function () {
        Hipeac.api.request('post', '/api/contact/', {
          user_id: this.user.id,
          message: this.msg
        }).then(function (res) {
          Hipeac.utils.notify('Message sent.');
        }).catch(function (error) {
          Hipeac.utils.notifyApiError(error);
        });
      }
    },
    created: function () {
      EventEmitter.on('show-contact-dialog', this.updateUser);
    },
    beforeDestroy: function () {
      EventEmitter.off('show-contact-dialog');
    }
  },

  'attendees-list': {
    data: function () {
      return {
        filters: {
          countries: [],
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
      showContactForm: {
        type: Boolean,
        default: true
      },
      users: {
        type: Array
      }
    },
    template: `
      <div v-if="users.length">
        <hipeac-search-bar v-if="users.length > 20" v-model="q" placeholder="Search by name, affiliation, country..." class="q-mb-lg"></hipeac-search-bar>
        <div class="row q-col-gutter-lg q-pt-md">
          <div class="col-12 col-lg">
            <display-2 v-html="overviewText" class="q-mb-lg"></display-2>
            <div class="q-mb-md">
              <display-5 :dense="true" class="display-inline q-mr-md">Institution types</display-5>
              <q-checkbox v-for="(name, code) in institutionTypes" v-model="filters.institutionTypes" :key="code" :val="code" :label="name" size="xs" />
            </div>
            <display-5 :dense="true" v-if="countries.length" class="display-inline q-mr-md">Countries</display-5>
            <q-checkbox v-for="country in countries" v-model="filters.countries" :key="country.code" :val="country.code" :label="country.name" size="xs" />
          </div>
          <div class="col-12 col-lg">
            <q-markup-table flat :dense="$q.screen.gt.sm">
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td>
                    {{ user.profile.name }}<span v-if="user.profile.institution">, <small>{{ user.profile.institution.short_name }}</small></span>
                    <small v-if="user.profile.second_institution"> / {{ user.profile.second_institution.short_name }}</small>
                  </td>
                  <td v-if="showContactForm" @click="contactUser(user)" class="min-width pointer">
                    <q-icon name="forward_to_inbox" />
                  </td>
                  <td class="min-width">
                    <a v-if="user.href" :href="user.href" target="_blank">
                      <q-icon name="north_east" />
                    </a>
                  </td>
                </tr>
              </tbody>
            </q-markup-table>
          </div>
        </div>
        <user-contact-dialog></user-contact-dialog>
      </div>
    `,
    computed: {
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
      institutions: function () {
        if (!this.users) return [];
        return _.uniq(_.pluck(this.users.filter(function (obj) {
          return obj.profile.institution !== null;
        }).map(function (obj) {
          return obj.profile;
        }), 'institution'), function (obj) {
          return obj.id;
        });
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

        if (this.q == '') return users;
        else return Hipeac.utils.filter(users, this.q);
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
        if (!this.users) {
          return 'No attendees found.';
        }

        var userText = 'attendees';

        return [
          '<strong class="text-no-wrap">',
          (this.counters.users == 1)
            ? 'One ' + userText.substring(0, userText.length - 1)
            : this.counters.users + ' ' + userText,
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
    },
    methods: {
      contactUser: function (user) {
        EventEmitter.emit('show-contact-dialog', user);
      },
      updateQuery: function (val) {
        this.q = val;
      }
    }
  }

};
