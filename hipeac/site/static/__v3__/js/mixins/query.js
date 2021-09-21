var QueryMixin = {
  props: ['q'],
  data: function () {
    return {
      query: this.q || ''
    }
  },
  methods: {
    customFilter: function (rows, terms, cols, getCellValue) {
      return Hipeac.utils.filter(rows, terms);
    }
  },
  watch: {
    query: function (val, oldVal) {
      if (val == '') this.$router.replace({query: {q: undefined}});
      else if (val != this.$route.query.q && val != oldVal) this.$router.replace({query: {q: val}});
    }
  },
  created: function () {
    if (this.$route.query.q) {
      this.query = this.$route.query.q;
    }
  }
};
