var HipeacStorage = {
  defaults: {
    set: function (key, value) {
      Quasar.LocalStorage.set('hipeac.defaults.' + key, value);
    },
    get: function (key) {
      return Quasar.LocalStorage.getItem('hipeac.defaults.' + key);
    },
    delete: function (key) {
      Quasar.LocalStorage.remove('hipeac.defaults.' + key);
    }
  },
  cache: {
    set: function (key, value, ttl) {
      var t = new Date();
      t.setSeconds(t.getSeconds() + (ttl || 120));
      Quasar.LocalStorage.set('hipeac.cache.' + key, {expires: t, value: value});
    },
    get: function (key) {
      var data = Quasar.LocalStorage.getItem('hipeac.cache.' + key);
      if (data && new Date(data.expires) > new Date()) {
        return data.value;
      } else {
        Quasar.LocalStorage.remove('hipeac.cache.' + key);
        return undefined;
      }
    },
    delete: function (key) {
      Quasar.LocalStorage.remove('hipeac.cache.' + key);
    }
  },
  stacks: {
    set: function (key, value, ttl) {
      var max_size = 10;
      var t = new Date();
      t.setSeconds(t.getSeconds() + (ttl || 120));
      value.expires = t;
      var stack = Quasar.LocalStorage.getItem('hipeac.stacks.' + key) || [];
      if (stack.length == max_size) {
        stack.pop();
      }
      stack.push({expires: t, data: value});
      Quasar.LocalStorage.set('hipeac.stacks.' + key, stack);
    },
    get: function (key, id) {
      var stack = Quasar.LocalStorage.getItem('hipeac.stacks.' + key) || [];
      var item = _.find(stack, function (obj) {
        return obj.data.id == id;
      });

      if (item) {
        if (new Date(item.expires) > new Date()) {
          return item;
        } else {
          clean_stack = _.reject(stack, function (obj) { return obj.data.id == id; });
          Quasar.LocalStorage.set('hipeac.stacks.' + key, clean_stack);
          return undefined;
        }
      } else {
        return undefined;
      }
    },
    delete: function (key, id) {
      var stack = Quasar.LocalStorage.getItem('hipeac.stacks.' + key) || [];
      clean_stack = _.reject(stack, function (obj) { return obj.data.id == id; });
      Quasar.LocalStorage.set('hipeac.stacks.' + key, clean_stack);
    }
  }
};
