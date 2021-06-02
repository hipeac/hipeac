Vue.component('hipeac-program-section', {
  props: {
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
    }
  },
  template: `
    <div v-if="program">
      <q-card-section v-for="(data, day) in program" :key="day" class="q-ma-sm">
        <h3 class="q-mb-lg">{{ data.date.format('dddd, MMM D') }}</h3>
        <div v-if="data.sessions" v-for="session in data.sessions" :key="session.id" class="row">
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
                <span>{{ session.session_type.value }}</span>
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
      </q-card-section>
    </div>
  `,
  computed: {
    sessionsList: function () {
      var output = [];

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
              teachersStr: course.teachersStr,
              topics: course.topics,
              route: 'course',
              session_type: session.session_type,
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
            q: session.q
          });
        });
      }

      if (!output.length) return [];

      var day = null;
      var time = null;
      var sTime = null;

      _.each(output, function (obj) {
        sDay = obj.startAt.format('YYYY-MM-DD');
        sTime = obj.startAt.format('LT');
        obj.showTime = (time != sTime || day != sDay);
        time = sTime;
        day = sDay;
      });

      return output;
    },
    program: function () {
      if (!this.sessionsList.length) return null;

      var days = _.uniq(this.sessionsList.map(function (obj) {
        return obj.isoDay;
      }));
      var sessionsMap = _.groupBy(this.sessionsList, 'isoDay');
      var program = days.map(function (day) {
        return {
          day: day,
          date: moment(day),
          sessions: sessionsMap[day]
        };
      });
      return _.indexBy(program, 'day');
    }
  }
});
