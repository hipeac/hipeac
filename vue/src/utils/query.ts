const getQString = (obj: Object, fields: string[]): string => {
  let query = '';

  fields.forEach((field) => {
    if (obj[field]) {
      query += obj[field].toLowerCase();
    }
  });

  return query;
};

export { getQString };
