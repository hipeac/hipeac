var SAVE_DELAY = 1500;


var FormElement = Vue.extend({
    store: ComponentStore,
    data: function () {
        return {
            invalid: false,
            mutableHelpText: null,
        }
    },
    props: ['field', 'value', 'default', 'help', 'customLabel', 'hideRequired'],
    computed: _.extend(
        Vuex.mapGetters(['fields']), {
        f: function () {
            if (!this.fields || !this.field) return null;
            var parts = this.field.split('.');
            if (parts.length > 1) return this.fields[parts[0]].children[parts[1]];
            else return this.fields[parts[0]];
        },
        label: function () {
            if (!this.f) return this.customLabel || '';
            return this.customLabel || this.f.label;
        },
        helpText: function () {
            if (!this.f) return this.help;
            return (_.has(this.f, 'help_text')) ? [this.f.help_text, this.help].join('. ') : this.help;
        },
        required: function () {
            if (!this.f || this.hideRequired) return false;
            return this.f.required;
        }
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
        value: _.debounce(function (val, oldVal) {
            if (oldVal === undefined) return;
            if (this.required && !val) {
                this.invalid = true;
                return;
            } else {
                this.invalid = false;
                EventHub.$emit('form-updated');
            }
        }, SAVE_DELAY)
    },
    mounted: function () {
        if (!this.value && this.default) this.$refs.el.value = this.default;
    }
});

Vue.component('automatic-updates', {
    template: '' +
        '<button class="btn btn-block btn-light" disabled>' +
            '<icon name="autorenew" class="sm mr-1"></icon>Automatic updates active' +
        '</button>' +
    ''
});

Vue.component('only-input', FormElement.extend({
    props: ['type', 'placeholder'],
    template: '' +
        '<input ref="el" :value="value" @input="updateValue" :placeholder="placeholder" :type="type" class="form-control form-control-sm">' +
    ''
}));

Vue.component('help-text', {
    template: '' +
        '<small class="form-text text-muted mb-2"><slot></slot></small>' +
    ''
});

Vue.component('custom-label', {
    props: ['text', 'required'],
    template: '' +
        '<label>{{ text }} <span v-if="required" class="text-danger">*</span></label>' +
    ''
});

Vue.component('custom-input', FormElement.extend({
    props: ['type', 'placeholder'],
    template: '' +
        '<div class="form-group">' +
            '<custom-label :text="label" :required="required" :class="{\'mb-0\': helpText}"></custom-label>' +
            '<help-text v-if="helpText">{{ helpText }}</help-text>' +
            '<input ref="el" :value="value" @input="updateValue" :placeholder="placeholder" :type="type" class="form-control form-control-sm">' +
        '</div>' +
    ''
}));

Vue.component('date-input', FormElement.extend({
    props: ['placeholder'],
    template: '' +
        '<div class="form-group">' +
            '<custom-label :text="label" :required="required" :class="{\'mb-0\': helpText}"></custom-label>' +
            '<help-text v-if="helpText">{{ helpText }}</help-text>' +
            '<input ref="el" :value="value" @input="updateValue" :placeholder="placeholder" type="date" class="form-control form-control-sm">' +
        '</div>' +
    ''
}));

Vue.component('markdown-textarea', FormElement.extend({
    props: {
        rows: {
            type: Number,
            default: 12
        },
        showHelp: {
            type: Boolean,
            default: true
        }
    },
    template: '' +
        '<div>' +
            '<div class="form-group">' +
                '<custom-label :text="label" :required="required" :class="{\'mb-0\': showHelp}"></custom-label>' +
                '<help-text v-if="showHelp">You can use Markdown to format your text; you can find more information about the <a href @click.prevent="showModal">Markdown syntax here</a>.<span v-if="helpText"> {{ helpText }}</span></help-text>' +
                '<textarea ref="el" :value="value" class="form-control form-control-sm" :rows="rows" @input="updateValue"></textarea>' +
            '</div>' +
            '<div ref="markdownModal" class="modal" tabindex="-1" role="dialog">' +
                '<div class="modal-dialog modal-lg" role="document">' +
                    '<div class="modal-content p-4">' +
                        '<strong>Via commonmark.org</strong><hr>' +
                        '<iframe class="embed-responsive-item border-0" style="height: 600px" src="https://commonmark.org/help/"></iframe>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
    '',
    methods: {
        showModal: function () {
            $(this.$refs.markdownModal).modal();
        }
    }
}));

var SelectElement = FormElement.extend({
    props: {
        forceChoices: {
            type: Array,
            default: function () {
                return [];
            }
        },
        selectProperty: {
            type: String
        }
    },
    template: '' +
        '<div class="form-group" ref="el" :value="value">' +
            '<custom-label :text="label" :required="required" :class="{\'mb-0\': helpText}" ></custom-label>' +
            '<help-text v-if="helpText">{{ helpText }}</help-text>' +
            '<select @change="updateValue" class="form-control form-control-sm" :class="{\'is-invalid\': invalid}">' +
                '<option v-for="choice in choices" :key="choice.value" :value="choice.value" :selected="choice.value == compareValue">{{ choice.display_name }}</option>' +
            '</select>' +
            '<help-text v-if="mutableHelpText"><span class="text-info">{{ mutableHelpText }}</span></help-text>' +
        '</div>' +
    '',
    computed: {
        choices: function () {
            if (this.forceChoices.length > 0) return this.forceChoices;
            if (!this.f) return [];
            return this.f.choices;
        },
        compareValue: function () {
            if (this.selectProperty) return this.value[this.selectProperty];
            return this.value;
        }
    }
});

Vue.component('only-select', SelectElement.extend({
    template: '' +
        '<select ref="el" :value="value" @change="updateValue" class="form-control form-control-sm" :class="{\'is-invalid\': invalid}">' +
            '<option v-for="choice in choices" :key="choice.value" :value="choice.value" :selected="choice.value == compareValue">{{ choice.display_name }}</option>' +
        '</select>' +
    '',
}));

Vue.component('simple-select', SelectElement.extend({

}));

Vue.component('country-select', SelectElement.extend({
    props: {
        force: {
            type: Boolean,
            default: false
        }
    },
    methods: {
        transformValue: function (value) {
            var obj = _.findWhere(this.choices, {value: value});
            return {
                code: obj.value,
                name: obj.display_name,
            }
        },
        forceCountry: function (code) {
            if (!this.force) return;
            try {
                value = this.transformValue(code);
                this.mutableHelpText = null;
                this.$refs.el.value = value;
                this.$emit('input', value);
            } catch (err) {
                this.mutableHelpText = 'Please note that only jobs in Europe can be posted to the HiPEAC Jobs portal.';
            }
        }
    },
    created: function () {
        EventHub.$on('force-country', this.forceCountry);
    }
}));

var MetadataElement = FormElement.extend({
    props: {
        type: {
            type: String
        },
        sorting: {
            type: String,
            default: 'position'
        }
    },
    computed: _.extend(
        Vuex.mapState(['metadata']),
        Vuex.mapGetters(['metadataDict', 'fields']), {
        options: function () {
            if (!this.metadata) return [];
            var type = this.type;
            var sortingFunc = (this.sorting == 'position')
                ? function (a, b) { return sort().int(a['position'], b['position']); }
                : function (a, b) { return sort().text(a['value'], b['value']); };

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
            '<custom-label :text="label" :required="required" :class="{\'mb-0\': helpText}"></custom-label>' +
            '<help-text v-if="helpText">{{ helpText }}</help-text>' +
            '<select @change="updateValue" class="form-control form-control-sm">' +
                '<option v-for="o in options" :key="o.id" :value="o.id" :selected="o.id == value.id">{{ o.value }}</option>' +
            '</select>' +
        '</div>' +
    ''
}));

Vue.component('metadata-checkboxes', MetadataListElement.extend({
    template: '' +
        '<div class="form-group" ref="el" :value="value">' +
            '<custom-label :text="label" :required="required" :class="{\'mb-0\': helpText}"></custom-label>' +
            '<help-text v-if="helpText">{{ helpText }}</help-text>' +
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
            });
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
        },
        updateValue: function (event) {
            if (this.many) {
                this.$emit('input', this.values);
            } else {
                this.$emit('input', this.values[0]);
                if (this.type == 'institution') {
                    var countryCode = _.findWhere(this.filteredItems, {id: this.values[0]}).country.code;
                    EventHub.$emit('force-country', countryCode);
                }
            }
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
                '<custom-label :text="label" :required="required" :class="{\'mb-0\': helpText}"></custom-label>' +
                '<help-text v-if="helpText">{{ helpText }}</help-text>' +
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
                            '</strong>' +
                            '<div v-if="!q || filteredItems.length == 0" class="text-center">'+
                                '<hr v-show="q"><catchphrase class="mb-4"><a href="mailto:missing@hipeac.net">Contact us</a> if you cannot find your {{ type }} in our list. We will add it to the website as soon as possible.</catchphrase>' +
                            '</div>' +
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

Vue.component('link-fieldset', FormElement.extend({
    data: function () {
        return {
            links: null
        }
    },
    template: '' +
        '<div class="form-group">' +
            '<custom-label :text="label" :required="required" :class="{\'mb-0\': helpText}"></custom-label>' +
            '<help-text v-if="helpText">{{ helpText }}</help-text>' +
            '<table class="w-100">' +
                '<tbody>' +
                    '<tr v-for="link in links">' +
                        '<td class="pl-0">' +
                            '<only-input v-model="link.url"></only-input>' +
                        '</td>' +
                        '<td class="w-25">' +
                            '<only-select v-model="link.type" :force-choices="typeChoices"></only-select>' +
                        '</td>' +
                        '<td class="text-right px-0"><a href @click.prevent="removeLink(link)" class="text-danger"><icon name="remove_circle" class="sm"></icon></a></td>' +
                    '</tr>' +
                '</tbody>' +
                '<tfoot class="d-block mt-1">' +
                    '<small><a href @click.prevent="addLink"><icon name="add" class="sm mr-1"></icon>Add link</a></small>' +
                '</tfoot>' +
            '</table>' +
        '</div>' +
    '',
    computed: {
        typeChoices: function () {
            if (!this.f) return [];
            return this.f.child.children.type.choices;
        }
    },
    methods: {
        addLink: function () {
            this.links.push({
                'type': 'website',
                'url': '',
            });
            this.$emit('input', this.links);
        },
        removeLink: function (link) {
            this.links = _.without(this.links, link);
            this.$emit('input', this.links);
        }
    },
    created: function () {
        this.links = _.clone(this.value);
    }
}));
