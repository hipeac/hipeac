var DjangoComponents = {

  'django-form': {
    data: function () {
      return {
        csrfToken: document.querySelector('html').dataset.csrfToken,
        mutable: {}
      };
    },
    props: {
      action: {
        type: String,
        required: true
      },
      fields: {
        type: Array,
        default: function () {
          return [];
        }
      },
      btnName: {
        type: String,
        default: null
      },
      btnText: {
        type: String,
        default: 'Send'
      }
    },
    template: `
      <form method="post" :action="action">
        <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken">
        <div class="row q-col-gutter-sm">
          <q-input dense filled v-for="f in fields" v-model="mutable[f.name]" :name="f.name" :label="f.label + ((f.required) ? ' *' : '')" :type="f.type" :required="f.required" class="col-12" :class="f.class" />
        </div>
        <slot></slot>
        <q-btn unelevated :name="btnName" color="primary" type="submit" class="q-mt-lg" :disable="!valid">{{ btnText }}</q-btn>
      </form>
    `,
    computed: {
      valid: function () {
        var mutable = this.mutable;
        var fails = 0;

        _.each(this.fields, function (f) {
          if (f.required && (mutable[f.name] == undefined || !mutable[f.name].length)) fails++;
        });

        return fails == 0;
      }
    }
  }

};
