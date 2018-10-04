var SearchList = Vue.extend({
    data: function () {
        return {
            q: '',
            filters: {
                topic: '__all__'
            },
        }
    },
    props: ['items', 'showSearch'],
    methods: {
        mapItems: function (data) {
            return data.map(function (obj) {
                obj.q = '';
                return obj;
            });
        },
        filterItems: function (items) {
            return data;
        },
        updateQuery: function (val) {
            this.q = val;
        }
    },
    computed: {
        mappedItems: function () {
            return this.mapItems(this.items);
        },
        filteredItems: function () {
            return filterMultiple(this.filterItems(this.mappedItems), this.q);
        },
        topics: function () {
            if (!this.items || !_.has(this.items[0], 'topics')) return [];
            return _.uniq(_.flatten(_.map(this.filteredItems, function (obj) { return obj.topics; })), function (obj) {
                return obj.id;
            }).sort(function (a, b) {
                return sortText(a.value, b.value);
            });
        }
    },
    created: function () {
        EventHub.$on('query-changed', this.updateQuery);
    },
    beforeDestroy: function () {
        EventHub.$off('query-changed');
    }
});


Vue.component('project-list', SearchList.extend({
    template: '' +
        '<div v-if="items.length" class="row">' +
            '<div class="col-6 col-md-3 col-lg-2">' +
                '<h6 class="mt-3">Topics</h6>' +
                '<label class="d-block my-1">' +
                    '<input v-model="filters.topic" type="radio" value="__all__" class="d-none">' +
                    '<filter-label text="ALL" :selected="\'__all__\' == filters.topic"></filter-label>' +
                '</label>' +
                '<label v-for="t in topics" class="d-block my-1">' +
                    '<input v-model="filters.topic" type="radio" :value="t.id" class="d-none">' +
                    '<filter-label :text="t.value" :selected="t.id == filters.topic"></filter-label>' +
                '</label>' +
            '</div>' +
            '<div class="col">' +
                '<search-card v-if="showSearch" class="container py-4" placeholder="Search projects by name, topic or keywords..."></search-card>' +
                '<div class="hipeac-card with-table">' +
                    '<table class="table w-100 m-0">' +
                        '<tbody class="no-top-line">' +
                            '<tr v-for="project in filteredItems" :key="project.id">' +
                                '<td>' +
                                    '<a :href="project.href">' +
                                        '<strong>{{ project.acronym }}: {{ project.name }}</strong>' +
                                    '</a><br>' +
                                    '<metadata-list :items="project.topics"></metadata-list>' +
                                '</td>' +
                                '<td class="d-none d-md-table-cell logo-td text-center align-middle">' +
                                    '<img v-if="project.images" :src="project.images.sm" class="logo-md"></img>' +
                                '</td>' +
                            '</tr>' +
                        '</tbody>' +
                    '</table>' +
                '</div>' +
            '</div>' +
        '</div>' +
    '',
    methods: {
        mapItems: function (items) {
            return mapper().projects(items);
        },
        filterItems: function (items) {
            var filters = this.filters;
            return items.filter(function (obj) {
                return (filters.topic == '__all__' || _.contains(obj.topicIds, filters.topic))
            });
        }
    }
}));

Vue.component('job-list', SearchList.extend({
    data: function () {
        return {
            activeTab: 'countries',
            filters: {
                careerLevel: '__all__',
                country: '__all__',
                type: '__all__',
                topic: '__all__',
                institution: '__all__'
            },
            internship: INTERNSHIP,
            showMore: false
        }
    },
    props: ['showExtraFilters'],
    template: '' +
        '<div v-if="items.length" class="row">' +
            '<div class="col-6 col-md-3 col-lg-2">' +
                '<a class="btn btn-pill btn-block" v-if="showExtraFilters" @click.prevent="showMore = !showMore">' +
                    '<span v-if="!showMore">More filters <i class="material-icons">&#xE315;</i></span>' +
                    '<span v-else>Less filters <i class="material-icons">&#xE314;</i></span>' +
                '</a>' +
                '<h6 class="mt-3">Positions ({{ filteredItems.length }})</h6>' +
                '<label class="d-block my-1">' +
                    '<input v-model="filters.type" type="radio" value="__all__" class="d-none">' +
                    '<filter-label text="ALL" :selected="\'__all__\' == filters.type"></filter-label>' +
                '</label>' +
                '<label class="d-block my-1">' +
                    '<input v-model="filters.type" type="radio" :value="internship" class="d-none">' +
                    '<filter-label text="Internships" :selected="internship == filters.type"></filter-label>' +
                '</label>' +
                '<h6 class="mt-3">Topics</h6>' +
                '<label class="d-block my-1">' +
                    '<input v-model="filters.topic" type="radio" value="__all__" class="d-none">' +
                    '<filter-label text="ALL" :selected="\'__all__\' == filters.topic"></filter-label>' +
                '</label>' +
                '<label v-for="t in topics" class="d-block my-1">' +
                    '<input v-model="filters.topic" type="radio" :value="t.id" class="d-none">' +
                    '<filter-label :text="t.value" :selected="t.id == filters.topic"></filter-label>' +
                '</label>' +
            '</div>' +
            '<div class="col-6 col-md-3 col-lg-2 border-left" v-show="showExtraFilters && showMore">' +
                '<a @click.prevent="activeTab = \'countries\'" class="btn btn-pill mb-3" :class="{\'btn-primary\': activeTab == \'countries\'}">' +
                    '<i class="material-icons">&#xE80B;</i></a>' +
                '<a @click.prevent="activeTab = \'institutions\'" class="btn btn-pill mb-3" :class="{\'btn-primary\': activeTab == \'institutions\'}">' +
                    '<i class="material-icons">&#xE0AF;</i></a>' +
                '<a @click.prevent="activeTab = \'careerLevels\'" class="btn btn-pill mb-3" :class="{\'btn-primary\': activeTab == \'careerLevels\'}">' +
                    '<i class="material-icons">&#xE7FD;</i></a>' +
                '<div v-show="activeTab == \'countries\'">' +
                    '<h6>Countries</h6>' +
                    '<label class="d-block my-1">' +
                        '<input v-model="filters.country" type="radio" value="__all__" class="d-none">' +
                        '<filter-label text="ALL" :selected="\'__all__\' == filters.country"></filter-label>' +
                    '</label>' +
                    '<label v-for="c in countries" class="d-block my-1">' +
                        '<input v-model="filters.country" type="radio" :value="c.code" class="d-none">' +
                        '<filter-label :text="c.name" :selected="c.code == filters.country"></filter-label>' +
                    '</label>' +
                '</div>' +
                '<div v-show="activeTab == \'institutions\'">' +
                    '<h6>Institutions</h6>' +
                    '<label class="d-block my-1">' +
                        '<input v-model="filters.institution" type="radio" value="__all__" class="d-none">' +
                        '<filter-label text="ALL" :selected="\'__all__\' == filters.institution"></filter-label>' +
                    '</label>' +
                    '<label v-for="inst in institutions" class="d-block my-1">' +
                        '<input v-model="filters.institution" type="radio" :value="inst.id" class="d-none">' +
                        '<filter-label :text="inst.short_name" :selected="inst.id == filters.institution"></filter-label>' +
                    '</label>' +
                '</div>' +
                '<div v-show="activeTab == \'careerLevels\'">' +
                    '<h6>Carrer levels</h6>' +
                    '<label class="d-block my-1">' +
                        '<input v-model="filters.careerLevel" type="radio" value="__all__" class="d-none">' +
                        '<filter-label text="ALL" :selected="\'__all__\' == filters.careerLevel"></filter-label>' +
                    '</label>' +
                    '<label v-for="cl in careerLevels" class="d-block my-1">' +
                        '<input v-model="filters.careerLevel" type="radio" :value="cl.id" class="d-none">' +
                        '<filter-label :text="cl.value" :selected="cl.id == filters.careerLevel"></filter-label>' +
                    '</label>' +
                '</div>' +
            '</div>' +
            '<div class="col">' +
                '<search-card v-if="showSearch" class="container py-4" placeholder="Search open positions by title, company, country, topic or keywords..."></search-card>' +
                '<div class="hipeac-card with-table">' +
                    '<table class="table w-100 m-0">' +
                        '<tbody class="no-top-line">' +
                            '<tr v-for="job in filteredItems" :key="job.id">' +
                                '<td>' +
                                    '<a :href="job.href">' +
                                        '<strong>{{ job.title }}</strong>' +
                                    '</a><br>' +
                                    '<span v-if="job.internship" class="badge badge-primary">INTERNSHIP</span>' +
                                    '<metadata-list :items="job.topics"></metadata-list>' +
                                '</td>' +
                                '<td class="d-none d-md-table-cell logo-td text-center align-middle">' +
                                    '<img v-if="job.institution.images" :src="job.institution.images.sm" class="logo-sm"></img>' +
                                '</td>' +
                            '</tr>' +
                        '</tbody>' +
                    '</table>' +
                '</div>' +
            '</div>' +
        '</div>' +
    '',
    methods: {
        mapItems: function (items) {
            return mapper().jobs(items);
        },
        filterItems: function (items) {
            var filters = this.filters;
            return items.filter(function (obj) {
                return (filters.type == '__all__' || filters.type == obj.typeId)
                    && (filters.topic == '__all__' || _.contains(obj.topicIds, filters.topic))
                    && (filters.country == '__all__' || filters.country == obj.country.code)
                    && (filters.institution == '__all__' || filters.institution == obj.institution.id)
                    && (filters.careerLevel == '__all__' || _.contains(obj.careerLevelIds, filters.careerLevel))
            });
        }
    },
    computed: {
        careerLevels: function () {
            if (!this.items || !this.showExtraFilters) return [];
            return _.uniq(_.flatten(_.map(this.filteredItems, function (obj) { return obj.career_levels; })), function (obj) {
                return obj.id;
            }).sort(function (a, b) {
                return sortText(a.value, b.value);
            });
        },
        countries: function () {
            if (!this.items || !this.showExtraFilters) return [];
            return _.uniq(_.pluck(this.filteredItems, 'country'), function (obj) {
                return obj.code;
            }).sort(function (a, b) {
                return sortText(a.name, b.name);
            });
        },
        institutions: function () {
            if (!this.items || !this.showExtraFilters) return [];
            return _.uniq(_.pluck(this.filteredItems, 'institution'), function (obj) {
                return obj.id;
            }).sort(function (a, b) {
                return sortText(a.name, b.name);
            });
        }
    }
}));
