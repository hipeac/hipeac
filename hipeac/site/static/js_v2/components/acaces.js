Vue.component('acaces-registrations-table', {
  data: function () {
    return {
      togglePlaceholder: false,
      dialogVisible: false,
      mutableLists: {
        admitted: [],
        granted: []
      },
      columns: [
        {
          name: 'id',
          field: 'id',
          sortable: true,
          label: 'ID',
          align: 'left',
        },
        {
          name: 'admitted',
          field: 'id',
          label: 'Admit',
          align: 'center',
        },
        {
          name: 'granted',
          field: 'id',
          label: 'Grant',
          align: 'center',
        },
        {
          name: 'user_gender',
          field: 'user_gender',
          align: 'center',
          label: 'Gender'
        },
        {
          name: 'user_name',
          field: 'user_name',
          sortable: true,
          align: 'left',
          label: 'Student'
        },
        {
          name: 'country_code',
          field: 'country_code',
          sortable: true,
          align: 'center',
          label: 'Country'
        },
        {
          name: 'user_affiliation',
          field: 'user_affiliation',
          sortable: true,
          align: 'left',
          label: 'Affiliation'
        },
        {
          name: 'date',
          field: 'created_at',
          sortable: true,
          align: 'left',
          label: 'Date'
        },
        {
          name: 'visa_status',
          align: 'center',
          label: 'Visa'
        },
        {
          name: 'payment_status',
          align: 'center',
          label: 'Payment'
        }
      ],
      initialPagination: {
        rowsPerPage: 0,
        sortBy: 'date',
        descending: true
      }
    }
  },
  props: {
    data: {
      type: Array,
      required: true
    },
    admittedIds: {
      type: Array,
      default: function () {
        return [];
      }
    },
    grantedIds: {
      type: Array,
      default: function () {
        return [];
      }
    },
    uuid: {
      type: String,
      default: null
    },
    showUser: {
      type: Boolean,
      default: true
    },
    grantsPerCountry: {
      type: [Boolean, Object],
      default: false
    }
  },
  template: `
    <div>
      <q-table flat dense loading row-key="id" :data="registrations" :columns="columns" :pagination="initialPagination">
        <template v-slot:body="props">
          <q-tr :props="props" class="cursor-pointer" @click="$router.replace({params: {uuid: props.row.uuid}})" :class="{'bg-orange-1': props.row.uuid == uuid}">
            <q-td key="id" :props="props"><samp><small>{{ props.row.id }}</small></samp></q-td>
            <q-td key="admitted" :props="props">
              <q-toggle size="xs" v-model="mutableLists['admitted']" :val="props.row.id" color="green" checked-icon="check" unchecked-icon="arrow_forward_ios" />
            </q-td>
            <q-td key="granted" :props="props">
              <q-toggle v-if="props.row.custom_data.grant_requested" size="xs" v-model="mutableLists['granted']" :val="props.row.id" color="green" :disable="disableToggle(props.row)" checked-icon="check" :unchecked-icon="(disableToggle(props.row)) ? 'null' : 'arrow_forward_ios'" />
              <q-toggle v-else size="xs" v-model="togglePlaceholder" :val="false" color="green" disable class="transparent" />
            </q-td>
            <q-td key="user_gender" :props="props">
              <q-icon :name="{'male': 'male', 'female': 'female', 'non_binary': 'toll', null: 'toll'}[props.row.user_gender]"></q-icon>
            </q-td>
            <q-td key="user_name" :props="props">{{ props.row.user_name }}</q-td>
            <q-td key="country_code" :props="props">
              <country-flag :code="props.row.country_code"></country-flag>
            </q-td>
            <q-td key="user_affiliation" :props="props" class="full-width">{{ props.row.user_affiliation }}</q-td>
            <q-td key="date" :props="props"><small>{{ props.row.date.format('LLLL') }}</small></q-td>
            <q-td key="visa_status" :props="props">
              <span v-if="props.row.visa_requested">
                <q-badge v-if="props.row.visa_sent" color="positive">
                  <q-icon name="done" class="q-mr-xs"></q-icon>Yes</q-badge>
                <q-badge v-else color="orange-5">
                  <q-icon name="radio_button_unchecked" class="q-mr-xs"></q-icon>Yes</q-badge>
              </span>
              <q-badge v-else outline color="grey">
                <q-icon name="close" class="q-mr-xs"></q-icon>No</q-badge>
            </q-td>
            <q-td key="invoice_status" :props="props">
              <span v-if="props.row.invoice_requested">
                <q-badge v-if="props.row.invoice_sent" color="positive">
                  <q-icon name="done" class="q-mr-xs"></q-icon>Yes</q-badge>
                <q-badge v-else color="orange-5">
                  <q-icon name="radio_button_unchecked" class="q-mr-xs" />Yes</q-badge>
              </span>
              <q-badge v-else outline color="grey">
                <q-icon name="close" class="q-mr-xs"></q-icon>No</q-badge>
            </q-td>
            <q-td key="payment_status" :props="props">
              <q-badge v-if="props.row.is_paid" color="positive"><q-icon name="done" class="q-mr-xs" />Paid</q-badge>
              <q-badge v-else color="orange-5">
                <q-icon name="radio_button_unchecked" class="q-mr-xs" />Pending</q-badge>
            </q-td>
          </q-tr>
        </template>
      </q-table>
      <q-dialog v-model="showDialog" @show="dialogVisible = true">
        <q-card v-if="registration" style="width: 500px">
          <q-card-section>
            <display-4 class="q-mb-lg">Registration #{{ registration.id }}</display-4>
            <q-list dense>
              <q-item>
                <q-item-section avatar><q-icon name="schedule"></q-icon></q-item-section>
                <q-item-section>{{ registration.date.format('LLLL') }}</q-item-section>
              </q-item>
              <q-separator inset="item"></q-separator>
              <q-item>
                <q-item-section avatar><q-icon name="accessibility_new"></q-icon></q-item-section>
                <q-item-section>{{ registration.user_name }}</q-item-section>
              </q-item>
              <q-separator inset="item"></q-separator>
              <q-item>
                <q-item-section avatar><q-icon name="email"></q-icon></q-item-section>
                <q-item-section>{{ registration.user.email }}</q-item-section>
              </q-item>
              <q-separator inset="item"></q-separator>
              <q-item>
                <q-item-section avatar><q-icon :name="{'male': 'male', 'female': 'female', 'non_binary': 'toll', null: 'toll'}[registration.user_gender]"></q-icon></q-item-section>
                <q-item-section class="text-capitalize">{{ registration.user_gender }}</q-item-section>
              </q-item>
              <q-separator inset="item"></q-separator>
              <q-item>
                <q-item-section avatar><q-icon name="business"></q-icon></q-item-section>
                <q-item-section>{{ registration.user_affiliation }}</q-item-section>
              </q-item>
              <q-separator v-if="registration.user.profile.country" inset="item"></q-separator>
              <q-item v-if="registration.user.profile.country">
                <q-item-section avatar>
                  <country-flag :code="registration.user.profile.country.code"></country-flag>
                </q-item-section>
                <q-item-section>{{ registration.user.profile.country.name }}</q-item-section>
              </q-item>
              <q-separator v-if="registration.invoice_requested" inset="item"></q-separator>
              <q-item v-if="registration.invoice_requested">
                <q-item-section avatar><q-icon name="grading" :color="(registration.invoice_sent) ? 'positive' : 'orange-7'"></q-icon></q-item-section>
                <q-item-section v-if="registration.invoice_sent" class="text-positive text-bold">Invoice sent</q-item-section>
                <q-item-section v-else class="text-orange-7 text-bold">Invoice requested (not sent)</q-item-section>
              </q-item>
              <q-separator inset="item"></q-separator>
              <q-item v-if="registration.is_paid">
                <q-item-section avatar><q-icon name="done_outline" color="positive"></q-icon></q-item-section>
                <q-item-section class="text-positive text-bold">Paid</q-item-section>
              </q-item>
              <q-item v-else>
                <q-item-section avatar><q-icon name="radio_button_unchecked" color="orange-7"></q-icon></q-item-section>
                <q-item-section class="text-orange-7 text-bold">Pending payment</q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
          <q-card-section v-show="registration.custom_data.grant_requested">
          </q-card-section>
          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Close" color="grey" v-close-popup></q-btn>
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>
  `,
  computed: {
    registrations: function () {
      return this.data.map(function (obj) {
        obj.date = moment(obj.created_at);
        obj.country_code = obj.user.profile.institution.country.code || obj.custom_data.profile.country.code;
        obj.user_gender = obj.custom_data.profile.gender || {
          1: 'female',
          2: 'male',
          96: 'non_binary'
        }[obj.user.profile.gender_id] || null;
        obj.user_name = obj.user.profile.name;
        obj.user_affiliation = obj.user.profile.institution.name;
        return obj;
      });
    },
    registration: function () {
      if (this.data.length && this.uuid) {
        return _.findWhere(this.data, {uuid: this.uuid});
      } else return null;
    },
    showDialog: {
      get: function () {
        return this.registration != null;
      },
      set: function (val) {
        if (this.dialogVisible) {
          this.$router.replace({params: {uuid: undefined}});
          this.dialogVisible = false;
        }
      }
    }
  },
  methods: {
    disableToggle: function (row) {
      return this.grantsPerCountry
          && (this.grantsPerCountry[row.country_code].grants_assigned >= this.grantsPerCountry[row.country_code].grants)
          && this.mutableLists['granted'].indexOf(row.id) < 0;
    }
  },
  watch: {
    'mutableLists': {
      deep: true,
      handler: _.debounce(function (val, oldVal) {
        if (!_.isEqual(val['admitted'], this.admittedIds)) {
          this.$root.$emit('acaces-ids-updated', 'admitted_ids', val['admitted']);
        }
        if (!_.isEqual(val['granted'], this.grantedIds)) {
          this.$root.$emit('acaces-ids-updated', 'granted_ids', val['granted']);
        }
      }, 250)
    }
  },
  created: function () {
    if (this.admittedIds) {
      this.mutableLists['admitted'] = this.admittedIds;
    }
    if (this.grantedIds) {
      this.mutableLists['granted'] = this.grantedIds;
    }
  }
});


Vue.component('acaces-countries-table', {
  data: function () {
    return {
      columns: [
        {
          name: 'country_code',
          field: 'country_code',
        },
        {
          name: 'country_name',
          field: 'country_name',
          label: 'Country',
          sortable: true,
          align: 'left'
        },
        {
          name: 'grants',
          field: 'grants',
          label: 'Grants available',
          sortable: true,
          align: 'center'
        },
        {
          name: 'grants_requested',
          field: 'grants_requested',
          label: 'Grants requested',
          sortable: true,
          align: 'center'
        },
        {
          name: 'grants_assigned',
          field: 'grants_assigned',
          label: 'Grants assigned',
          sortable: true,
          align: 'center'
        },
        {
          name: 'registrations',
          field: 'registrations',
          label: 'Registrations',
          sortable: true,
          align: 'center'
        },
        {
          name: 'admitted',
          field: 'admitted',
          label: 'Admitted',
          sortable: true,
          align: 'center'
        }
      ],
      initialPagination: {
        rowsPerPage: 0,
        sortBy: 'registrations',
        descending: true
      }
    }
  },
  props: {
    grantsPerCountry: {
      type: Object,
      required: true
    },
    regRoute: {
      type: String,
      default: 'registrations'
    }
  },
  template: `
    <div>
      <q-table flat dense loading row-key="country_code" :data="countries" :columns="columns" :pagination="initialPagination">
        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td key="country_code" :props="props">
              <country-flag :code="props.row.country_code"></country-flag>
            </q-td>
            <q-td key="country_name" :props="props">{{ props.row.country_name }}</q-td>
            <q-td key="grants" :props="props">
              <q-icon name="indeterminate_check_box" size="xs" :color="(clickable(props.row.country_code)) ? 'grey-5' : 'grey-3'" class="q-mr-sm" @click="updateGrants(props.row.country_code, '-')" :class="{'cursor-pointer': clickable(props.row.country_code) }"></q-icon>
              <samp>{{ props.row.grants }}</samp>
              <q-icon name="add_box" size="xs" color="grey-5" class="q-ml-sm cursor-pointer" @click="updateGrants(props.row.country_code, '+')"></q-icon>
            </q-td>
            <q-td key="grants_requested" :props="props">
              <samp>{{ props.row.grants_requested }}</samp>
              <q-icon name="circle" size="10px" :color="(props.row.grants_requested > props.row.grants) ? 'orange' : 'green'" class="q-ml-xs"></q-icon>
            </q-td>
            <q-td key="grants_assigned" :props="props">
              <samp>{{ props.row.grants_assigned }}</samp>
              <q-icon name="circle" size="10px" :color="(props.row.grants_assigned < props.row.grants) ? 'orange' : 'green'" class="q-ml-xs"></q-icon>
            </q-td>
            <q-td key="registrations" :props="props">
              <samp>{{ props.row.registrations }}</samp>
              <router-link :to="{name: 'registrations', query: {q: props.row.country_name}}" class="q-ml-xs">
                <q-icon name="pageview" size="xs" color="grey-5"></q-icon>
              </router-link>
            </q-td>
            <q-td key="admitted" :props="props">
              <samp>{{ props.row.admitted }}</samp>
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </div>
  `,
  methods: {
    clickable: function (code) {
      return this.grantsPerCountry
          && _.has(this.grantsPerCountry, code)
          && this.grantsPerCountry[code].grants > this.grantsPerCountry[code].grants_assigned;
    },
    updateGrants: function (code, operator) {
      var g = _.clone(this.grantsPerCountry[code].grants);
      if (operator == '+') g++;
      else if (g == this.grantsPerCountry[code].grants_assigned) return
      else g--;

      this.$root.$emit('country-grants-updated', code, g);
    }
  },
  computed: {
    countries: function () {
      if (!this.grantsPerCountry) return [];
      return _.values(this.grantsPerCountry).map(function (obj) {
        obj.country_code = obj.country.code;
        obj.country_name = obj.country.name;
        return obj;
      }).sort(function (a, b) {
        return Hipeac.utils.sortText(a.country_name, b.country_name);
      });
    }
  }
});
