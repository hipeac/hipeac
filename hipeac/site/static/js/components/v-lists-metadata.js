var MetadataList = Vue.extend({
    store: ComponentStore,
    props: ['items', 'title'],
    computed: _.extend(
        Vuex.mapState(['metadata']),
        Vuex.mapGetters(['metadataDict']), {
        sortedItems: function () {
            return this.items.sort(function (a, b) { return sortText(a.value, b.value); });
        }
    }),
    created: function () {
        this.$store.commit('fetchMetadata');
    }
});

Vue.component('metadata-badges', MetadataList.extend({
    props: ['color'],
    template: '' +
        '<div v-if="items.length" class="mb-4">' +
            '<h5 class="display-sm">{{ title }}</h5>' +
            '<span v-for="item in sortedItems" :key="item.id" :item="item" class="badge mr-1" :class="c">' +
                '{{ item.value }}' +
            '</span>' +
        '</div>' +
    '',
    computed: {
        c: function () {
            if (!this.color) return 'badge-primary';
            return 'badge-' + this.color;
        }
    }
}));

Vue.component('metadata-list', MetadataList.extend({
    template: '' +
        '<div v-if="items.length" class="mb-4">' +
            '<h5 class="display-sm">{{ title }}</h5>' +
            '<span v-for="item in sortedItems" :key="item.id" :item="item" class="badge badge-primary mr-1">' +
                '{{ item.value }}' +
            '</span>' +
        '</div>' +
    ''
}));
