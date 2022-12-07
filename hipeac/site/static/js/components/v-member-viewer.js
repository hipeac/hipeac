Vue.component('member-viewer', {
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
      default: 'query-changed'
    },
    showTopics: {
      type: Boolean,
      default: true
    },
    members: {
      type: Array
    }
  },
  template: '' +
    '<div v-if="members.length" class="row">' +
      '<div class="col-12 col-md">' +
        '<catchphrase v-html="overviewText" class="mb-4"></catchphrase>' +
        '<div class="mb-4">' +
          '<h6 class="d-inline display-sm mr-2">Institution types</h6>' +
          '<div v-for="(name, code) in institutionTypes" :key="code" class="form-check form-check-inline mr-2">' +
            '<label class="form-check-label pointer">' +
              '<input v-model="filters.institutionTypes" :value="code" type="checkbox" class="form-check-input">' +
              '<span v-html="name"></span>' +
            '</label>' +
          '</div>' +
        '</div>' +
        '<div v-if="showTopics && topics.length" class="mb-4">' +
          '<h6 class="d-inline display-sm mr-2">Research topics</h6>' +
          '<div v-for="topic in topics" :key="topic.id" class="form-check form-check-inline mr-2">' +
            '<label class="form-check-label pointer">' +
              '<input v-model="filters.topics" :value="topic.id" type="checkbox" class="form-check-input">' +
              '<span v-html="topic.value"></span>' +
            '</label>' +
          '</div>' +
        '</div>' +
        '<h6 class="d-inline display-sm mr-2">Countries</h6>' +
        '<div v-for="country in countries" :key="country.code" class="form-check form-check-inline mr-2">' +
          '<label class="form-check-label pointer">' +
            '<input v-model="filters.countries" :value="country.code" type="checkbox" class="form-check-input">' +
            '<span v-html="country.name"></span>' +
          '</label>' +
        '</div>' +
      '</div>' +
      '<div class="col-12 col-md">' +
        '<hr class="d-md-none my-4">' +
        '<table class="table table-sm">' +
          '<tr v-for="member in filteredMembers" :key="member.user">' +
            '<td v-if="selectedUser == member.user" @click="selectedUser = 0" class="pointer">' +
              '<icon name="expand_less" class="sm mr-2" :class="{\'text-white\': !member.affiliates.length}"></icon>' +
              '{{ member.name }}' +
              '<span v-if="member.institution">' +
                ', <institution-icon :type="member.institution.type" class="sm"></institution-icon> ' +
                '<small>{{ member.institution.short_name }}</small>' +
              '</span>' +
              '<small v-if="member.second_institution">' +
                ' / {{ member.second_institution.short_name }}' +
              '</small>' +
              '<ul v-if="member.affiliates.length" class="mt-2">' +
                '<li v-for="aff in member.affiliates" class="text-sm">{{ aff.first_name }} {{ aff.last_name }}</li>' +
              '</ul>' +
            '</td>' +
            '<td v-else @click="selectedUser = member.user" class="pointer">' +
              '<icon name="expand_more" class="sm mr-2" :class="{\'text-white\': !member.affiliates.length}"></icon>' +
              '{{ member.name }}' +
              '<span v-if="member.institution">' +
                ', <institution-icon :type="member.institution.type" class="sm"></institution-icon> ' +
                '<small>{{ member.institution.short_name }}</small>' +
              '</span>' +
              '<small v-if="member.second_institution">' +
                ' / {{ member.second_institution.short_name }}' +
              '</small>' +
            '</td>' +
            '<td class="sm">' +
              '<a v-if="member.url" :href="member.url" target="_blank"><icon name="open_in_new" class="sm"></icon></a>' +
            '</td>' +
          '</tr>' +
        '</table>' +
      '</div>' +
    '</div>' +
    '<div v-else class="row">' +
      '<div class="col-12 col-md">' +
        '<skeleton-content></skeleton-content>' +
      '</div>' +
      '<div class="col-12 col-md">' +
        '<skeleton-table class="m-0" :rows="10"></skeleton-table>' +
      '</div>' +
    '</div>' +
  '',
  computed: _.extend(
    Vuex.mapGetters(['groupedMetadata']), {
    topics: function () {
      if (!this.groupedMetadata || !_.has(this.groupedMetadata, 'topic') || !this.userTopics.length) return [];
      var userTopics = this.userTopics;
      return this.groupedMetadata['topic'].filter(function (obj) {
        return userTopics.indexOf(obj.id) != -1;
      });
    },
    institutions: function () {
      if (!this.members) return [];
      return _.uniq(_.pluck(this.members.filter(function (obj) {
        return obj.institution !== null;
      }), 'institution'), function (obj) {
        return obj.id;
      });
    },
    countries: function () {
      if (!this.institutions) return [];
      return _.uniq(_.pluck(this.institutions, 'country'), function (obj) {
        return obj.code;
      }).sort(function (a, b) {
        return sort().text(a.name, b.name);
      });
    },
    userTopics: function () {
      if (!this.members) return [];
      return _.uniq(_.flatten(this.members.map(function (obj) {
        return [];  // obj.profile.topics;
      })));
    },
    sortedMembers: function () {
      if (!this.members) return [];
      return this.members.slice().map(function (obj) {
        obj.itypes = [];
        if (obj.institution) obj.itypes.push(obj.institution.type);
        if (obj.second_institution) obj.itypes.push(obj.second_institution.type);
        return obj;
      }).sort(function (a, b) {
        return sort().text(a.name, b.name);
      });
    },
    filteredMembers: function () {
      if (!this.members) return [];
      var filters = this.filters;
      var members = this.sortedMembers;

      if (filters.countries.length) {
        members = members.filter(function (obj) {
          return obj.institution && obj.institution.country
            && filters.countries.indexOf(obj.institution.country.code || null) != -1;
        });
      }

      if (filters.institutionTypes.length) {
        members = members.filter(function (obj) {
          return _.intersection(filters.institutionTypes, obj.itypes).length > 0;
        });
      }

      /*if (filters.topics.length) {
        members = members.filter(function (obj) {
          return _.intersection(filters.topics, obj.topics).length > 0;
        });
      }*/

      if (this.q == '') return members;
      else return filterMultiple(members, this.q);
    },
    counters: function () {
      var countries = _.without(_.keys(_.groupBy(this.filteredMembers, function (obj) {
        return (obj.institution && obj.institution.country) ? obj.institution.country.name : '--none--';
      })), '--none--');
      var institutions = _.without(_.keys(_.groupBy(this.filteredMembers, function (obj) {
        return (obj.institution) ? obj.institution.name : '--none--';
      })), '--none--');

      return {
        users: this.filteredMembers.length,
        affiliates: _.reduce(this.filteredMembers, function (memo, obj) {
          return memo + ((obj.affiliates) ? obj.affiliates.length : 0);
        }, 0),
        institutions: institutions.length,
        institution: (institutions.length == 1) ? institutions[0] : null,
        countries: countries.length,
        country: (countries.length == 1) ? countries[0] : null
      }
    },
    overviewText: function () {
      if (!this.members || (this.ids && this.ids.length == 0)) {
        return 'No members found.';
      }

      var userText = 'members';

      return [
        '<strong class="text-nowrap">',
        (this.counters.users == 1)
          ? 'One ' + userText.substring(0, userText.length - 1)
          : this.counters.users + ' ' + userText + (
            (this.listType == 'members' && this.counters.affiliates)
              ? ' (' + this.counters.affiliates + ' affiliates)'
              : ''
            ),
        '</strong> from <span class="text-nowrap">',
        (this.counters.institution)
          ? this.counters.institution
          : this.counters.institutions + ' institutions',
        '</span> in <span class="text-nowrap">',
        (this.counters.country)
          ? this.counters.country
          : this.counters.countries + ' countries',
        '</span>.'
      ].join('');
    }
  }),
  methods: {
    updateQuery: function (val) {
      this.q = val;
    }
  },
  created: function () {
    this.$store.commit('fetchMetadata');
    EventHub.$on(this.eventName, this.updateQuery);
  }
});
