Vue.component('hipeac-job-cards', {
  props: {
    items: {
      type: Array
    }
  },
  template: `
    <div v-if="items.length" class="row q-col-gutter-sm items-stretch">
      <div v-for="item in items" :key="item.id" class="col-12 col-sm-6 col-md-4 col-lg-3 pointer" @click="openURL(item.href)">
        <q-card class="hipeac__card column full-height">
          <q-card-section horizontal class="q-mt-xs q-mb-none q-px-sm">
            <q-card-section class="col-8 q-pb-none">
              <img v-if="item.institution.images" :src="item.institution.images.lg" class="jobs__logo">
            </q-card-section>
          </q-card-section>
          <q-card-section class="text-body2 q-px-lg">
            <p class="text-bold q-mb-xs">{{ item.title }}</p>
            <span class="text-caption">@ {{ item.institution.short_name }}</span>
          </q-card-section>
          <q-space></q-space>
          <q-card-section class="text-body2 q-px-lg">
            <ul class="list-unstyled text-secondary" :class="{soon: item.expiresSoon}">
              <li v-if="item.internship" class="text-primary "><icon name="info" class="sm"></icon>
                <strong>Internship</strong></li>
              <li>
                <strong v-if="item.isNew" class="bg-new float-right">New</strong>
                <icon name="today" class="sm"></icon>
                <span class="deadline">{{ item.deadline | moment }}</span>
              </li>
              <li>
                <icon name="location_on" class="sm"></icon>
                <span v-if="item.location">{{ item.location }}<span v-if="item.country">, </span></span>
                <span v-if="item.country">{{ item.country.name }}</span>
              </li>
              <li><icon name="how_to_reg" class="sm"></icon><metadata-join :items="item.career_levels"></metadata-join></li>
              <li v-if="item.topics.length"><icon name="label" class="sm"></icon><metadata-join :items="item.topics"></metadata-join></li>
            </ul>
          </q-card-section>
        </q-card>
      </div>
    </div>
  `,
  methods: {
    openURL: function (url) {
      return Quasar.utils.openURL(url);
    }
  }
});
