Vue.component('user-viewer-topics', {
    store: ComponentStore,
    props: {
        topics: {
            type: Array
        }
    },
    template: '' +
        '<p v-if="topics.length" class="pl-3">' +
            '<icon name="bookmarks" class="sm" style="margin-left:-1rem"></icon> ' +
            '<strong>Research topics:</strong> {{ topicsString }}' +
        '</p>' +
    '',
    computed: _.extend(
        Vuex.mapGetters(['metadataDict']), {
        topicsString: function () {
            var metadata = this.metadataDict;
            return this.topics.map(function (id) {
                return metadata[id].value;
            }).sort().join(', ');
        }
    })
});

Vue.component('user-viewer-detail', {
    props: {
        user: {
            type: Object
        },
        showAffiliates: {
            type: Boolean,
            default: false
        }
    },
    template: '' +
        '<div v-if="user" class="my-2 py-3 pl-4 pr-3 bg-light text-sm clearfix">' +
            '<p v-if="user.profile.institution" class="mb-0">' +
                '<institution-icon :type="user.profile.institution.type" class="sm"></institution-icon> ' +
                '{{ user.profile.institution.name }}' +
            '</p>' +
            '<p v-if="user.profile.second_institution" class="mb-0">' +
                '<institution-icon :type="user.profile.second_institution.type" class="sm"></institution-icon> ' +
                '{{ user.profile.second_institution.name }}' +
            '</p>' +
            '<user-viewer-topics :topics="user.profile.topics" class="mt-2 mb-0"></user-viewer-topics>' +
            '<p v-if="showAffiliates && user.affiliates" class="mt-2 mb-0 ml pl-3">' +
                '<icon name="group" class="sm" style="margin-left: -1rem"></icon> ' +
                '<strong>Research group</strong>' +
                '<ul class="mt-1" style="padding-left:0.85rem">' +
                    '<li v-for="aff in user.affiliates">' +
                        '{{ aff.profile.name }}' +
                    '</li>' +
                '</ul>' +
            '</p>' +
        '</div>' +
    ''
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
            default: 'query-changed'
        },
        embedSearch: {
            type: Boolean,
            default: false
        },
        isMemberList: {
            type: Boolean,
            default: false
        },
        showTopics: {
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
    template: '' +
        '<div v-if="users.length" class="row">' +
            '<div class="col-12 col-md">' +
                '<div v-if="embedSearch && users.length > 10" class="border-top border-bottom py-2 mb-4">' +
                    '<search-box :eventName="eventName" placeholder="Search by name, affiliation, country..."></search-box>' +
                '</div>' +
                '<catchphrase v-if="embedSearch" v-html="overviewText" class="mb-4"></catchphrase>' +
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
                '<catchphrase v-if="!embedSearch" v-html="overviewText" class="mb-4"></catchphrase>' +
                '<table class="table table-sm">' +
                    '<tr v-for="user in filteredUsers" :key="user.id">' +
                        '<td v-if="selectedUser == user.id" @click="selectedUser = 0" class="pointer">' +
                            '<icon name="expand_less" class="sm mr-2"></icon>' +
                            '{{ user.profile.name }}' +
                            '<user-viewer-detail v-if="selectedUser == user.id" :user="user" :show-affiliates="isMemberList"></user-viewer-detail>' +
                        '</td>' +
                        '<td v-else @click="selectedUser = user.id" class="pointer">' +
                            '<icon name="expand_more" class="sm mr-2"></icon>' +
                            '{{ user.profile.name }}' +
                            '<span v-if="user.profile.institution && selectedUser != user.id">' +
                                ', <institution-icon :type="user.profile.institution.type" class="sm"></institution-icon> ' +
                                '<small>{{ user.profile.institution.short_name }}</small>' +
                            '</span>' +
                            '<small v-if="user.profile.second_institution && selectedUser != user.id">' +
                                ' / {{ user.profile.second_institution.short_name }}' +
                            '</small>' +
                        '</td>' +
                        '<td class="sm">' +
                            '<a v-if="user.href" :href="user.href" target="_blank"><icon name="open_in_new" class="sm"></icon></a>' +
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
        sortedUsers: function () {
            if (!this.users) return [];
            return this.users.slice().map(function (obj) {
                obj.itypes = [];
                if (obj.profile.institution) obj.itypes.push(obj.profile.institution.type);
                if (obj.profile.second_institution) obj.itypes.push(obj.profile.second_institution.type);
                return obj;
            }).sort(function (a, b) {
                return sort().text(a.profile.name, b.profile.name);
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
            else return filterMultiple(users, this.q);
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
