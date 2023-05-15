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
          name: 'places',
          field: 'places',
          label: 'Places available',
          sortable: true,
          align: 'center'
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
      <q-table flat dense row-key="country_code" :data="countries" :columns="columns" :pagination="initialPagination">
        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td key="country_code" :props="props">
              <country-flag :code="props.row.country_code"></country-flag>
            </q-td>
            <q-td key="country_name" :props="props">{{ props.row.country_name }}</q-td>
            <q-td key="places" :props="props">
              <q-icon name="indeterminate_check_box" size="xs" :color="(clickablePlaces(props.row.country_code)) ? 'grey-5' : 'grey-3'" class="q-mr-sm" @click="updatePlaces(props.row.country_code, '-')" :class="{'cursor-pointer': clickablePlaces(props.row.country_code) }"></q-icon>
              <samp>{{ props.row.places }}</samp>
              <q-icon name="add_box" size="xs" color="grey-5" class="q-ml-sm cursor-pointer" @click="updatePlaces(props.row.country_code, '+')"></q-icon>
            </q-td>
            <q-td key="grants" :props="props">
              <q-icon name="indeterminate_check_box" size="xs" :color="(clickableGrants(props.row.country_code)) ? 'grey-5' : 'grey-3'" class="q-mr-sm" @click="updateGrants(props.row.country_code, '-')" :class="{'cursor-pointer': clickableGrants(props.row.country_code) }"></q-icon>
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
              <router-link :to="{name: 'registrations', query: {q: 'country:' + props.row.key}}" class="q-ml-xs">
                <q-icon name="pageview" size="xs" color="grey-5"></q-icon>
              </router-link>
            </q-td>
            <q-td key="admitted" :props="props">
              <samp>{{ props.row.admitted }}</samp>
              <q-icon name="circle" size="10px" :color="(props.row.admitted < props.row.places) ? 'orange' : 'green'" class="q-ml-xs"></q-icon>
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </div>
  `,
  methods: {
    clickablePlaces: function (code) {
      return this.grantsPerCountry
          && _.has(this.grantsPerCountry, code)
          && this.grantsPerCountry[code].places > this.grantsPerCountry[code].admitted;
    },
    clickableGrants: function (code) {
      return this.grantsPerCountry
          && _.has(this.grantsPerCountry, code)
          && this.grantsPerCountry[code].grants > this.grantsPerCountry[code].grants_assigned;
    },
    updateGrants: function (code, operator) {
      var g = _.clone(this.grantsPerCountry[code].grants);
      if (operator == '+') g++;
      else if (g == this.grantsPerCountry[code].grants_assigned) return
      else g--;

      this.$root.$emit('country-grants-updated', this.grantsPerCountry[code].self, g);
    },
    updatePlaces: function (code, operator) {
      var g = _.clone(this.grantsPerCountry[code].places);
      if (operator == '+') g++;
      else if (g == this.grantsPerCountry[code].admitted) return
      else g--;

      this.$root.$emit('country-places-updated', this.grantsPerCountry[code].self, g);
    }
  },
  computed: {
    countries: function () {
      if (!this.grantsPerCountry) return [];
      return _.values(this.grantsPerCountry).map(function (obj) {
        obj.country_code = obj.country.code;
        obj.country_name = obj.country.name;
        obj.key = slugify(obj.country.name).toLowerCase();
        return obj;
      }).sort(function (a, b) {
        return Hipeac.utils.sortText(a.country_name, b.country_name);
      });
    }
  }
});

Vue.component('acaces-grant-stats-card', {
  props: {
    data: {
      type: Object
    },
    title: {
      type: String,
      default: 'Grant overview'
    },
    showTotals: {
      type: Boolean,
      default: true
    }
  },
  template: `
    <q-card v-if="data" class="hipeac__card">
      <div :class="{'q-pa-sm': $q.screen.gt.xs }">
        <q-card-section>
          <display-4>{{ title }}</display-4>
        </q-card-section>
        <q-list class="text-body2 q-mb-md">
          <q-item v-if="showTotals" class="q-py-xs">
            <q-item-section avatar>
              <stats-progress :value="100" color="primary">{{ data.registrations }}</stats-progress>
            </q-item-section>
            <q-item-section><strong>Registrations</strong></q-item-section>
          </q-item>
          <q-item class="q-py-xs">
            <q-item-section avatar>
              <stats-progress :value="(data.places_available / data.registrations) * 100" color="green">{{ data.places_available }}</stats-progress>
            </q-item-section>
            <q-item-section>Available places</q-item-section>
          </q-item>
          <q-item class="q-py-xs">
            <q-item-section avatar>
              <stats-progress :value="(data.admitted / data.places_available) * 100" color="green">{{ data.admitted }}</stats-progress>
            </q-item-section>
            <q-item-section>Admitted applicants</q-item-section>
            <q-item-section side>
              <router-link :to="{name: 'registrations', query: {q: 'admitted:yes'}}" class="q-ml-xs">
                <q-icon name="pageview" size="xs" color="grey-5"></q-icon>
              </router-link>
            </q-item-section>
          </q-item>
          <q-item class="q-py-xs">
            <q-item-section avatar>
              <stats-progress :value="(data.grants_requested / data.registrations) * 100" color="blue">{{ data.grants_requested }}</stats-progress>
            </q-item-section>
            <q-item-section>Grants requested</q-item-section>
            <q-item-section side>
              <router-link :to="{name: 'registrations', query: {q: 'grant.requested:yes'}}" class="q-ml-xs">
                <q-icon name="pageview" size="xs" color="grey-5"></q-icon>
              </router-link>
            </q-item-section>
          </q-item>
          <q-item class="q-py-xs">
            <q-item-section avatar>
              <stats-progress :value="(data.grants_available / data.registrations) * 100" :color="(data.grants_available < data.grants_requested) ? 'orange' : 'green'">{{ data.grants_available }}</stats-progress>
            </q-item-section>
            <q-item-section>Grants available</q-item-section>
          </q-item>
          <q-item class="q-py-xs">
            <q-item-section avatar>
              <stats-progress :value="(data.grants_assigned / data.registrations) * 100" :color="(data.grants_assigned < data.grants_available) ? 'orange' : 'green'">{{ data.grants_assigned }}</stats-progress>
            </q-item-section>
            <q-item-section>Grants assigned</q-item-section>
            <q-item-section side>
              <router-link :to="{name: 'registrations', query: {q: 'grant.assigned:yes'}}" class="q-ml-xs">
                <q-icon name="pageview" size="xs" color="grey-5"></q-icon>
              </router-link>
            </q-item-section>
          </q-item>
        </q-list>
      </div>
      <slot></slot>
    </q-card>
  `
});
