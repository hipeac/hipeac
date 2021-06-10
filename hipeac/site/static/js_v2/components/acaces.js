Vue.component('acaces-registrations-table', {
  data: function () {
    return {
      togglePlaceholder: false,
      dialogVisible: false,
      mutableGrantedIds: [],
      columns: [
        {
          name: 'id',
          field: 'id',
          sortable: true,
          label: 'ID',
          align: 'left',
        },
        {
          name: 'grant',
          field: 'has_grant',
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
      pagination: {
        rowsPerPage: 0
      }
    }
  },
  props: {
    data: {
      type: Array,
      required: true
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
      <q-table flat dense row-key="uuid" :data="registrations" :columns="columns" :pagination.sync="pagination">
        <template v-slot:body="props">
          <q-tr :props="props" class="cursor-pointer" @click="$router.replace({params: {uuid: props.row.uuid}})" :class="{'bg-orange-1': props.row.uuid == uuid}">
            <q-td key="id" :props="props"><samp><small>{{ props.row.id }}</small></samp></q-td>
            <q-td key="grant" :props="props">
              <q-toggle v-if="props.row.custom_data.grant_requested" size="xs" v-model="mutableGrantedIds" :val="props.row.id" color="green" :disable="disableToggle(props.row)" checked-icon="check" :unchecked-icon="(disableToggle(props.row)) ? null : 'arrow_forward_ios'" />
              <q-toggle v-else size="xs" v-model="togglePlaceholder" :val="false" color="green" disable class="transparent" unchecked-icon="remove" />
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
          <q-card-section v-show="registration.custom_data.grant_requested" >
            <q-toggle size="xs" v-model="mutableGrantedIds" :val="registration.id" color="green" />
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
      var grantedIds = this.grantedIds;
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
        obj.has_grant = _.has(grantedIds, obj.id);
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
          && this.mutableGrantedIds.indexOf(row.id) < 0;
    }
  },
  watch: {
    'mutableGrantedIds': _.debounce(function (val, oldVal) {
      if (val != this.grantedIds) {
        this.$root.$emit('granted-ids-updated', val);
      }
    }, 250)
  },
  created: function () {
    if (this.grantedIds) {
      this.mutableGrantedIds = this.grantedIds;
    }
  }
});
