function linkTransform(items) {
    var output = {};
    _.each(items, function(obj){
        output[obj.type] = obj.url;
    });
    return output;
}

function mapper() {
    var getMetadataString = function (obj) {
        return [
            _.map(obj.application_areas, function (o) { return o.value; }).join(' '),
            _.map(obj.topics, function (o) { return o.value; }).join(' ')
        ].join(' ');
    };

    return {
        base: function (items) {
            return items.map(function (obj) {
                obj.q = '';
                return obj;
            });
        },
        articles: function (items) {
            return items.map(function (obj) {
                obj.subheader = obj.type_display;
                return obj;
            });
        },
        breaks: function (items) {
            return items.map(function (obj) {
                obj.icon = {
                    'coffee': 'free_breakfast',
                    'lunch': 'restaurant'
                }[obj.type];
                obj.startAt = obj.start_at.substring(0, 5);
                obj.endAt = obj.end_at.substring(0, 5);
                return obj;
            });
        },
        clippings: function (items) {
            return items.map(function (obj) {
                obj.subheader = obj.media;
                obj.href = obj.url;
                return obj;
            });
        },
        events: function (items) {
            var breaksMapper = this.breaks;
            var sessionsMapper = this.sessions;

            return items.map(function (obj) {
                obj.markedTravelInfo = (obj.travel_info) ? marked(obj.travel_info) : '';
                obj.registrations_round = (obj.registrations_count)
                    ? Math.floor(obj.registrations_count / 10) * 10
                    : 0;
                obj.links = linkTransform(obj.links);
                obj.href = obj.redirect_url || obj.href;
                obj.past = moment().isAfter(obj.end_date);
                obj.datesStr = [
                    moment(obj.start_date).format('MMMM D'),
                    moment(obj.end_date).format('D, YYYY'),
                ].join('-');

                // generate schedule

                if (obj.breaks && obj.breaks.length) {
                    obj.breaks = breaksMapper(obj.breaks);
                    var breaksMap = _.groupBy(obj.breaks, 'date');
                }

                if (obj.sessions && obj.sessions.length) {
                    obj.sessions = sessionsMapper(obj.sessions);
                    var sessionsMap = _.groupBy(obj.sessions, 'date');
                }

                var schedule = _.map(obj.dates, function (date) {
                    return {
                        date: date,
                        breaks: (breaksMap && _.has(breaksMap, date)) ? breaksMap[date] : null,
                        sessions: (sessionsMap && _.has(sessionsMap, date)) ? sessionsMap[date] : null,
                    };
                });
                obj.schedule = _.indexBy(schedule, 'date');

                return obj;
            });
        },
        institutions: function (items) {
            return items.map(function (obj) {
                obj.links = linkTransform(obj.links);
                obj.q = '';
                return obj;
            });
        },
        jobs: function (items) {
            return items.map(function (obj) {
                obj.isNew = moment().diff(moment(obj.created_at), 'days') < 7;
                obj.expiresSoon = moment().diff(moment(obj.deadline), 'days') > -7;
                obj.careerLevelIds = _.pluck(obj.career_levels, 'id');
                obj.topicIds = _.pluck(obj.topics, 'id');
                obj.typeId = obj.employment_type.id;
                obj.internship = obj.employment_type.id == INTERNSHIP;
                obj.q = [
                    getMetadataString(obj),
                    (obj.internship) ? 'internships' : '',
                    obj.title,
                    (obj.institution) ? obj.institution.name + ' ' + obj.institution.short_name : '',
                    (obj.project) ? obj.project.acronym : '',
                    (obj.project) ? obj.project.name : '',
                    (obj.country) ? obj.country.name : '',
                    obj.city,
                    obj.keywords.join(' ')
                ].join(' ').toLowerCase();
                return obj;
            });
        },
        members: function (items, institutions) {
            var ins = _.indexBy(_.map(institutions, _.clone), 'id');
            var mapInstitution = function (id) {
                return (id) ? ins[id] : null;
            };

            return items.map(function (obj) {
                obj.institution = mapInstitution(obj.profile.institution);
                obj.secondary_institution = mapInstitution(obj.profile.secondary_institution);
                obj.topicIds = _.pluck(obj.profile.topics, 'id');
                obj.q = [
                    getMetadataString(obj.profile),
                    obj.profile.name,
                    (obj.institution) ? obj.institution.country : '',
                    (obj.institution) ? obj.institution.name + ' ' + obj.institution.short_name : '',
                    (obj.secondary_institution)
                        ? obj.secondary_institution.name + ' ' + obj.secondary_institution.short_name
                        : ''
                ].join(' ').toLowerCase();
                return obj;
            });
        },
        projects: function (items) {
            return items.map(function (obj) {
                obj.isNew = moment().diff(moment(obj.start_date), 'days') < 60;
                obj.links = linkTransform(obj.links);
                obj.topicIds = _.pluck(obj.topics, 'id');
                obj.q = [
                    getMetadataString(obj),
                    obj.acronym,
                    obj.name
                ].join(' ').toLowerCase();
                return obj;
            });
        },
        publications: function (items) {
            return items.map(function (obj) {
                obj.q = [
                    obj.year,
                    obj.title,
                    (obj.conference) ? obj.conference : '',
                ].join(' ').toLowerCase();
                return obj;
            });
        },
        sessions: function (items) {
            return items.map(function (obj) {
                obj.markedSummary = (obj.summary) ? marked(obj.summary) : '';
                obj.startAt = obj.start_at.substring(0, 5);
                obj.endAt = obj.end_at.substring(0, 5);
                obj.q = [
                    getMetadataString(obj),
                    obj.title
                ].join(' ').toLowerCase();
                return obj;
            });
        },
        videos: function (items) {
            return items.map(function (obj) {
                obj.href = 'https://www.youtube.com/watch?v=' + obj.youtube_id;
                obj.snapshot = 'https://i.ytimg.com/vi/' + obj.youtube_id + '/mqdefault.jpg';
                obj.topicIds = _.pluck(obj.topics, 'id');
                obj.q = [
                    getMetadataString(obj),
                    obj.title,
                    obj.user.profile.name,
                ].join(' ').toLowerCase();
                return obj;
            });
        },
        visions: function (items) {
            return items.map(function (obj) {
                obj.markedIntroduction = marked(obj.introduction);
                obj.markedSummary = marked(obj.summary);
                obj.year = obj.publication_date.substring(0, 4);
                obj.q = '';
                return obj;
            });
        }
    };
}
