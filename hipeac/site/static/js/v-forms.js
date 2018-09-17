var SAVE_DELAY = 1500;


var FormElement = Vue.extend({
    store: ComponentStore,
    props: ['value', 'default', 'label', 'help', 'required'],
    computed: _.extend(
        Vuex.mapGetters([]), {
    }),
    methods: {
        transformValue: function (value) {
            if (!value && this.default) return this.default;
            return value;
        },
        updateValue: function (event) {
            value = this.transformValue(event.target.value);
            this.$refs.el.value = value;
            this.$emit('input', value);
        }
    },
    watch: {
        'value': _.debounce(function (val, oldVal) {
            if (!oldVal) return;
            EventHub.$emit('form-updated', true);
        }, SAVE_DELAY)
    },
    mounted: function () {
        if (!this.value && this.default) this.$refs.el.value = this.default;
    }
});

Vue.component('help-text', {
    props: ['text'],
    template: '' +
        '<small class="form-text text-muted mb-2"><slot></slot></small>' +
    ''
});

Vue.component('custom-input', FormElement.extend({
    props: ['type', 'placeholder'],
    template: '' +
        '<div class="form-group">' +
            '<label>{{ label }} <span v-if="required" class="text-danger">*</span></label>' +
            '<help-text v-if="help">{{ help }}</help-text>' +
            '<input ref="el" :value="value" @input="updateValue" :placeholder="placeholder" :type="type" class="form-control form-control-sm">' +
        '</div>' +
    ''
}));

Vue.component('date-input', FormElement.extend({
    props: ['placeholder'],
    template: '' +
        '<div class="form-group">' +
            '<label>{{ label }} <span v-if="required" class="text-danger">*</span></label>' +
            '<help-text v-if="help">{{ help }}</help-text>' +
            '<input ref="el" :value="value" @input="updateValue" :placeholder="placeholder" type="date" class="form-control form-control-sm">' +
        '</div>' +
    ''
}));

Vue.component('markdown-textarea', FormElement.extend({
    template: '' +
        '<div class="form-group">' +
            '<label>{{ label }} <span v-if="required" class="text-danger">*</span></label>' +
            '<help-text>You can use Markdown to format your text; you can find more information about the <a href="http://commonmark.org/help/" target="_blank" rel="noopener">Markdown syntax here</a>. {{ help }}</help-text>' +
            '<textarea ref="el" :value="value" class="form-control form-control-sm" rows="16" @input="updateValue"></textarea>' +
        '</div>' +
    ''
}));

Vue.component('country-select', FormElement.extend({
    template: '' +
        '<div class="form-group" ref="el" :value="value">' +
            '<label>{{ label }} <span v-if="required" class="text-danger">*</span></label>' +
            '<help-text v-if="help">{{ help }}</help-text>' +
            '<select @change="updateValue" class="form-control form-control-sm">' +
                '<option v-for="c in countries" :key="c.value" :value="c.value" :selected="c.value == value.code">{{ c.display_name }}</option>' +
            '</select>' +
        '</div>' +
    '',
    computed: _.extend(
        Vuex.mapGetters(['countries']), {
    }),
    methods: {
        transformValue: function (value) {
            obj =  _.findWhere(this.countries, {value: value});
            return {
                'code': obj.value,
                'name': obj.display_name
            };
        }
    }
}));


var MetadataElement = FormElement.extend({
    props: ['type', 'sorting'],
    computed: _.extend(
        Vuex.mapState(['metadata']),
        Vuex.mapGetters(['metadataDict']), {
        options: function () {
            if (!this.metadata) return [];
            var type = this.type;
            var sorting = this.sorting || 'position';
            var sortingFunc = (sorting == 'position')
                ? function (a, b) { return sortInt(a['sorting'], b['sorting']); }
                : function (a, b) { return sortText(a['value'], b['value']); };

            return this.metadata.filter(function (obj) {
                return obj.type == type;
            }).sort(sortingFunc);
        }
    }),
    methods: {
        transformValue: function (value) {
            return _.pick(_.find(this.metadata, function (obj) { return obj.id == value; }), 'id', 'value');
        }
    },
    created: function () {
        this.$store.commit('fetchMetadata');
    }
});

var MetadataListElement = MetadataElement.extend({
    data: function () {
        return {
            values: null
        }
    },
    methods: {
        transformValue: function (value) {
            return this.metadataDict[value];
        }
    },
    watch: {
        'values': function (val, oldVal) {
            if (!oldVal) return;
            var mdict = this.metadataDict;
            this.$emit('input', val.map(function (id) { return _.pick(mdict[id], 'id', 'value'); }));
        }
    },
    created: function () {
        this.values = _.pluck(this.value, 'id');
    }
});

Vue.component('metadata-select', MetadataElement.extend({
    template: '' +
        '<div class="form-group" ref="el" :value="value">' +
            '<label>{{ label }} <span v-if="required" class="text-danger">*</span></label>' +
            '<help-text v-if="help">{{ help }}</help-text>' +
            '<select @change="updateValue" class="form-control form-control-sm">' +
                '<option v-for="o in options" :key="o.id" :value="o.id" :selected="o.id == value.id">{{ o.value }}</option>' +
            '</select>' +
        '</div>' +
    ''
}));

Vue.component('metadata-checkboxes', MetadataListElement.extend({
    template: '' +
        '<div class="form-group" ref="el" :value="value">' +
            '<label>{{ label }} <span v-if="required" class="text-danger">*</span></label>' +
            '<help-text v-if="help">{{ help }}</help-text>' +
            '<div v-for="o in options" :key="o.id" class="form-check form-check-inline mr-2">' +
                '<label class="form-check-label pointer">' +
                    '<input v-model="values" :value="o.id" type="checkbox" class="form-check-input">' +
                    '{{ o.value }}' +
                '</label>' +
            '</div>' +
        '</div>' +
    ''
}));


var AucompletePopupElement = FormElement.extend({
    data: function () {
        return {
            values: [],
            q: ''
        }
    },
    props: ['type'],
    computed: _.extend(
        Vuex.mapState(['institutions', 'projects']), {
        rows: function() {
            return (this.many) ? 4 : 1;
        },
        many: function () {
            return _.isArray(this.value);
        },
        items: function () {
            if (this.type == 'institution') return this.institutions;
            if (this.type == 'project') return this.projects;
            return [];
        },
        indexedItems: function () {
            return _.indexBy(this.items, 'id');
        },
        filteredItems: function () {
            if (this.q == '') return [];
            return filterMultiple(this.items, this.q);
        },
        selectedItems: function () {
            if (!this.items.length || !this.value) return [];
            var items = this.indexedItems;
            return _.map(this.values, function (id) {
                return items[id];
            });;
        },
        text: function () {
            if (!this.value) return '(None)';
            return _.map(this.selectedItems, function (item) { return item.display; }).join(', ');
        }
    }),
    methods: {
        add: function (id) {
            if (this.many) this.values.push(id);
            else this.values = [id];
            this.updateValue();
        },
        remove: function (id) {
            if (this.many) this.values = _.without(this.values, id);
            else this.values = [];
        },
        showModal: function () {
            $(this.$refs.modal).modal();
        }
    },
    watch: {
        'values': function (val, oldVal) {
            if (!oldVal) return;
            this.$emit('input', (this.many) ? val : val[0]);
        }
    },
    created: function () {
        this.values = (this.many) ? this.value : [this.value];
        if (this.type == 'institution') this.$store.commit('fetchInstitutions');
        if (this.type == 'project') this.$store.commit('fetchProjects');
    }
});

Vue.component('autocomplete-popup', AucompletePopupElement.extend({
    template: '' +
        '<div>' +
            '<div class="form-group">' +
                '<label>{{ label }} <span v-if="required" class="text-danger">*</span></label>' +
                '<help-text v-if="help">{{ help }}</help-text>' +
                '<textarea ref="el" :rows="rows" :value="text" @click="showModal" type="text" class="form-control form-control-sm pointer" readonly></textarea>' +
            '</div>' +
            '<div ref="modal" class="modal" tabindex="-1" role="dialog">' +
                '<div class="modal-dialog modal-md" role="document">' +
                    '<div class="modal-content">' +
                        '<div class="modal-header bg-light pb-0">' +
                            '<ul class="nav nav-tabs d-flex w-100">' +
                                '<li class="nav-item">' +
                                    '<a class="nav-link active" href="#"><i class="material-icons mr-2">search</i>Search</a>' +
                                '</li>' +
                                '<li class="nav-item pointer ml-auto" data-dismiss="modal">' +
                                    '<a class="nav-link" href="#"><i class="material-icons">close</i></a>' +
                                '</li>' +
                            '</ul>' +
                        '</div>' +
                        '<div class="modal-body">' +
                            '<div class="input-group input-group-sm mb-3">' +
                                '<input v-model="q" type="text" class="form-control" placeholder="Search...">' +
                                '<div v-if="q" class="input-group-append pointer" @click="q = \'\'">' +
                                    '<span class="input-group-text"><i class="material-icons sm">delete</i></span>' +
                                '</div>' +
                            '</div>' +
                            '<table class="table table-sm pointer mb-4">' +
                                '<tbody class="no-top-line">' +
                                '<tr v-for="item in selectedItems" :key="\'s\' + item.id" @click="remove(item.id)">' +
                                    '<td><strong>{{ item.display }}</strong></td>' +
                                    '<td class="text-right"><i class="material-icons sm text-danger">close</i></td>' +
                                '</tr>' +
                                '</tbody>' +
                            '</table>' +
                            '<!-- data-dismiss="modal" -->' +
                            '<strong v-if="q" class="d-block text-secondary mb-2">' +
                                '<small>{{ filteredItems.length }} matches for "{{ q }}"</small>' +
                                '<div v-if="filteredItems.length == 0" class="text-center">'+
                                    '<hr><catchphrase class="mb-4"><a href="mailto:webmaster@hipeac.net">Contact us</a> if you cannot find your {{ type }} in our list. We will add it to the website as soon as possible.</catchphrase>' +
                                '</div>'+
                            '</strong>' +
                            '<table class="table table-sm pointer table-hover">' +
                                '<tr v-for="item in filteredItems" :key="item.id" v-show="values.indexOf(item.id) == -1" @click="add(item.id)">' +
                                    '<td>{{ item.display }}</td>' +
                                    '<td class="text-right"><i class="material-icons sm text-success">add</i></td>' +
                                '</tr>' +
                            '</table>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
    ''
}));
