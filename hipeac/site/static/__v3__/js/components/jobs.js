var HipeacJobComponents = {

  'job-card-section': {
    props: {
      item: {
        type: Object,
        required: true
      },
      favourites: {
        type: Array,
        default: function () {
          return [];
        }
      }
    },
    template: `
      <template v-if="item">
        <q-card-section class="q-pa-none">
          <q-icon v-if="starred" name="hotel_class" class="float-right" color="positive" size="24px" />
          <img v-if="item.institution.images" :src="item.institution.images.lg" class="jobs__logo">
          <h5 class="q-my-lg text-body2">{{ item.title }}<br>
            <span class="text-weight-light">@ {{ item.institution.short_name }}</span>
          </h5>
        </q-card-section>
        <q-space />
        <q-card-section class="q-pa-none q-mt-lg text-caption text-grey-8">
          <q-separator />
          <q-list class="q-mt-md">
            <q-item v-if="item.internship" class="q-pa-none text-primary" style="min-height: 1.25rem;">
              <q-item-section avatar style="min-width: 30px;">
                <q-icon color="primary" name="today" size="1rem" />
              </q-item-section>
              <q-item-section>Internship</q-item-section>
            </q-item>
            <q-item class="q-pa-none" style="min-height: 1.25rem;">
              <q-item-section avatar style="min-width: 30px;">
                <q-icon name="today" size="1rem" />
              </q-item-section>
              <q-item-section>{{ item.deadline }}</q-item-section>
              <q-item-section side v-if="item.isNew">
                <q-badge color="teal" label="New" />
              </q-item-section>
            </q-item>
            <q-item class="q-pa-none" style="min-height: 1.25rem;">
              <q-item-section avatar style="min-width: 30px;">
                <q-icon name="place" size="1rem" />
              </q-item-section>
              <q-item-section>
                {{ item.location }}, {{ item.country.name }}
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </template>
    `,
    computed: {
      starred: function () {
        return _.contains(this.favourites, this.item.id);
      }
    }
  },

  'job-cards': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        dialog: false,
        dialogItem: null,
        stack: []
      }
    },
    props: {
      items: {
        type: Array,
        required: true
      },
      popup: {
        type: Boolean,
        default: false
      },
      manageStack: {
        type: Boolean,
        default: false
      },
      modelValue: {
        type: Array
      }
    },
    template: `
      <div>
        <div v-if="items.length" class="row q-col-gutter-sm">
          <div v-for="item in items" class="col-12 col-sm-6 col-md-4 col-lg-3 d-flex align-items-stretch">
            <q-card v-if="!popup" class="hipeac__card column full-height flat" tag="a" :href="item.href" target="jobs">
              <job-card-section :item="item" :favourites="(manageStack) ? stack : []" />
            </q-card>
            <q-card v-else class="hipeac__card column full-height cursor-pointer" @click="showItem(item)" tag="div">
              <job-card-section :item="item" :favourites="(manageStack) ? stack : []" />
            </q-card>
          </div>
        </div>
        <q-dialog v-if="popup" v-model="dialog">
          <q-layout view="hHh lpR fff" container class="bg-white" style="width: 1000px; max-width: 100vw;">
            <q-header class="bg-white">
              <q-toolbar class="text-dark bg-grey-2">
                <div v-if="manageStack">
                  <q-btn v-if="itemInStack" @click="removeFromStack(dialogItem.id)" unelevated size="sm" icon="star" label="In your applications" color="positive" class="q-pl-sm" />
                  <q-btn v-else @click="addToStack(dialogItem.id)" unelevated size="sm" icon="star_border" label="Apply for this position" color="grey" class="q-pl-sm" />
                </div>
                <q-space />
                <q-btn flat round v-close-popup icon="close" />
              </q-toolbar>
            </q-header>
            <q-page-container>
              <q-page class="q-pa-md" :class="{'q-pa-sm': $q.screen.gt.sm}">
                <div class="row q-col-gutter-xl">
                  <div class="col-12 col-md-8">
                    <h1 class="q-mt-none q-mb-lg text-weight-light">{{ dialogItem.title }}</h1>
                    <marked v-if="dialogItem.description" :text="dialogItem.description" />
                  </div>
                  <div class="col-12 col-md-4">
                    <img v-if="dialogItem.institution.images" :src="dialogItem.institution.images.lg" class="sponsor">
                    <hipeac-metadata :metadata="dialogItem.topics" title="Topics" />
                    <hipeac-metadata :metadata="dialogItem.application_areas" title="Topics" />
                  </div>
                </div>
              </q-page>
            </q-page-container>
          </q-layout>
        </q-dialog>
      </div>
    `,
    computed: {
      itemInStack: function () {
        var stack = this.stack || [];
        return _.contains(stack, this.dialogItem.id || 0);
      }
    },
    methods: {
      getJob: function (item) {
        Hipeac.api.request('get', item.self).then(function (response) {
          this.dialogItem = response.data;
        }.bind(this));
      },
      showItem: function (item) {
        this.dialog = true;
        this.dialogItem = item;
        this.getJob(item);
      },
      addToStack: function (id) {
        var stack = this.stack.slice() || [];
        stack.push(id);
        this.stack = stack;
      },
      removeFromStack: function (id) {
        this.stack = _.without(this.stack, id);
      }
    },
    watch: {
      dialog: function (val) {
        if (val === false) {
          this.dialogItem = null;
        }
      },
      stack: function (val) {
        this.$emit('update:modelValue', val);
      }
    },
    created: function () {
      this.stack = this.modelValue;
    }
  }

};
