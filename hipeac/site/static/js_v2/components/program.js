Vue.component('hipeac-program', {
  data: function () {
    return {
      q: '',
      selectedDays: [],
      now: moment()
    }
  },
  props: {
    dates: {
      required: true,
      type: Array,
      default: function () {
        return [];
      }
    },
    breaks: {
      type: Array,
      default: function () {
        return [];
      }
    },
    courses: {
      type: Array,
      default: function () {
        return [];
      }
    },
    sessions: {
      type: Array,
      default: function () {
        return [];
      }
    },
    showSlots: {
      type: Boolean,
      default: false
    },
    searchPlaceholder: {
      type: String,
      default: 'Search by type, title, speakers, project, topics...'
    },
    compactDateFormat: {
      type: String,
      default: 'MMM D'
    }
  },
  template: `
    <div v-if="program">
      <q-card-section class="q-mx-sm">
        <hipeac-search-box :placeholder="searchPlaceholder" eventName="program-query-changed"></hipeac-search-box>
      </q-card-section>
      <q-card-actions class="q-mb-sm q-mx-sm text-body2">
        <q-checkbox v-for="(date, idx) in dates" :key="idx" v-model="selectedDays" :val="date.format('L')" :label="($q.screen.gt.sm) ? date.format('dddd, MMM D') : date.format(compactDateFormat)" class="q-mr-md"></q-checkbox>
        <q-space></q-space>
        <!--<q-btn v-if="$q.screen.gt.xs" flat no-caps @click="dialog = true" icon="filter_list" class="float-right" label="Filters"></q-btn>-->
      </q-card-actions>
      <q-separator></q-separator>
      <q-card-section v-for="(data, day) in program" :key="day" class="q-ma-sm">
        <h3 class="q-mb-lg">{{ data.date.format('dddd, MMM D') }}</h3>
        <div v-if="data.sessions" v-for="session in data.sessions" :key="session.id">
          <div v-if="session.session_type == 'break'" class="row bg-grey-1 text-body2">
            <div v-if="session.showTime" class="col-12 border-top"></div>
            <div class="col-2 q-py-lg q-pr-lg text-center">
              <q-icon size="sm" :name="session.icon" color="grey-7"></q-icon>
            </div>
            <div class="col-10 border-left q-py-lg q-pl-lg" :class="{'border-top': !session.showTime}">
              <ul class="row inline q-col-gutter-y-sm q-col-gutter-x-md q-mb-none text-caption text-grey-9">
                <li>
                  <q-icon size="xs" name="lens" color="grey-7" class="q-mr-xs"></q-icon>
                  <span>{{ session.title }}</span>
                </li>
                <li>
                  <q-icon size="xs" name="schedule" color="grey-7" class="q-mr-xs"></q-icon>
                  <span>{{ session.startAt.format('HH:mm') }} - {{ session.endAt.format('HH:mm') }}</span>
                </li>
              </ul>
            </div>
          </div>
          <div v-else class="row">
            <div v-if="session.showTime" class="col-12 border-top"></div>
            <div class="col-2 q-py-lg q-pr-lg text-center">
              <div v-show="session.showTime">
                <h4 v-if="$q.screen.gt.sm" class="text-h5">{{ session.startAt.format('h:mm') }} <small>{{ session.startAt.format('A') }}</small></h4>
                <span v-else>{{ session.startAt.format('h:mm') }} <small>{{ session.startAt.format('A') }}</small></span>
              </div>
            </div>
            <div class="col-10 border-left q-py-lg q-pl-lg col-pointer" :class="{'border-top': !session.showTime}" @click="$router.push({name: session.route, params: {id: session.id}})">
              <hipeac-avatar-item v-if="session.isKeynote && _.has(keynotesDict, session.id) && keynotesDict[session.id].main_speaker" :profile="keynotesDict[session.id].main_speaker.profile" class="q-px-none q-pt-none q-mb-sm"></hipeac-avatar-item>
              <display-3 class="q-mb-xs">{{ session.title }}</display-3>
              <ul class="row inline q-col-gutter-y-sm q-col-gutter-x-md q-mb-none text-caption text-grey-9">
                <li>
                  <q-icon size="xs" name="lens" :color="session.color" class="q-mr-xs"></q-icon>
                  <span v-if="showSlots && session.session_type.value == 'Course'">Slot {{ session.slot }}</span>
                  <span v-else>{{ session.session_type.value }}</span>
                </li>
                <li>
                  <q-icon size="xs" name="schedule" color="grey-7" class="q-mr-xs"></q-icon>
                  <span>{{ session.startAt.format('HH:mm') }} - {{ session.endAt.format('HH:mm') }}</span>
                </li>
                <!--<li v-if="sessionRegistered(session.id)">
                  <q-icon size="xs" name="check" color="green" class="q-mr-xs"></q-icon>
                  <span>Registered</span>
                </li>-->
              </ul>
            </div>
          </div>
        </div>
      </q-card-section>
    </div>
  `,
  computed: {
    sessionsList: function () {
      var output = [];

      if (this.breaks.length) {
        _.each(this.breaks, function (br) {
          output.push({
            key: 'b-' + br.id,
            id: br.id,
            title: br.notes,
            date: br.date,
            isoDay: br.isoDay,
            startAt: br.startAt,
            endAt: br.endAt,
            duration: br.duration,
            session_type: 'break',
            icon: br.icon,
            q: []
          });
        });
      }

      if (this.courses.length) {
        _.each(this.courses, function (course) {
          var i = 0;

          _.each(course.sessions, function (session) {
            i++;
            output.push({
              key: 'c-' + course.id + '-' + session.id,
              id: course.id,
              title: course.title + ' (#' + i + ')',
              date: session.date,
              isoDay: session.isoDay,
              startAt: session.startAt,
              endAt: session.endAt,
              duration: session.duration,
              topics: course.topics,
              route: 'course',
              session_type: session.session_type,
              color: course.color,
              slot: course.custom_data.slot || null,
              q: [
                course.title,
                session.session_type.value,
                session.keywords.join(' ')
              ].join(' ').toLowerCase()
            });
          });
        });
      }

      if (this.sessions.length) {
        _.each(this.sessions, function (session) {
          output.push({
            key: 's-' + session.id,
            id: session.id,
            title: session.title,
            date: session.date,
            isoDay: session.isoDay,
            startAt: session.startAt,
            endAt: session.endAt,
            duration: session.duration,
            teachersStr: '',
            topics: session.topics,
            route: 'session',
            session_type: session.session_type,
            color: session.color,
            q: session.q
          });
        });
      }

      if (!output.length) return [];

      output = output.sort(function (a, b) {
        return a.startAt - b.startAt;
      });

      return output;
    },
    filteredSessions: function () {
      if (!this.sessionsList.length) return null;

      var days = this.selectedDays;
      var filtered = this.sessionsList.filter(function (obj) {
        return _.contains(days, obj.startAt.format('L'));
      });

      if (this.q) {
        filtered = Hipeac.utils.filterMultiple(filtered, this.q);
      }

      // Add a showDate helper

      var day = null;
      var time = null;

      _.each(filtered, function (obj) {
        sDay = obj.startAt.format('YYYY-MM-DD');
        sTime = obj.startAt.format('LT');
        obj.showTime = (time != sTime || day != sDay);
        time = sTime;
        day = sDay;
      });

      return filtered;
    },
    program: function () {
      if (!this.sessionsList.length) return null;

      var days = _.uniq(this.filteredSessions.map(function (obj) {
        return obj.isoDay;
      }));
      var sessionsMap = _.groupBy(this.filteredSessions, 'isoDay');
      var program = days.map(function (day) {
        return {
          day: day,
          date: moment(day),
          sessions: sessionsMap[day]
        };
      });
      return _.indexBy(program, 'day');
    }
  },
  methods: {
    updateDays: function () {
      var self = this;
      var selectedDays = _.clone(this.dates.filter(function (obj) {
        return obj.dayOfYear() >= self.now.dayOfYear();
      })).map(function (date) {
        return date.format('L');
      });

      this.selectedDays = (selectedDays.length)
        ? selectedDays
        : _.clone(this.dates).map(function (date) {
          return date.format('L');
        });
    },
    updateQuery: function (val) {
      this.q = val;
    }
  },
  created: function () {
    this.updateDays();
    this.$root.$on('program-query-changed', this.updateQuery);
  },
  beforeDestroy () {
    this.$root.$off('program-query-changed');
  }
});
