var SAVE_DELAY = 1500;


var FormElement = Vue.extend({
    store: ComponentStore,
    props: ['value', 'default', 'label', 'help', 'required'],
    computed: _.extend(
        Vuex.mapGetters(['requiredFields']), {
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
            '<h6>{{ label }} <span v-if="required" class="text-danger">*</span></h6>' +
            '<help-text v-if="help">{{ help }}</help-text>' +
            '<input ref="el" :value="value" @input="updateValue" :placeholder="placeholder" :type="type" class="form-control form-control-sm">' +
        '</div>' +
    ''
}));

Vue.component('date-input', FormElement.extend({
    props: ['placeholder'],
    template: '' +
        '<div class="form-group">' +
            '<h6>{{ label }} <span v-if="required" class="text-danger">*</span></h6>' +
            '<help-text v-if="help">{{ help }}</help-text>' +
            '<input ref="el" :value="value" @input="updateValue" :placeholder="placeholder" type="date" class="form-control form-control-sm">' +
        '</div>' +
    ''
}));

Vue.component('markdown-textarea', FormElement.extend({
    template: '' +
        '<div class="form-group">' +
            '<h6>{{ label }} <span v-if="required" class="text-danger">*</span></h6>' +
            '<help-text>You can use Markdown to format your text; you can find more information about the <a href="http://commonmark.org/help/" target="_blank">Markdown syntax here</a>. {{ help }}</help-text>' +
            '<textarea ref="el" :value="value" class="form-control form-control-sm" rows="16" @input="updateValue"></textarea>' +
        '</div>' +
    ''
}));

Vue.component('country-select', FormElement.extend({
    template: '' +
        '<div class="form-group" ref="el" :value="value">' +
            '<h6>{{ label }} <span v-if="required" class="text-danger">*</span></h6>' +
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
            '<h6>{{ label }} <span v-if="required" class="text-danger">*</span></h6>' +
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
            '<h6>{{ label }} <span v-if="required" class="text-danger">*</span></h6>' +
            '<help-text v-if="help">{{ help }}</help-text>' +
            '<div v-for="o in options" :key="o.id" class="form-check form-check-inline mr-2">' +
                '<label class="form-check-label">' +
                    '<input v-model="values" :value="o.id" type="checkbox" class="form-check-input">' +
                    '<small>{{ o.value }}</small>' +
                '</label>' +
            '</div>' +
        '</div>' +
    ''
}));


var AucompletePopupElement = FormElement.extend({
    data: function () {
        return {
            q: ''
        }
    },
    props: ['type'],
    computed: _.extend(
        Vuex.mapState(['institutions', 'projects']), {
        prop: function () {
            if (this.type == 'institution') return 'short_name';
            if (this.type == 'project') return 'acronym';
            return 'id';
        },
        items: function () {
            if (this.type == 'institution') return mapper().institutions(this.institutions);
            if (this.type == 'project') return mapper().projects(this.projects);
            return [];
        },
        filteredItems: function () {
            return filterMultiple(this.items, this.q);
        },
        text: function () {
            if (!this.value) return '(None)';
            return this.value[this.prop];
        }
    }),
    methods: {
        showModal: function () {
            $(this.$refs.modal).modal();
        }
    },
    created: function () {
        if (this.type == 'project') this.$store.commit('fetchProjects');
    }
});

Vue.component('autocomplete-popup', AucompletePopupElement.extend({
    template: '' +
        '<div>' +
            '<div class="form-group">' +
                '<h6>{{ label }} <span v-if="required" class="text-danger">*</span></h6>' +
                '<help-text v-if="help">{{ help }}</help-text>' +
                '<input ref="el" :value="text" @click="showModal" type="text" class="form-control form-control-sm" readonly>' +
            '</div>' +
            '<div ref="modal" class="modal" tabindex="-1" role="dialog">' +
                '<div class="modal-dialog modal-md" role="document">' +
                    '<div class="modal-content position-fixed">' +
                        '<div class="modal-body scrollable">' +
                            '<div class="input-group mb-3">' +
                                '<input v-model="q" type="text" class="form-control" placeholder="Search...">' +
                                '<div class="input-group-append">' +
                                    '<span class="input-group-text" id="basic-addon2">&times;</span>' +
                                '</div>' +
                            '</div>{{ q }}' +
                            '<!-- data-dismiss="modal" -->' +
                            '<simple-list :items="filteredItems" :prop="prop"></simple-list>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
    ''
}));
