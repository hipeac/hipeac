var HipeacEventComponents = {

  'hipeac-program-card': {
    data: function () {
      return {
        q: '',
        now: moment()
      };
    },
    props: {
      event: {
        required: true,
        type: Object
      },
      keynotes: {
        type: Array,
        default: function () {
          return [];
        }
      },
      showSlots: {
        type: Boolean,
        default: false
      }
    },
    template: `
      <q-card>
        <hipeac-search-bar v-model="q" placeholder="Search by title, speakers, project, topics..." :filters="filters"></hipeac-search-bar>
        <hipeac-no-data v-if="!filteredSessions.length" :filter="q" message="No matching sessions found"></hipeac-no-data>
        <div v-else>
          <q-card-section v-for="(data, day) in program" :key="day" :class="{'q-pa-md': $q.screen.gt.xs}">
            <h3 class="q-mb-lg">{{ data.date.format('dddd, MMM D') }}</h3>
            <div v-if="data.sessions" v-for="session in data.sessions" :key="session.id">
              <div v-if="session.session_type == 'break'" class="row bg-grey-1 text-body2">
                <div v-if="session.show_time" class="col-12 border-top"></div>
                <div class="col-2 q-py-md q-px-xs text-center">
                  <q-icon size="sm" :name="session.icon" color="grey-7"></q-icon>
                </div>
                <div class="col-10 border-left q-py-md q-pl-lg" :class="{'border-top': !session.show_time}">
                  <ul class="row inline q-col-gutter-y-sm q-col-gutter-x-md q-mb-none text-caption text-grey-9">
                    <li>
                      <q-icon size="xs" name="lens" color="grey-7" class="q-mr-xs"></q-icon>
                      <span>{{ session.title }}</span>
                    </li>
                    <li>
                      <q-icon size="xs" name="schedule" color="grey-7" class="q-mr-xs"></q-icon>
                      <span>{{ session.start.format('H:mm') }} - {{ session.end.format('H:mm') }}</span>
                    </li>
                  </ul>
                </div>
              </div>
              <div v-else class="row">
                <div v-if="session.show_time" class="col-12 border-top"></div>
                <div class="col-2 q-py-md q-px-sm text-center">
                  <div v-show="session.show_time">
                    <h4 v-if="$q.screen.gt.sm" class="text-h5 text-weight-light">{{ session.start.format('H:mm') }}</h4>
                    <small v-else class="text-subtitle2">{{ session.start.format('H:mm') }}</small>
                  </div>
                </div>
                <div class="col-10 border-left q-py-md q-pl-lg col-pointer" :class="{'border-top': !session.show_time}" @click="$router.push({name: session.route, params: {id: session.id}})">
                  <hipeac-profile-item v-if="keynotesDict[session.id] && keynotesDict[session.id].main_speaker" :profile="keynotesDict[session.id].main_speaker.profile" class="q-px-none q-pt-none q-mb-sm"></hipeac-profile-item>
                  <display-3 class="q-mb-xs">{{ session.title }}</display-3>
                  <ul class="row inline q-col-gutter-y-sm q-col-gutter-x-md q-mb-none text-caption text-grey-9">
                    <li>
                      <q-icon size="xs" name="lens" :color="session.color" class="q-mr-xs"></q-icon>
                      <span v-if="showSlots && session.session_type.value == 'Course'">Slot {{ session.slot }}</span>
                      <span v-else>{{ session.session_type.value }}</span>
                    </li>
                    <li v-if="session.room">
                      <q-icon size="xs" name="room" color="grey-7" class="q-mr-xs"></q-icon>
                      <span>{{ session.room.name }}</span>
                    </li>
                    <li>
                      <q-icon size="xs" name="schedule" color="grey-7" class="q-mr-xs"></q-icon>
                      <span>{{ session.start.format('H:mm') }} - {{ session.end.format('H:mm') }}</span>
                    </li>
                    <li v-if="session.track">
                      <q-icon size="xs" name="label_important" :color="session.track.color" class="q-mr-xs"></q-icon>
                      <span>{{ session.track.name }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </q-card-section>
        </div>
      </q-card>
    `,
    computed: {
      filters: function () {
        var f = [];
        var out = {};

        _.each(this.sessions, function (s) {
          f.push(s._q.split(' ').filter(function (word) {
            return word.indexOf(':') > -1;
          }));
        });

        _.each(_.uniq(_.flatten(f)), function (word) {
          var s = word.split(':');
          if (s[1] != '') {
            if (!_.has(out, s[0])) out[s[0]] = [s[1]];
            else out[s[0]].push(s[1]);
          }
        });

        return _.map(out, function (options, name) {
          return {
            name: name,
            options: options
          };
        });
      },
      keynotesDict: function () {
        if (!this.keynotes.length) return {};
        return _.indexBy(this.keynotes, 'id');
      },
      sessions: function () {
        var output = [];
        var rooms = {};

        _.each(this.event.venues, function (venue) {
          _.each(venue.rooms, function (room) {
            rooms[room.id] = room;
          });
        });

        if (this.event.breaks.length) {
          _.each(this.event.breaks, function (br) {
            output.push({
              key: 'b-' + br.id,
              id: br.id,
              title: br.notes,
              date: br.date,
              isoDay: br.start.format('YYYY-MM-DD'),
              start: br.start,
              end: br.end,
              duration: br.duration,
              session_type: 'break',
              room: null,
              icon: br.icon,
              _q: ''
            });
          });
        }

        if (this.event.sessions.length) {
          _.each(this.event.sessions, function (session) {
            output.push({
              key: 's-' + session.id,
              id: session.id,
              title: session.title,
              date: session.date,
              isoDay: session.start.format('YYYY-MM-DD'),
              start: session.start,
              end: session.end,
              duration: session.duration,
              teachersStr: '',
              topics: session.topics,
              route: 'session',
              session_type: session.session_type,
              room: rooms[session.room] || null,
              color: session.color,
              _q: session._q
            });
          });
        }

        if (!output.length) return [];

        output = output.sort(function (a, b) {
          return a.start - b.start;
        });

        return output;
      },
      filteredSessions: function () {
        if (!this.sessions.length) return null;
        var filtered = this.sessions;

        if (this.q) {
          filtered = Hipeac.utils.filter(filtered, this.q);
        }

        // Add a show_time helper

        var day = null;
        var time = null;

        _.each(filtered, function (obj) {
          s_day = obj.start.format('YYYY-MM-DD');
          s_time = obj.start.format('LT');
          obj.show_time = (time != s_time || day != s_day);
          if (obj.session_type != 'break') {
            time = s_time;
            day = s_day;
          }
        });

        return filtered;
      },
      program: function () {
        if (!this.sessions.length) return null;

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
    watch: {
      q: function (val, oldVal) {
        if (val == '') this.$router.replace({query: {q: undefined}});
        else if (val != this.$route.query.q && val != oldVal) this.$router.replace({query: {q: val}});
      }
    },
    created: function () {
      if (this.$route.query.q) {
        this.q = this.$route.query.q;
      }
    }
  },

  'hipeac-session-breaks': {
    props: {
      breaks: {
        type: Array,
        default: function () {
          return [];
        }
      },
      session: {
        required: true,
        type: Object
      }
    },
    template: `
      <div v-if="!!breaks_in_session.length">
        <display-5>Breaks</display-5>
        <q-list separator class="text-grey-7">
          <q-item dense v-for="br in breaks_in_session" :key="br.id" class="q-pa-xs">
            <q-item-section avatar>
              <q-icon size="xs" :name="br.icon"></q-icon>
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-body2">{{ br.notes }}</q-item-label>
            </q-item-section>
            <q-item-section side center>
              <q-item-label caption>{{ br.start.format('HH:mm') }} - {{ br.end.format('HH:mm') }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </div>
    `,
    computed: {
      breaks_in_session: function () {
        var output = [];
        var s = this.session;

        _.each(this.breaks, function (br) {
          if (br.start.isBetween(s.start, s.end)) {
            output.push(br);
          }
        });

        return output;
      }
    }
  },

  'hipeac-metadata': {
    props: {
      metadata: {
        type: Array,
        default: function () {
          return [];
        }
      },
      title: {
        type: String,
        default: 'Metadata'
      },
      badgeColor: {
        type: String,
        default: 'primary'
      }
    },
    template: `
      <div v-if="metadata.length">
        <display-5 style="margin:0">{{ title }}</display-5>
        <div class="q-gutter-x-sm q-mt-sm">
          <q-badge v-for="item in metadata" :label="item.value" :color="badgeColor" />
        </div>
      </div>
    `
  },

  'hipeac-session-application-areas': {
    props: {
      session: {
        type: Object,
        required: true
      }
    },
    template: '<hipeac-metadata :metadata="session.application_areas" title="Application areas" badge-color="blue-5"></hipeac-metadata>'
  },

  'hipeac-session-topics': {
    props: {
      session: {
        type: Object,
        required: true
      }
    },
    template: '<hipeac-metadata :metadata="session.topics" title="Topics"></hipeac-metadata>'
  }

};
