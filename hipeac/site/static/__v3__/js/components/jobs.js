var HipeacJobComponents = {

  'job-cards': {
    props: {
      items: {
        type: Array
      }
    },
    template: `
      <div v-if="items.length" class="row q-col-gutter-sm">
        <div v-for="item in items" class="col-12 col-sm-6 col-md-4 col-lg-3 d-flex align-items-stretch">
          <q-card class="hipeac__card block full-height" tag="a" :href="item.href">
            <q-card-section>
              <img v-if="item.institution.images" :src="item.institution.images.sm">
              <h6 class="title mb-auto">{{ item.title }}<br>
                <span class="text-light-weight">@ {{ item.institution.short_name }}</span>
              </h6>
              <q-list>
                <q-item v-if="item.internship" class="text-primary ">
                  <strong>Internship</strong>
                </q-item>
                <q-item>
                  <strong v-if="item.isNew" class="bg-new float-right">New</strong>
                  <span class="deadline">{{ item.deadline }}</span>
                </q-item>
                <q-item>

                  <span v-if="item.location">{{ item.location }}<span v-if="item.country">, </span></span>
                  <span v-if="item.country">{{ item.country.name }}</span>
                </q-item>
                <!--<q-item><icon name="how_to_reg" class="sm"></icon><metadata-join :items="item.career_levels"></metadata-join></q-item>
                <q-item v-if="item.topics.length"><icon name="label" class="sm"></icon><metadata-join :items="item.topics"></metadata-join></q-item>-->
              </q-list>
            </q-card-section>
          </q-card>
        </div>
      </div>
    `
  }

};
