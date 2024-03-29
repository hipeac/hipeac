var CommonMarkReader = new commonmark.Parser({safe: true, smart: true});
var CommonMarkWriter = new commonmark.HtmlRenderer();


var HipeacCommonComponents = {

  'django-form-error': {
    props: {
      field: {
        type: String,
        default: null
      },
      error: {
        type: String,
        required: true
      }
    },
    template: '<em class="hidden"></em>',
    created: function () {
      Quasar.Notify.create({
        timeout: 10000,
        progress: true,
        html: true,
        message: (this.field)
          ? '<strong>' + this.field + '</strong>: ' + this.error
          : this.error,
        type: 'negative',
        actions: [
          { label: 'Dismiss', color: 'white', handler: function () {} }
        ],
        attrs: {
          role: 'alert'
        }
      });
    }
  },

  'django-message': {
    props: {
      message: {
        type: String
      },
      level: {
        type: String
      },
      tags: {
        type: String
      }
    },
    template: '<em class="hidden"></em>',
    created: function () {
      /*
      DEBUG = 10
      INFO = 20
      SUCCESS = 25
      WARNING = 30
      ERROR = 40
      */
      var level = +this.level;
      Quasar.Notify.create({
        timeout: (level > 25) ? 10000 : 5000,
        message: this.message,
        type: {
          10: 'info',
          20: 'info',
          25: 'positive',
          30: 'warning',
          40: 'negative'
        }[level] || 'info',
        actions: [
          {
            label: 'Dismiss',
            color: (level == 30) ? 'dark' : 'white',
            handler: function () {}
          }
        ],
        attrs: {
          role: 'alert'
        }
      });
    }
  },

  'country-flag': {
    props: {
      code: {
        type: String
      }
    },
    template: '<i :class="css"></i>',
    computed: {
      css: function () {
        if (!this.code) return '';
        return [
          "flag-sprite",
          "flag-" + this.code[0],
          "flag-_" + this.code[1],
        ].join(' ').toLowerCase()
      }
    }
  },

  'display-lg': {
    template: '<h2 class="display display-lg"><span><slot></slot></span></h2>'
  },

  'display-2': {
    template: '<h3 class="q-mt-none q-mb-sm text-h5 text-weight-light"><slot></slot></h3>'
  },

  'display-3': {
    template: '<h4 class="q-mt-none q-mb-sm text-weight-regular"><slot></slot></h4>'
  },

  'display-4': {
    template: '<h5 class="q-mt-none q-mb-sm text-weight-regular"><slot></slot></h5>'
  },

  'display-5': {
    props: {
      dense: {
        type: Boolean,
        default: false
      }
    },
    template: `
      <h6 class="q-my-none text-weight-bold text-dark" :class="{'q-mb-md': !dense}"><slot></slot></h6>
    `
  },

  'download-btn': {
    props: {
      href: {
        type: String,
        required: true
      },
      title: {
        type: String,
        default: 'Download'
      }
    },
    template: `
      <q-btn type="a" :href="href" class="full-width" color="primary">
        <q-icon name="download" size="xs" class="q-mr-sm" />{{ title }}</q-btn>
    `
  },

  'form-section-title': {
    template: `
      <q-banner rounded class="bg-blue-grey-1 q-mb-sm text-right text-dark">
        <strong><slot></slot></strong>
      </q-banner>
    `
  },

  'marked': {
    props: {
      text: {
        type: String,
        default: ''
      }
    },
    template: '<div class="marked" v-html="compiledText"></div>',
    computed: {
      compiledText: function () {
        if (!this.text || this.text == '') return this.text;
        return CommonMarkWriter.render(CommonMarkReader.parse(this.text));
      }
    }
  },

  'hipeac-side-menu': {
    props: {
      collapse: {
        type: Boolean,
        default: false
      },
      label: {
        type: String,
        default: 'Menu'
      }
    },
    template: `
      <div class="text-body2">
        <q-expansion-item
          v-if="collapse"
          dense
          switch-toggle-side
          expand-separator
          :label="label"
        >
          <q-menu>
            <slot></slot>
          </q-menu>
        </q-expansion-item>
        <slot v-else></slot>
      </div>
    `
  },

  'hipeac-toolbar-menu': {
    data: function () {
      return {
        menu: HIPEAC_MENU
      };
    },
    template: `
      <q-btn-group stretch flat v-show="$q.screen.gt.sm">
        <q-btn no-caps v-for="item in menu" type="a" :href="item[1]" :label="item[0]" :class="item[2]"></q-btn>
      </q-btn-group>
    `
  },

  'hipeac-dialog-menu': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        visible: false,
        menu: HIPEAC_MENU
      };
    },
    props: {
      modelValue: {
        type: Boolean
      }
    },
    template: `
      <q-dialog v-model="visible" position="top" full-width full-height>
        <q-card class="bg-particles">
          <q-card-section>
            <q-btn unelevated round icon="close" color="white" text-color="dark" v-close-popup />
            <div class="q-gutter-y-md text-center q-pb-xl">
              <hipeac-logo :width="50" class="q-mb-md"></hipeac-logo>
              <p v-for="item in menu" class="text-h4 text-grey-8 text-weight-light">
                <a :href="item[1]" :class="item[2]" class="flat">{{ item[0] }}</a>
              </p>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
    `,
    watch: {
      'modelValue': function (val) {
        if (this.visible != val) this.visible = val;
      },
      'visible': function (val) {
        this.$emit('update:modelValue', val);
      }
    },
    created: function () {
      this.visible = this.modelValue;
    }
  },

  'hipeac-submenu-fabs': {
    props: {
      menu: {
        required: true,
        type: Array,
        default: function () {
          return [];
        }
      },
      checks: {
        type: Object,
        default: function () {
          return {};
        }
      }
    },
    template: `
      <div v-if="!$q.screen.gt.sm" class="fixed-bottom-right" style="z-index: 2001; right: 16px; bottom: 16px">
        <q-fab icon="menu" direction="up" vertical-actions-align="right" color="#005eb8" class="bg-hipeac">
          <q-fab-action square v-for="item in items" :to="item.to" :label="item.label" color="blue-1" text-color="dark" :icon="item.icon"></q-fab-action>
        </q-fab>
      </div>
    `,
    computed: {
      items: function () {
        var checks = this.checks;
        return this.menu.filter(function (item) {
          return !_.has(item, 'check') || checks[item.check];
        });
      }
    }
  },

  'hipeac-submenu-tabs': {
    props: {
      menu: {
        required: true,
        type: Array,
        default: function () {
          return [];
        }
      },
      checks: {
        type: Object,
        default: function () {
          return {};
        }
      },
      hashtag: {
        type: String,
        default: null
      }
    },
    template: `
      <q-tabs v-if="$q.screen.gt.sm" stretch inline-label no-caps>
        <q-route-tab v-for="item in items" :exact="item.exact" :to="item.to" :label="item.label" :icon="item.icon"></q-route-tab>
        <q-route-tab v-if="hashtag" class="q-px-xs" :href="'https://twitter.com/hashtag/' + hashtag + '?f=live'" target="_blank"><twitter-logo :width="20" fill="white" /></q-route-tab>
      </q-tabs>
    `,
    computed: {
      items: function () {
        var checks = this.checks;
        return this.menu.filter(function (item) {
          return !_.has(item, 'check') || checks[item.check];
        });
      }
    }
  },

  'hipeac-user-menu': {
    data: function () {
      return {
        userId: +(document.querySelector('html').dataset.user)
      };
    },
    props: {
      username: {
        type: String
      }
    },
    template: `
      <div v-if="userId > 0" class="row reverse q-gutter-md">
        <q-btn no-caps outline color="primary" :label="username">
          <q-menu anchor="bottom right" self="top right" class="text-body2">
            <q-list style="min-width: 140px">
              <q-item clickable tag="a" :href="'/~' + username + '/'">
                <q-item-section>Public profile</q-item-section>
              </q-item>
              <q-item clickable tag="a" href="/accounts/profile/">
                <q-item-section>Settings</q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable tag="a" href="/accounts/logout/">
                <q-item-section>Sign out</q-item-section>
                <q-item-section side><q-icon name="logout" size="xs" /></q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
        <hipeac-notifications-btn />
      </div>
    `
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

  'hipeac-notifications-btn': {
    setup: function () {
      Vuex.useStore();
    },
    template: `
      <q-btn round flat :icon="icon" :disable="counter == 0" size="md">
        <q-badge v-if="counter" rounded color="red-7" floating>{{ counter }}</q-badge>
        <q-menu anchor="bottom right" self="top right" max-width="300px">
          <q-list separator padding class="text-body2" style="min-width: 140px" >
            <q-item-label header>Notifications</q-item-label>
            <q-item v-for="n in notifications" clickable tag="a" :href="n.message.path">
              <q-item-section side><q-icon :name="n.icon" size="xs" /></q-item-section>
              <q-item-section>{{ n.message.text }}</q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
    `,
    computed: _.extend(
      Vuex.mapState('common', ['notifications']), {
      counter: function () {
        if (this.notifications == undefined) return 0;
        return this.notifications.length;
      },
      icon: function () {
        return (this.counter > 0) ? 'notifications_active' : 'notifications_none';
      }
    }),
    created: function () {
      this.$store.commit('common/getNotifications');
    }
  },

  'hipeac-no-data': {
    props: {
      message: {
        type: String,
        required: true
      },
      filter: {
        type: String,
        default: ''
      }
    },
    template: `
      <div class="full-width text-center q-pa-xl">
        <q-icon size="6em" :name="filter ? 'search_off' : 'layers_clear'" color="grey" />
        <h5 class="text-weight-light text-grey-8">{{ message }}</h5>
      </div>
    `
  },

  'hipeac-highlight-item': {
    props: {
      icon: {
        type: String,
        default: 'star'
      },
      color: {
        type: String,
        default: 'dark'
      },
      external: {
        type: Boolean,
        default: false
      }
    },
    template: `
      <q-item clickable v-ripple :class="text_color">
        <q-item-section avatar>
          <q-icon :name="icon" :color="color" />
        </q-item-section>
        <q-item-section :class="{'text-weight-bold': color != 'dark'}"><slot></slot></q-item-section>
        <q-item-section side>
          <q-icon :name="link_icon" color="grey-8" size="xs" />
        </q-item-section>
      </q-item>
    `,
    computed: {
      text_color: function () {
        return 'text-' + this.color;
      },
      link_icon: function () {
        return this.external ? 'north_east' : 'arrow_forward_ios';
      }
    }
  },

  'hipeac-profile-item': {
    props: {
      profile: {
        required: true,
        type: Object
      },
      dense: {
        type: Boolean,
        default: false
      },
      showAvatar: {
        type: Boolean,
        default: true
      }
    },
    template: `
      <q-item :dense="dense" class="q-pa-none">
        <q-item-section avatar v-if="showAvatar">
          <q-avatar v-if="profile.avatar_url" size="64px">
            <img :src="profile.avatar_url">
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>{{ profile.name }}</q-item-label>
          <q-item-label v-if="profile.institution" caption>{{ profile.institution.name }}<span v-if="profile.institution.country">, {{ profile.institution.country.name }}</span></q-item-label>
        </q-item-section>
      </q-item>
    `
  },

  'hipeac-edit-icon': {
    template: `
      <q-icon name="drive_file_rename_outline" color="primary" class="cursor-pointer" />
    `
  },

  'hipeac-remove-icon': {
    props: {
      size: {
        type: String,
        default: null
      }
    },
    template: `
      <q-icon name="backspace" color="red-12" class="cursor-pointer" :size="size" />
    `
  },

  'hipeac-yes-chip': {
    props: {
      color: {
        type: String,
        default: 'positive'
      },
      icon: {
        type: String,
        default: 'check'
      }
    },
    template: '<q-chip :color="color" text-color="white" size="xs" :icon="icon" class="hipeac-chip">Yes</q-chip>'
  },

  'hipeac-no-chip': {
    props: {
      color: {
        type: String,
        default: 'grey-6'
      },
      icon: {
        type: String,
        default: 'close'
      }
    },
    template: '<q-chip outline :color="color" size="xs" :icon="icon" class="hipeac-chip">No</q-chip>'
  },

  'hipeac-big-alert': {
    props: {
      icon: {
        type: String,
        default: 'warning'
      },
      msg: {
        type: String,
        default: 'You need to log in to your HiPEAC account to view this page.'
      }
    },
    template: `
      <div class="row justify-center">
        <div class="col-12 col-md-8 col-lg-6 text-center">
          <q-icon :name="icon" size="6em" color="blue-2" />
          <h2 class="text-weight-light q-my-lg">{{ msg }}</h2>
          <slot></slot>
        </div>
      </div>
    `
  },

  'hipeac-please-login': {
    data: function () {
      return {
        path: window.location.pathname
      };
    },
    props: {
      msg: {
        type: String,
        default: 'You need to log in to your HiPEAC account to view this page.'
      }
    },
    template: `
      <hipeac-big-alert icon="password" :msg="msg">
        <q-btn outline no-caps type="a" color="primary" :href="'/accounts/login/?next=' + path" label="Log in" size="lg" class="q-my-lg" />
      </hipeac-big-alert>
    `
  },

  'hipeac-logo': {
    props: {
      fill: {
        type: String,
        default: '#1e64c8'
      },
      width: {
        type: Number,
        default: 120
      }
    },
    template: `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 49.07 35.08" :width="width"><g fill-rule="evenodd" clip-rule="evenodd"><path fill="#005eb8" d="M0 24.33 2.64 7.64h3.4l-1 6.36h3.9l1-6.36h3.4l-2.66 16.7H7.3l1.17-7.4H4.56l-1.16 7.4zm18.76 10.75-1.7-10.75h1.85V20.8h.94c2.6 0 3.54-.76 3.54-3.78v-2.16c0-2.3-1.15-3.08-3.25-3.08h-2.26L15.9 24.33h-2.8l1.99-12.56-1.12-6.97L44.26 0l1.92 12.12a5.08 5.08 0 0 0-2.66-.52H42.5c-2.17 0-2.77 1.06-2.45 3.1l1.1 7.02c.26 1.65 1.21 2.73 3.37 2.73h1.05c1.23 0 2.03-.18 2.47-.65l1.04 6.5zm.98-16.59h-.83v-4.43h.8c.5 0 .65.13.65.54v2.98c0 .69-.21.91-.63.91m4.96-6.72v12.56h5.74v-2.3h-2.86v-3.11h2.46v-2.17h-2.46v-2.68h2.65v-2.3zm10.93 1.73.66 5.63h-1.37l.68-5.63zm-2.39-1.73-1.9 12.56h2.96l.36-3.03h1.88l.37 3.03h2.95l-1.9-12.56zm11.24 2.66.25 1.63h2.1l.57 3.6H45.3l.32 1.96c.06.38-.18.53-.65.53-.47 0-.75-.15-.8-.54l-1.15-7.18c-.06-.38.17-.54.66-.54.46 0 .74.16.8.54"/><path fill="#ffe800" d="M15.73 7.63h2.8l-.4 2.47h-2.79z"/></g></svg>
    `
  },

  'github-logo': {
    template: `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180.442 175.988"><defs><clipPath id="a"><path d="M0 140.868h595v560.264H0z"/></clipPath></defs><g fill="#1b1817" clip-path="url(#a)" transform="matrix(1.33333 0 0 -1.33333 -433.6 925.213)"><path fill-rule="evenodd" d="M392.867 693.91c-37.366 0-67.666-30.294-67.666-67.666 0-29.897 19.388-55.261 46.274-64.209 3.382-.626 4.623 1.468 4.623 3.255 0 1.614-.063 6.944-.092 12.598-18.824-4.093-22.797 7.984-22.797 7.984-3.078 7.821-7.513 9.901-7.513 9.901-6.14 4.2.463 4.114.463 4.114 6.795-.478 10.373-6.973 10.373-6.973 6.035-10.345 15.83-7.354 19.69-5.625.608 4.373 2.362 7.358 4.297 9.048-15.03 1.71-30.83 7.513-30.83 33.44 0 7.388 2.644 13.425 6.973 18.163-.703 1.705-3.02 8.587.655 17.908 0 0 5.682 1.818 18.613-6.936 5.398 1.499 11.186 2.25 16.937 2.276 5.75-.025 11.544-.777 16.951-2.276 12.916 8.754 18.59 6.936 18.59 6.936 3.683-9.321 1.366-16.203.663-17.908 4.339-4.738 6.964-10.775 6.964-18.162 0-25.99-15.83-31.712-30.897-33.387 2.427-2.1 4.59-6.218 4.59-12.531 0-9.054-.079-16.341-.079-18.57 0-1.8 1.218-3.91 4.648-3.246 26.871 8.958 46.235 34.313 46.235 64.2 0 37.371-30.295 67.666-67.665 67.666"/><path d="M350.83 596.756c-.15-.336-.679-.437-1.16-.206-.491.22-.767.679-.608 1.016.146.346.676.443 1.165.21.492-.22.773-.683.602-1.02M353.57 593.699c-.323-.3-.953-.16-1.381.313-.443.471-.526 1.102-.199 1.406.333.3.945.159 1.389-.313.442-.477.528-1.103.191-1.406M356.238 589.802c-.415-.288-1.093-.018-1.512.584-.414.601-.414 1.323.01 1.612.42.29 1.088.03 1.512-.568.414-.612.414-1.333-.01-1.628M359.893 586.037c-.37-.41-1.16-.3-1.739.259-.592.545-.756 1.32-.384 1.729.375.41 1.17.294 1.752-.26.587-.544.767-1.324.371-1.728M364.936 583.85c-.164-.53-.925-.77-1.691-.545-.766.232-1.266.853-1.112 1.388.16.534.924.785 1.696.544.764-.231 1.266-.847 1.107-1.386M370.473 583.445c.02-.558-.63-1.02-1.435-1.03-.81-.019-1.464.433-1.473.982 0 .564.636 1.022 1.445 1.035.804.016 1.463-.432 1.463-.987M375.627 584.322c.096-.544-.463-1.103-1.262-1.252-.786-.144-1.513.192-1.613.732-.097.559.472 1.118 1.257 1.262.8.14 1.516-.188 1.618-.741"/></g></svg>
    `
  },

  'google-logo': {
    template: `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M113.47 309.408L95.648 375.94l-65.139 1.378C11.042 341.211 0 299.9 0 256c0-42.451 10.324-82.483 28.624-117.732h.014L86.63 148.9l25.404 57.644c-5.317 15.501-8.215 32.141-8.215 49.456.002 18.792 3.406 36.797 9.651 53.408z" fill="#fbbb00"/><path d="M507.527 208.176C510.467 223.662 512 239.655 512 256c0 18.328-1.927 36.206-5.598 53.451-12.462 58.683-45.025 109.925-90.134 146.187l-.014-.014-73.044-3.727-10.338-64.535c29.932-17.554 53.324-45.025 65.646-77.911h-136.89V208.176h245.899z" fill="#518ef8"/><path d="M416.253 455.624l.014.014C372.396 490.901 316.666 512 256 512c-97.491 0-182.252-54.491-225.491-134.681l82.961-67.91c21.619 57.698 77.278 98.771 142.53 98.771 28.047 0 54.323-7.582 76.87-20.818l83.383 68.262z" fill="#28b446"/><path d="M419.404 58.936l-82.933 67.896C313.136 112.246 285.552 103.82 256 103.82c-66.729 0-123.429 42.957-143.965 102.724l-83.397-68.276h-.014C71.23 56.123 157.06 0 256 0c62.115 0 119.068 22.126 163.404 58.936z" fill="#f14336"/></svg>
    `
  },

  'linkedin-logo': {
    template: `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 75.77 76.25"><path fill="#0077b5" d="M0 5.47C0 2.45 2.51 0 5.6 0h64.57c3.1 0 5.6 2.45 5.6 5.46v65.33c0 3.02-2.5 5.46-5.6 5.46H5.6c-3.09 0-5.6-2.44-5.6-5.46z"/><path fill="#fff" fill-rule="evenodd" d="M22.97 63.83V29.4H11.53v34.43zM17.25 24.7c3.99 0 6.47-2.64 6.47-5.95-.07-3.38-2.48-5.95-6.4-5.95-3.91 0-6.47 2.57-6.47 5.95 0 3.3 2.48 5.95 6.32 5.95zM29.3 63.83h11.45V44.6c0-1.03.07-2.05.37-2.79.83-2.05 2.71-4.18 5.87-4.18 4.15 0 5.8 3.15 5.8 7.78v18.42h11.45V44.09c0-10.58-5.65-15.5-13.18-15.5-6.17 0-8.88 3.45-10.39 5.8h.08V29.4H29.3c.15 3.23 0 34.43 0 34.43z"/></svg>
    `
  },

  'twitter-logo': {
    props: {
      fill: {
        type: String,
        default: '#55ACEE'
      },
      width: {
        type: Number,
        default: 32
      }
    },
    template: `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" :width="width"><path :fill="fill" d="M32 6.08c-1.18.52-2.45.87-3.78 1.03a6.59 6.59 0 0 0 2.89-3.63c-1.27.75-2.67 1.3-4.17 1.6a6.56 6.56 0 0 0-11.18 5.98A18.64 18.64 0 0 1 2.23 4.2a6.54 6.54 0 0 0 2.03 8.76 6.54 6.54 0 0 1-2.97-.82v.09a6.57 6.57 0 0 0 5.26 6.43 6.6 6.6 0 0 1-2.96.12 6.57 6.57 0 0 0 6.13 4.55A13.17 13.17 0 0 1 0 26.05 18.6 18.6 0 0 0 10.06 29c12.07 0 18.68-10 18.68-18.68l-.02-.85c1.28-.92 2.4-2.08 3.27-3.4z"/></svg>
    `
  },

  'ugent-logo': {
    template: `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 75.77 76.25"><path fill="#0077b5" d="M0 5.47C0 2.45 2.51 0 5.6 0h64.57c3.1 0 5.6 2.45 5.6 5.46v65.33c0 3.02-2.5 5.46-5.6 5.46H5.6c-3.09 0-5.6-2.44-5.6-5.46z"/><path fill="#fff" fill-rule="evenodd" d="M22.97 63.83V29.4H11.53v34.43zM17.25 24.7c3.99 0 6.47-2.64 6.47-5.95-.07-3.38-2.48-5.95-6.4-5.95-3.91 0-6.47 2.57-6.47 5.95 0 3.3 2.48 5.95 6.32 5.95zM29.3 63.83h11.45V44.6c0-1.03.07-2.05.37-2.79.83-2.05 2.71-4.18 5.87-4.18 4.15 0 5.8 3.15 5.8 7.78v18.42h11.45V44.09c0-10.58-5.65-15.5-13.18-15.5-6.17 0-8.88 3.45-10.39 5.8h.08V29.4H29.3c.15 3.23 0 34.43 0 34.43z"/></svg>
    `
  },

  'socialaccount-provider': {
    props: {
      provider: {
        type: String,
        required: true
      },
      height: {
        type: String,
        default: '32px'
      }
    },
    template: `
      <component :is="comp" :style="{'height': height}"></component>
    `,
    computed: {
      comp: function () {
        return this.provider.toLowerCase() + '-logo';
      }
    }
  },

  'hipeac-copy-icon': {
    props: {
      text: {
        type: String,
        required: true
      }
    },
    template: '<q-icon name="copy_all" @click.stop="copyToClipboard" class="cursor-pointer" />',
    methods: {
      copyToClipboard: function () {
        Quasar.copyToClipboard(this.text).then(function () {
          Hipeac.utils.notify('Copied to clipboard', 'none');
        }).catch(function () {
          Hipeac.utils.notify('Could not copy to clipboard', 'warning');
        });
      }
    }
  },

  'hipeac-search-bar': {
    emits: ['update:modelValue'],
    data: function () {
      return {
        dialogVisible: false,
        filterData: {}
      };
    },
    props: {
      modelValue: {
        type: String,
        default: ''
      },
      placeholder: {
        type: String,
        default: 'Search...'
      },
      filters: {
        type: Array,
        default: function () {
          return [];
        }
      }
    },
    template: `
      <div>
        <q-input filled :dense="$q.screen.gt.sm" v-model="q" :placeholder="($q.screen.gt.sm) ? placeholder : 'Search...'" type="search" class="text-mono q-mb-md">
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
          <template v-slot:append>
            <q-icon v-show="q !== ''" @click="q = ''" name="close" class="cursor-pointer" />
            <q-icon v-if="filters.length" @click="dialogVisible = true" name="tune" class="cursor-pointer q-ml-sm" />
          </template>
        </q-input>
        <q-dialog v-model="dialogVisible" position="right" @before-show="updateFilters" @before-hide="updateQuery">
          <q-card v-if="filters.length" style="width: 280px; height: 100%" class="q-pa-lg">
            <display-5 class="text-grey-8">Search builder</display-5>
            <div class="q-gutter-md q-mt-md">
              <q-input dense filled v-model="filterData.text" @keyup.enter="dialogVisible = false" type="text" label="Text" />
              <q-separator />
              <q-select v-for="filter in filters" dense filled v-model="filterData[filter.name]" :options="filter.options" :label="filter.name">
                <template v-if="filterData[filter.name]" v-slot:append>
                  <q-icon name="clear" @click.stop="filterData[filter.name] = null" class="cursor-pointer" size="14px" />
                </template>
              </q-select>
            </div>
          </q-card>
        </q-dialog>
      </div>
    `,
    computed: {
      q: {
        get: function () {
          return this.modelValue;
        },
        set: function (val) {
          this.$emit('update:modelValue', val);
        }
      }
    },
    methods: {
      updateQuery: function () {
        var val = this.filterData;
        var q = [val.text];
        _.each(_.keys(val), function (k) {
          if (k != 'text' && val[k]) q.push(k + ':' + val[k]);
        });
        this.$emit('update:modelValue', q.join(' ').trim());
      },
      updateFilters: function () {
        var q = this.q.replace(/\s+/g,' ').trim();

        if (q == '') {
          this.filterData = {};
          return;
        }

        var filterParts = {};
        var textParts = [];

        _.each(q.split(' '), function (word) {
          if (word.indexOf(':') > -1) {
            var s = word.split(':');
            filterParts[s[0]] = s[1];
          } else {
            textParts.push(word);
          }
        });

        filterParts['text'] = textParts.join(' ');

        this.filterData = filterParts;
      }
    }
  },

  'editor-link': {
    data: function () {
      return {
        show: false
      }
    },
    props: {
      url: {
        type: String
      },
      type: {
        type: String,
        default: 'btn'
      }
    },
    template: `
      <q-btn v-if="show && type == 'btn'" flat round icon="edit" type="a" :href="url" target="_editor"></q-btn>
    `,
    created: function () {
      var self = this;
      if (USER_IS_AUTHENTICATED) {
        Hipeac.api.request('head', this.url).then(function (res) {
          if (res.status == 200) self.show = true;
        });
      }
    }
  },

  'stats-progress': {
    props: {
      size: {
        type: String,
        default: 'lg'
      },
      fontSize: {
        type: String,
        default: '12px'
      },
      value: {
        type: Number,
        required: true
      }
    },
    template: `
      <q-circular-progress show-value :size="size" :font-size="fontSize" :value="value" :color="color" track-color="grey-3">
        <samp><strong><slot></slot></strong></samp>
      </q-circular-progress>
    `,
    computed: {
      color: function () {
        if (this.value == 100) return 'positive';
        if (this.value >= 50) return 'blue';
        if (this.value >= 25) return 'light-blue';
        if (this.value >= 10) return 'cyan';
        return 'blue-grey';
      }
    }
  },

  'youtube-embed': {
    props: {
      url: {
        type: String,
        required: true
      },
      hideInfo: {
        type: Boolean,
        default: true
      }
    },
    template: '<q-video :ratio="16/9" :src="src" class="rounded-borders" />',
    computed: {
      youtubeId: function () {
        var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
        var match = this.url.match(regExp);
        return (match && match[7].length == 11) ? match[7] : null;
      },
      src: function () {
        if (!this.youtubeId) return null;
        return [
          'https://www.youtube.com/embed/',
          this.youtubeId,
          (this.hideInfo) ? '?showinfo=0' : ''
        ].join('');
      }
    }
  }

};
