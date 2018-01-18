var mapper = function () {
    return {
        base: function (items) {
            return items.map(function (obj) {
                obj.q = '';
                return obj;
            });
        },
        projects: function (items) {
            return items.map(function (obj) {
                obj.topicIds = _.pluck(obj.topics, 'id');
                obj.q = [
                    obj.acronym.toLowerCase(),
                    obj.name.toLowerCase(),
                    _.map(obj.application_areas, function (o) { return o.value.toLowerCase(); }).join(' '),
                    _.map(obj.topics, function (o) { return o.value.toLowerCase(); }).join(' ')
                ].join(' ');
                return obj;
            });
        },
        institutions: function (items) {
            return items.map(function (obj) {
                obj.q = '';
                return obj;
            });
        },
        jobs: function (items) {
            return items.map(function (obj) {
                obj.careerLevelIds = _.pluck(obj.career_levels, 'id');
                obj.topicIds = _.pluck(obj.topics, 'id');
                obj.typeId = obj.employment_type.id;
                obj.internship = obj.employment_type.id == INTERNSHIP;
                obj.q = [
                    (obj.internship) ? 'internships' : '',
                    obj.title.toLowerCase(),
                    (obj.institution) ? obj.institution.name.toLowerCase() : '',
                    (obj.project) ? obj.project.acronym.toLowerCase() : '',
                    (obj.project) ? obj.project.name.toLowerCase() : '',
                    (obj.country) ? obj.country.name.toLowerCase() : '',
                    obj.city,
                    obj.keywords.join(' '),
                    _.map(obj.application_areas, function (o) { return o.value.toLowerCase(); }).join(' '),
                    _.map(obj.topics, function (o) { return o.value.toLowerCase(); }).join(' ')
                ].join(' ');
                return obj;
            });
        }
    };
};
