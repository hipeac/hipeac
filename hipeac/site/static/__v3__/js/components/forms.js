var HipeacFormComponents = {

  'hipeac-editor': {
    data: function () {
      return {
        dialogVisible: false,
      };
    },
    props: {
      saveEventName: {
        type: String,
        default: null
      },
      obj: {
        type: Object,
        default: null
      },
      objKey: {
        type: String,
        default: 'id'
      },
      position: {
        type: String,
        default: 'top'
      },
      size: {
        type: String,
        default: 'sm'
      }
    },
    template: `
      <q-dialog :position="position" v-model="showDialog" @show="dialogVisible = true">
        <q-card v-if="obj" style="max-width: 95vw;" :style="{'width': sizePx}">
          <q-card-section class="scroll q-px-lg q-py-xl" style="min-height: 250px; max-height: 75vh;">
            <slot></slot>
          </q-card-section>
          <q-separator />
          <q-card-actions align="right" class="q-py-md q-px-lg">
            <q-btn flat v-close-popup label="Close" color="grey-8" />
            <q-space />
            <q-btn v-if="saveEventName" unelevated @click="save" :label="(objKey in obj) ? 'Update' : 'Create'" color="primary" class="q-px-md" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    `,
    computed: {
      sizePx: function () {
        return {
          'sm': '400px',
          'md': '550px',
          'lg': '900px'
        }[this.size] || '400px';
      },
      showDialog: {
        get: function () {
          return this.obj != null;
        },
        set: function (val) {
          if (this.dialogVisible) {
            this.dialogVisible = false;
            EventEmitter.emit('hipeac-editor-hide');
          }
        }
      }
    },
    methods: {
      hideDialog: function () {
        this.dialogVisible = false;
        EventEmitter.emit('hipeac-editor-hide');
      },
      save: function () {
        EventEmitter.emit(this.saveEventName, this.obj);
      }
    },
    created: function () {
      EventEmitter.on('hipeac-editor-hide-after-save', this.hideDialog);
    },
    beforeUnmount: function () {
      EventEmitter.off('hipeac-editor-hide-after-save');
    }
  },

  'hipeac-conference-poster-list': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        stack: []
      };
    },
    props: {
      addText: {
        type: String,
        default: 'Add poster'
      },
      modelValue: {
        type: Array
      },
      sessions: {
        type: Array,
        required: true
      }
    },
    template: `
      <div>
        <div v-for="el in stack" class="row q-col-gutter-xs q-mb-sm items-center">
          <q-input class="col-8" filled dense v-model="el['title']" label="Poster title"></q-input>
          <q-select class="col-3" filled dense v-model="el['session']" label="Session" :options="options" emit-value map-options>
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.title }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
          <div class="col-1 text-center">
            <hipeac-remove-icon @click.prevent="removeFromStack(idx)" />
          </div>
        </div>
        <q-btn outline @click="addToStack" size="sm" color="green" icon="add" :label="addText"></q-btn>
      </div>
    `,
    computed: {
      options: function () {
        return this.sessions.map(function (obj) {
          return {
            label: obj.start.format('dddd'),
            title: obj.title,
            value: obj.id,
          }
        });
      }
    },
    methods: {
      addToStack: function () {
        this.stack.push({
          'title': '',
          'authors': '',
          'session': null,
        });
        this.$emit('update:modelValue', this.stack);
      },
      removeFromStack: function (idx) {
        this.stack.splice(idx, 1);
        this.$emit('update:modelValue', this.stack);
      }
    },
    created: function () {
      this.stack = this.modelValue;
    }
  },

  'hipeac-text-list': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        stack: []
      };
    },
    props: {
      addText: {
        type: String,
        default: 'Add'
      },
      fields: {
        type: Array,
        default: function () {
          return [];
        }
      },
      modelValue: {
        type: Array,
        default: function () {
          return [];
        }
      }
    },
    template: `
      <div class="q-mb-lg">
        <input v-model="mutable" type="hidden" />
        <div v-for="el in stack" class="row q-col-gutter-xs q-mb-sm items-center">
          <div v-for="field in fields" class="col">
            <q-input v-if="field.type == 'text'" filled dense v-model="el[field.id]" :label="field.label"></q-input>
            <q-select v-if="field.type == 'select'" filled dense v-model="el[field.id]" :label="field.label" :options="field.options"></q-select>
          </div>
          <div class="col-1 text-center">
            <hipeac-remove-icon @click.prevent="removeFromStack(el)" />
          </div>
        </div>
        <q-btn outline @click="addToStack" size="sm" color="green" icon="add" :label="addText"></q-btn>
      </div>
    `,
    computed: {
      mutable: {
        get: function () {
          return this.modelValue;
        },
        set: function (val) {
          this.$emit('update:modelValue', val);
        }
      }
    },
    methods: {
      addToStack: function () {
        this.stack.push({
          'id': '',
          'title': '',
        });
        this.$emit('update:modelValue', this.stack);
      },
      removeFromStack: function (item) {
        this.stack = _.without(this.stack, item);
        this.$emit('update:modelValue', this.stack);
      }
    },
    created: function () {
      this.stack = this.modelValue;
    }
  },

  'hipeac-datepicker': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        mutable: null
      };
    },
    props: {
      modelValue: {
        type: String
      },
      label: {
        type: String,
        required: true
      },
      options: {
        type: [Array, Function],
        default: function () {
          return function () {
            return true;
          };
        }
      },
      hint: {
        type: [String, Boolean],
        default: false
      },
      hintClass: {
        type: [String],
        default: ''
      },
      withTime: {
        type: Boolean,
        default: false
      },
      allowNull: {
        type: Boolean,
        default: false
      }
    },
    template: `
      <div>
        <input v-model="mutable" type="hidden" />
        <q-input filled dense :bottom-slots="hint !== false" v-model="mutable" :label="label">
          <template v-slot:append>
            <q-icon name="event" class="cursor-pointer" size="xs">
              <q-popup-proxy ref="qDateProxy" transition-show="scale" transition-hide="scale">
                <q-date v-model="mutable" :mask="mask" :options="options" :default-year-month="yearMonth" first-day-of-week="1">
                  <div class="row items-center justify-end">
                    <q-btn v-close-popup label="Close" color="primary" flat />
                  </div>
                </q-date>
              </q-popup-proxy>
            </q-icon>
            <q-icon v-if="withTime" name="access_time" class="cursor-pointer q-ml-sm" size="xs">
              <q-popup-proxy transition-show="scale" transition-hide="scale">
                <q-time v-model="mutable" :mask="mask" format24h>
                  <div class="row items-center justify-end">
                    <q-btn v-close-popup label="Close" color="primary" flat />
                  </div>
                </q-time>
              </q-popup-proxy>
            </q-icon>
            <q-icon v-if="allowNull" name="cancel" @click="mutable = null" class="cursor-pointer q-ml-sm" size="xs" />
          </template>
          <template v-if="hint" v-slot:hint>
            <div :class="hintClass">{{ hint }}</div>
          </template>
        </q-input>
      </div>
    `,
    computed: {
      mask: function () {
        return (this.withTime)
          ? 'YYYY-MM-DDTHH:mm'
          : 'YYYY-MM-DD';
      },
      yearMonth: function () {
        if (_.isArray(this.options)) return _.first(this.options).substring(0, 7);
        return moment().format('YYYY/MM');
      }
    },
    watch: {
      'mutable': function (val) {
        this.$emit('update:modelValue', val);
      }
    },
    created: function () {
      this.mutable = this.modelValue;
    }
  },

  'hipeac-markdown': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        mutable: null
      };
    },
    props: {
      modelValue: {
        type: String
      },
      label: {
        type: String,
        default: 'Text'
      }
    },
    template: `
      <div>
        <div class="row q-col-gutter-lg">
          <div class="col-12 col-md-6 align-items-stretch">
            <q-input filled dense v-model="mutable" :label="label" type="textarea" autogrow bottom-slots>
              <template v-slot:hint>
                <div>You can use Markdown to format your text; you can find more information about the <a href="https://commonmark.org/help/" target="_blank" rel="noopener">Markdown syntax here</a>.</div>
              </template>
            </q-input>
          </div>
          <div class="col-12 col-md-6 align-items-stretch">
            <div v-if="$q.screen.gt.sm" class="marked-preview bg-grey-1 text-body2 full-height">
              <marked :text="mutable"></marked>
            </div>
          </div>
        </div>
      </div>
    `,
    watch: {
      'mutable': function (val) {
        this.$emit('update:modelValue', val);
      }
    },
    created: function () {
      this.mutable = this.modelValue;
    }
  },

  'hipeac-country-select': {
    setup: function () {
      Vuex.useStore();
    },
    emits: ['update:modelValue'],
    data: function () {
      return {
        mutable: null
      };
    },
    props: {
      modelValue: {
        type: Object
      }
    },
    template: `
      <q-select dense filled v-model="mutable" :options="options" label="Country" option-value="code"
        option-label="name" />
    `,
    computed: _.extend(
      Vuex.mapState('common', ['countries']), {
      options: function () {
        var c = [];
        if (!this.countries) return c;

        _.each(this.countries, function (val, key) {
          c.push({
            code: key,
            name: val
          });
        });

        return c;
      }
    }),
    watch: {
      'mutable': function (val) {
        this.$emit('update:modelValue', val);
      }
    },
    created: function () {
      this.mutable = this.modelValue;
      this.$store.commit('common/getCountries');
    }
  },

  'hipeac-metadata-select': {
    setup: function () {
      Vuex.useStore();
    },
    emits: ['update:modelValue'],
    data: function () {
      return {
        mutable: null
      };
    },
    props: {
      modelValue: {
        type: Number
      },
      label: {
        type: String,
        required: true
      },
      type: {
        type: String,
        required: true
      }
    },
    template: `
      <q-select
        v-model="mutable"
        :label="label"
        :options="options"
        dense
        filled
        emit-value
        map-options
      />
    `,
    computed: _.extend(
      Vuex.mapState('common', ['metadata']), {
      options: function () {
        var o = [];
        var self = this;

        if (!this.metadata) return o;

        _.each(this.metadata.filter(function (obj) {
          return obj.type == self.type;
        }), function (m) {
          o.push({
            value: m.id,
            label: m.value,
          });
        });

        return o;
      }
    }),
    watch: {
      'mutable': function (val) {
        this.$emit('update:modelValue', val);
      }
    },
    created: function () {
      this.mutable = this.modelValue;
      this.$store.commit('common/getMetadata');
    }
  },

  'hipeac-metadata-rel-select': {
    setup: function () {
      Vuex.useStore();
    },
    emits: ['update:modelValue'],
    data: function () {
      return {
        cache: null,
        mutable: null,
        options: []
      };
    },
    props: {
      modelValue: {
        type: Array,
        default: function () {
          return [];
        }
      },
      label: {
        type: String,
        required: true
      },
      type: {
        type: String,
        required: true
      }
    },
    template: `
      <q-select
        v-model="mutable"
        :options="options"
        :label="label"
        multiple
        dense
        filled
        emit-value
        map-options
        use-chips
        @filter="search"
        use-input
        input-debounce="100"
      >
        <template v-slot:no-option>
          <q-item>
            <q-item-section class="text-grey-7 text-caption">
              <span>No results found. <a href="mailto:missing@hipeac.net">Contact us</a> if you think something is missing in our list.</span>
            </q-item-section>
          </q-item>
        </template>
      </q-select>
    `,
    computed: _.extend(
      Vuex.mapState('common', ['metadata']), {
      initialOptions: function () {
        if (!this.metadata) return [];

        var self = this;

        return this.metadata.filter(function (obj) {
          return obj.type == self.type;
        }).map(function (obj) {
          return {
            _q: obj._q,
            value: obj.id,
            label: obj.value,
          };
        });
      }
    }),
    methods: {
      initOptions: function () {
        if (!this.initialOptions.length) {
          setTimeout(function () {
            this.initOptions();
          }.bind(this), 25);
          return;
        }

        this.options = this.initialOptions;
      },
      search: function (q, update, abort) {
        update(function () {
          if (q == '' || q.length < 2) {
            this.options = this.initialOptions;
          } else {
            var skipNegatives = true;
            this.options = Hipeac.utils.filter(this.initialOptions || [], q, skipNegatives);
          }
        }.bind(this));
      },
      updateCache: function (val) {
        this.cache = _.clone(val[this.type]);
      }
    },
    watch: {
      'mutable': function (val) {
        var map = _.indexBy(this.cache, 'mid');

        this.$emit('update:modelValue', val.map(function (id) {
          return map[id] || {
            mid: id
          };
        }));
      }
    },
    created: function () {
      this.cache = _.clone(this.modelValue);
      this.mutable = _.pluck(this.modelValue, 'mid');
      this.$store.commit('common/getMetadata');
      this.initOptions();
      EventEmitter.on('update:user:rel_metadata', this.updateCache);
    }
  },

  'hipeac-search-select': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        mutable: null,
        options: []
      };
    },
    props: {
      modelValue: {
        type: Object
      },
      initialOptions: {
        type: Array,
        default: function () {
          return [];
        }
      },
      label: {
        type: String,
        required: true
      },
      type: {
        type: String,
        required: true
      },
      clearable: {
        type: Boolean,
        default: true
      }
    },
    template: `
      <q-select
        v-model="mutable"
        :options="options"
        :label="label"
        dense
        filled
        :option-label="optionLabel"
        @filter="search"
        use-input
        input-debounce="200"
        :clearable="clearable"
      >
        <template v-slot:no-option>
          <q-item>
            <q-item-section class="text-grey-7 text-caption">
              <span>No results found. <a href="mailto:missing@hipeac.net">Contact us</a> if you think something is missing in our list.</span>
            </q-item-section>
          </q-item>
        </template>
        <template v-slot:option="scope">
          <q-item v-bind="scope.itemProps">
            <q-item-section>
              <q-item-label>{{ scope.opt[optionLabel] }}</q-item-label>
              <q-item-label caption v-if="scope.opt[optionLabel] != scope.opt.name">{{ scope.opt.name }}</q-item-label>
            </q-item-section>
          </q-item>
        </template>
      </q-select>
    `,
    computed: {
      optionLabel: function () {
        return {
          'institution': 'short_name',
          'project': 'acronym'
        }[this.type] || 'label';
      }
    },
    methods: {
      search: function (q, update, abort) {
        if (q == '' || q.length < 3) {
          this.options = this.initialOptions || [];
          abort();
          return;
        }

        var self = this;
        var url = {
          'institution': '/api/v1/network/institutions/',
          'project': '/api/v1/network/projects/'
        }[this.type];

        axios.get(url, {
          params: {
            search: q
          }
        }).then(function (res) {
          update(function () {
            self.options = res.data.results;
          });
        });
      }
    },
    watch: {
      'mutable': function (val) {
        this.$emit('update:modelValue', val);
      }
    },
    created: function () {
      this.mutable = this.modelValue;
      this.options = _.clone(this.initialOptions);
    }
  },

  'hipeac-search-rel-select': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        cache: null,
        mutable: null
      };
    },
    props: {
      modelValue: {
        type: Array,
        default: function () {
          return [];
        }
      },
      initialOptions: {
        type: Array,
        default: function () {
          return [];
        }
      },
      label: {
        type: String,
        required: true
      },
      type: {
        type: String,
        required: true
      }
    },
    template: `
      <hipeac-search-select
        v-model="mutable"
        :initial-options="initialOptions"
        :label="label"
        :type="type"
        multiple
        emit-value
        map-options
        use-chips
        :clearable="false"
      />
    `,
    methods: {
      updateCache: function (val) {
        this.cache = _.clone(val[this.type]);
      }
    },
    watch: {
      'mutable': function (val) {
        var map = _.indexBy(this.cache, 'oid');

        this.$emit('update:modelValue', val.map(function (obj) {
          return map[obj.id] || {
            oid: obj.id
          };
        }));
      }
    },
    created: function () {
      this.cache = _.clone(this.modelValue);
      this.mutable = this.initialOptions;
      EventEmitter.on('update:user:rel_objects', this.updateCache);
    }
  },

  'hipeac-custom-fieldsets': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        mutable: null
      };
    },
    props: {
      modelValue: {
        type: Object
      },
      fieldsets: {
        type: Array,
        default: function () {
          return [];
        }
      },
      event: {
        type: Object
      }
    },
    template: `
      <div v-if="mutable" v-for="fieldset in fieldsets" class="q-mt-lg">
        <h6 class="q-mb-md">{{ fieldset.title }}</h6>
        <div class="row q-col-gutter-md items-end">
          <div v-for="field in fieldset.fields" class="col-12" :class="field.class">
            <div v-if="field.text">{{ field.text }} <strong v-show="field.required" class="text-orange">*</strong></div>
            <div v-if="field.type" :class="{'q-mt-md': field.text}">
              <q-input v-if="field.type == 'text' || field.type == 'email'" v-model="mutable.custom_data[field.id]" :type="field.type" filled dense :autogrow="field.type == 'text'" />
              <hipeac-text-list v-else-if="field.type == 'text_list'" v-model="mutable.custom_data[field.id]" :fields="field.fields" :limit="field.limit" />
              <q-option-group v-else-if="field.type == 'single_choice' || field.type == 'multiple_choice'" v-model="mutable.custom_data[field.id]" :options="field.options" :type="(field.type == 'single_choice') ? 'radio' : 'checkbox'" />
              <q-item v-else-if="field.type == 'checkbox'" class="q-pl-none">
                <q-item-section avatar class="q-px-none">
                  <q-checkbox v-model="mutable.custom_data[field.id]"
                    keep-color :color="(field.mandatory && !mutable.custom_data[field.id]) ? 'orange' : null"></q-checkbox>
                </q-item-section>
                <q-item-section>
                  <q-item-label><marked :text="field.label"></marked></q-item-label>
                  <small v-show="field.mandatory" class="text-caption text-grey-8">Mandatory</small>
                </q-item-section>
              </q-item>
              <hipeac-datepicker v-else-if="field.type == 'date'" v-model="mutable.custom_data[field.id]" :label="field.label" :options="field.options" />
              <div v-else>{{ field }}</div>
            </div>
          </div>
        </div>
      </div>
    `,
    computed: {
      topicsSorted: function () {
        return this.event.topics.sort(function (a, b) {
          return Hipeac.utils.sortText(a.name, b.name);
        });
      },
      tracksSorted: function () {
        return this.event.tracks.sort(function (a, b) {
          return Hipeac.utils.sortText(a.name, b.name);
        });
      }
    },
    watch: {
      'mutable': {
        deep: true,
        handler: function (val) {
          this.$emit('update:modelValue', val);
        }
      }
    },
    created: function () {
      this.mutable = this.modelValue;
    }
  },

  'hipeac-file-list': {
    props: {
      files: {
        type: Array,
        default: function () {
          return [];
        }
      },
      icon: {
        type: String,
        default: 'file_present'
      },
      confirmRemoveMsg: {
        type: String,
        default: 'Are you sure you want to delete this file?'
      },
      removeEventName: {
        type: String,
        default: 'hipeac-file-removed'
      }
    },
    template: `
      <q-list dense class="q-gutter-y-xs">
        <q-item v-for="item in items" class="bg-grey-2 rounded-borders">
          <q-item-section class="text-caption">
            <q-item-label :lines="1">{{ item.filename }}</q-item-label>
          </q-item-section>
          <q-item-section side>
            <div class="text-grey-8 q-gutter-sm">
              <q-btn flat dense icon="visibility" size="sm" type="a" :href="item.url" target="_blank" />
              <q-btn flat dense icon="backspace" color="red-12" size="sm" @click.prevent="remove(item)" />
            </div>
          </q-item-section>
        </q-item>
      </q-list>
    `,
    computed: {
      items: function () {
        return this.files.map(function (obj) {
          obj.filename = obj.url.split('\\').pop().split('/').pop();
          return obj;
        });
      }
    },
    methods: {
      remove: function (obj) {
        var eventName = this.removeEventName;
        Hipeac.utils.confirmAction(this.confirmRemoveMsg, function () {
          Hipeac.api.remove(obj, function (res) {
            EventEmitter.emit(eventName, obj);
          });
        });
      }
    }
  },

  'hipeac-accompanying': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        dialog: false,
        stack: []
      };
    },
    props: {
      modelValue: {
        type: Array,
        default: function () {
          return [];
        }
      },
      label: {
        type: String,
        default: ''
      },
      fee: {
        type: Number,
        default: 0
      }
    },
    template: `
      <div>
        <q-dialog v-model="dialog" style="min-width: 400px">
          <q-card>
            <q-card-section class="scroll q-pa-lg" style="min-height: 250px; max-height: 75vh;">
              <div class="text-h6 q-mb-sm">Accompanying persons</div>
              <p>Accompanying persons can attend "{{ label }}" for an extra fee of <strong>{{ fee }} EUR</strong> per person<span v-if="totalFee"> ({{ totalFee }} EUR in total)</span>.</p>
              <input v-model="mutable" type="hidden" />
              <div v-for="el in stack" class="row q-col-gutter-xs q-mb-sm items-center">
                <q-input filled dense v-model="el.name" label="name" class="col"></q-input>
                <hipeac-metadata-select v-model="el.dietary" type="meal_preference" label="Dietary requirements" class="col" />
                <div class="col-1 text-center">
                  <hipeac-remove-icon @click.prevent="removeFromStack(el)" />
                </div>
              </div>
              <q-btn outline @click="addToStack" size="sm" color="green" icon="add" label="Add person"></q-btn>
            </q-card-section>
            <q-card-actions align="right" class="q-py-md q-px-lg">
              <q-btn flat label="Cancel" color="grey" @click="stack = []" v-close-popup />
              <q-btn flat label="Update" color="primary" @click="update" :disable="disableSave" v-close-popup />
            </q-card-actions>
          </q-card>
        </q-dialog>
        <small @click.prevent="dialog = true" class="text-primary cursor-pointer"><span v-if="modelValue.length">{{ modelValue.length }}</span><span v-else>Add</span> accompanying person<span v-if="modelValue.length != 1">s</span></small>
      </div>
    `,
    computed: {
      disableSave: function () {
        if (this.stack.length == 0) return true;
        return _.contains(_.pluck(this.stack, 'name'), '');
      },
      mutable: {
        get: function () {
          return this.modelValue;
        },
        set: function (val) {
          this.$emit('update:modelValue', val);
        }
      },
      totalFee: function () {
        if (this.fee == 0) return 0;
        return this.fee * this.stack.length;
      }
    },
    methods: {
      addToStack: function () {
        this.stack.push({
          'name': '',
          'dietary': 'none',
        });
      },
      removeFromStack: function (item) {
        this.stack = _.without(this.stack, item);
      },
      update: function () {
        this.$emit('update:modelValue', this.stack);
      }
    },
    created: function () {
      this.stack = this.modelValue;
    }
  }

};
