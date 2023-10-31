<template>
  <div class="row q-col-gutter-xl">
    <div class="col-12 col-lg">
      <h3 v-html="overviewText" class="q-mb-lg text-weight-light"></h3>
      <h6>Institution types</h6>
      <div class="q-gutter-x-sm q-gutter-y-xs q-mb-md">
        <q-checkbox
          v-for="institutionType in institutionTypeOptions"
          v-model="filters.institutionTypes"
          :key="institutionType.value"
          :val="institutionType.value"
          :label="institutionType.label"
          dense
          size="xs"
        />
      </div>
      <h6 v-if="countryOptions.length">Countries</h6>
      <div class="q-gutter-x-sm q-gutter-y-xs">
        <q-checkbox
          v-for="country in countryOptions"
          v-model="filters.countries"
          :key="country.code"
          :val="country.code"
          :label="country.name"
          dense
          size="xs"
        />
      </div>
    </div>
    <div class="col-12 col-lg">
      <q-markup-table flat :dense="$q.screen.gt.sm">
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>
              {{ user.profile.name
              }}<span v-if="user.profile.institution"
                >, <small>{{ user.profile.institution.short_name }}</small></span
              >
              <small v-if="user.profile.second_institution"> / {{ user.profile.second_institution.short_name }}</small>
            </td>
            <td v-if="showContactForm" @click="contactUser(user)" class="min-width pointer">
              <q-icon name="forward_to_inbox" />
            </td>
            <td class="min-width">
              <a v-if="user.href" :href="user.href" target="_blank">
                <q-icon name="north_east" />
              </a>
            </td>
          </tr>
        </tbody>
      </q-markup-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';

import { api } from '@/axios';

const props = defineProps<{
  session: HipeacSession;
  showContactForm?: boolean;
}>();

const attendees = ref<HipeacEventAttendee[]>([]);
const institutionTypes = {
  university: 'University',
  lab: 'Government Lab',
  innovation: 'Innovation Center',
  industry: 'Industry',
  sme: 'SME',
  other: 'Other',
};
const filters = ref<{
  institutionTypes: string[];
  countries: string[];
}>({
  institutionTypes: [],
  countries: [],
});

const filteredUsers = computed<User[]>(() => {
  return attendees.value
    .map((attendee) => attendee.user)
    .filter((user) => {
      if (filters.value.institutionTypes.length) {
        if (!user.profile.institution) {
          return false;
        }
        if (!filters.value.institutionTypes.includes(user.profile.institution.type)) {
          return false;
        }
      }
      if (filters.value.countries.length) {
        if (!user.profile.institution) {
          return false;
        }
        if (!filters.value.countries.includes(user.profile.institution.country?.code || '')) {
          return false;
        }
      }
      return true;
    });
});

const countryOptions = computed<Country[]>(() => {
  return attendees.value
    .map((attendee) => attendee.user.profile.institution?.country || null)
    .filter((country, index, self) => {
      return country !== null && self.findIndex((c) => c?.code === country?.code) === index;
    })
    .sort((a, b) => {
      return (a as Country).name.localeCompare((b as Country).name);
    });
});

const institutionTypeOptions = computed<QuasarOption[]>(() => {
  return attendees.value
    .map((attendee) =>
      attendee.user.profile.institution
        ? {
            value: attendee.user.profile.institution.type,
            label: institutionTypes[attendee.user.profile.institution.type],
          }
        : null
    )
    .filter((type, index, self) => {
      return type !== null && self.findIndex((t) => t?.value === type?.value) === index;
    });
});

const overviewText = computed<string>(() => {
  const countries = new Set<string>();
  const institutions = new Set<string>();

  filteredUsers.value.forEach((user) => {
    if (user.profile.institution) {
      countries.add(user.profile.institution.country?.name || '');
      institutions.add(user.profile.institution.short_name);
    }
  });

  const countryCount = countries.size;
  const institutionCount = institutions.size;
  const attendeeCount = filteredUsers.value.length;
  const attendees =
    attendeeCount === 1 ? '<strong>One attendee</strong>' : `<strong>${attendeeCount} attendees</strong>`;

  if (attendeeCount === 0) {
    return 'No attendees found.';
  }

  if (countryCount === 1 && institutionCount === 1) {
    return `${attendees} from ${institutions.values().next().value}, <span class="text-no-wrap">${
      countries.values().next().value
    }</span>.`;
  } else if (countryCount === 1) {
    return `${attendees} from <span class="text-no-wrap">${institutionCount} institutions</span> in ${
      countries.values().next().value
    }.`;
  } else {
    return `${attendees} from <span class="text-no-wrap">${institutionCount} institutions</span> in <span class="text-no-wrap">${countryCount} countries</span>.`;
  }
});

function fetchAttendees() {
  api.get(props.session.rel_attendees).then((res) => {
    attendees.value = res.data;
  });
}

function clearFilters() {
  filters.value = {
    institutionTypes: [],
    countries: [],
  };
}

function contactUser(user: User) {
  alert(user.id);
}

onMounted(() => {
  fetchAttendees();
});
</script>
