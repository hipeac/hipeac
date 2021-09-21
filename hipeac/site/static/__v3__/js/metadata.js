var HipeacMetadata = {
  options: {
    gender: {
      female: 'Female',
      male: 'Male',
      'non-binary': 'Non-binary'
    },
    dietary: {
      none: 'No special requirements',
      vegetarian: 'Vegetarian',
      vegan: 'Vegan',
      kosher: 'Kosher',
      muslim: 'Muslim',
      'intolerant-gluten': '[Intolerant] Gluten',
      'intolerant-lactose': '[Intolerant] Lactose',
      'allergic-crustaceans': '[Allergic] Crustaceans',
      'allergic-peanuts': '[Allergic] Peanuts'
    }
  },
  getQuasarOptions: function (metadata) {
    var out = [];
    _.each(this.options[metadata], function (val, key) {
      out.push({
        'value': key,
        'label': val
      });
    });
    return out;
  }
};
