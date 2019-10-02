var CommonMarkReader = new commonmark.Parser({safe: true, smart: true});
var CommonMarkWriter = new commonmark.HtmlRenderer();

var EventHub = new Vue();


var FETCH_WAIT = 250;
var ComponentStore = new Vuex.Store({
    state: {
        options: null,
        articles: null,
        quotes: [],
        metadata: [],
        institutions: [],
        projects: []
    },
    mutations: {
        fetchArticles: _.debounce(function (state) {
            if (!state.articles) {
                api().getArticles().then(function (res) {
                    state.articles = Object.freeze(mapper().articles(res));
                });
            }
        }, FETCH_WAIT),
        fetchQuotes: _.debounce(function (state) {
            if (!state.quotes.length) {
                api().getQuotes().then(function (res) {
                    state.quotes = Object.freeze(res);
                });
            }
        }, FETCH_WAIT),
        fetchMetadata: _.debounce(function (state) {
            if (!state.metadata.length) {
                api().getMetadata().then(function (res) {
                    state.metadata = Object.freeze(res);
                });
            }
        }, FETCH_WAIT),
        fetchInstitutions: _.debounce(function (state) {
            if (!state.institutions.length) {
                api().getAllInstitutions().then(function (res) {
                    state.institutions = Object.freeze(res.map(function (obj) {
                        obj.display = obj.name;
                        obj.q = [
                            obj.name,
                            obj.local_name,
                            obj.short_name
                        ].join(' ').toLowerCase();
                        return obj;
                    }));
                });
            }
        }, FETCH_WAIT),
        fetchProjects: _.debounce(function (state) {
            if (!state.projects.length) {
                api().getAllProjects().then(function (res) {
                    state.projects = Object.freeze(res.map(function (obj) {
                        obj.display = [
                            obj.acronym,
                            (obj.ec_project_id) ? ' #' + obj.ec_project_id : ''
                        ].join('');
                        obj.q = [
                            obj.display,
                            obj.name
                        ].join(' ').toLowerCase();
                        return obj;
                    }));
                });
            }
        }, FETCH_WAIT),
        setOptions: function (state, options) {
            state.options = Object.freeze(options);
        }
    },
    getters: {
        groupedArticles: function (state) {
            if (!state.articles) return null;
            return {
                type: _.groupBy(state.articles, 'type'),
                event: _.groupBy(state.articles, 'event')
            }
        },
        requiredFields: function (state) {
            if (!state.options) return null;
            if (_.has(state.options.actions, 'POST')) return _.keys(state.options.actions.POST);
            if (_.has(state.options.actions, 'PUT')) return _.keys(state.options.actions.PUT);
            return null;
        },
        fields: function (state) {
            if (!state.options) return null;
            if (_.has(state.options.actions, 'POST')) return state.options.actions.POST;
            if (_.has(state.options.actions, 'PUT')) return state.options.actions.PUT;
            return null;
        },
        metadataDict: function (state) {
            return _.indexBy(state.metadata, 'id');
        },
        groupedMetadata: function (state) {
            if (!state.metadata) return null;
            return _.groupBy(state.metadata, 'type');
        },
    }
});

Vue.filter('moment', function (date, format) {
    return moment(date).format(format || 'll');
});

Vue.filter('markdown', function (text) {
    return CommonMarkWriter.render(CommonMarkReader.parse(text));
});

Vue.component('marked', {
    props: {
        text: {
            type: String,
            default: ''
        }
    },
    template: '' +
        '<div class="marked" v-html="compiledMarkdown"></div>' +
    '',
    computed: {
        compiledMarkdown: function () {
            if (!this.text) return '';
            return CommonMarkWriter.render(CommonMarkReader.parse(this.text));
        }
    }
});

Vue.directive('tooltip', function (el, binding) {
    var val = binding.value;

    $(el).tooltip({
        title: (val) ? val : '',
        placement: 'bottom',
        trigger: 'hover',
        delay: {show: 400, hide: 0}
    });
});

Vue.component('loading', {
    data: function () {
        return {
            visible: false
        }
    },
    props: {
        text: {
            type: String,
            default: 'Loading...'
        },
        icon: {
            type: String,
            default: 'graph_eq'
        },
        delay: {
            type: Number,
            default: 500
        }
    },
    template: '' +
        '<span v-show="visible" class="navbar-text text-primary pt-0">' +
            '<i class="material-icons sm mr-2">{{ icon }}</i>{{ text }}' +
        '</span>' +
    '',
    methods: {
        show: function (val) {
            var self = this;
            setTimeout(function () {
                self.visible = val;
            }, (val) ? 0 : this.delay);
        }
    },
    created: function () {
        EventHub.$on('loading', this.show);
    },
    beforeDestroy: function () {
        EventHub.$off('loading');
    }
});

Vue.component('loading2', {
    template: '' +
        '<div class="text-center my-5">' +
            '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="80px" height="80px" viewBox="0 0 40 40" enable-background="new 0 0 40 40" xml:space="preserve">' +
                '<path opacity="0.1" fill="#000" d="M20.201,5.169c-8.254,0-14.946,6.692-14.946,14.946c0,8.255,6.692,14.946,14.946,14.946 s14.946-6.691,14.946-14.946C35.146,11.861,28.455,5.169,20.201,5.169z M20.201,31.749c-6.425,0-11.634-5.208-11.634-11.634 c0-6.425,5.209-11.634,11.634-11.634c6.425,0,11.633,5.209,11.633,11.634C31.834,26.541,26.626,31.749,20.201,31.749z"/>' +
                '<path fill="yellow" d="M26.013,10.047l1.654-2.866c-2.198-1.272-4.743-2.012-7.466-2.012h0v3.312h0 C22.32,8.481,24.301,9.057,26.013,10.047z">' +
                '<animateTransform attributeType="xml" attributeName="transform" type="rotate" from="0 20 20" to="360 20 20" dur="1s" repeatCount="indefinite"/>' +
                '</path>' +
            '</svg>' +
        '</div>' +
    ''
});

Vue.component('editor-link', {
    data: function () {
        return {
            show: false
        }
    },
    props: ['url'],
    template: '' +
        '<li v-if="show" class="nav-item">' +
            '<a class="nav-link" :href="url"><i class="material-icons mr-1">edit</i>Edit</a>' +
        '</li>' +
    '',
    created: function () {
        var self = this;
        if (USER_IS_AUTHENTICATED) {
            ajax().head(this.url).then(function (res, statusText, request) {
                if (request.status == 200) self.show = true;
            });
        }
    }
});

Vue.component('hipeac-logo', {
    template: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 366"><g fill-rule="evenodd" clip-rule="evenodd"><path fill="#005eb8" d="M7.5 251.8L34.3 82.3h34.5l-10.2 64.6h39.6l10.2-64.6h34.5L116 251.8H81.6l11.9-75H53.8l-11.8 75zM198 361l-17.2-109.2h18.7v-36h9.6c26.4 0 35.9-7.7 35.9-38.3v-22c0-23.4-11.6-31.3-33-31.3h-22.9l-20.2 127.6h-28.5l20.2-127.6-11.3-70.8L457 4.7l19.5 123.1a51.6 51.6 0 0 0-27-5.3H439c-22 0-28.1 10.8-24.9 31.4l11.3 71.4C428 242 437.6 253 459.5 253h10.7c12.5 0 20.6-1.8 25.1-6.6l10.5 66L198 361zm10-168.5h-8.5v-45h8.2c5 0 6.6 1.3 6.6 5.5v30.2c0 7-2.2 9.3-6.4 9.3m50.3-68.3v127.6h58.3v-23.4h-29v-31.6h25v-22h-25l-.1-27.2h27v-23.4h-56.2zm111 17.6L376 199H362l6.9-57.2h.3zM345 124.2l-19.3 127.6h30l3.7-30.8h19.1l3.7 30.8h30l-19.3-127.6H345zm114.1 27l2.6 16.6H483l5.8 36.5h-21.2l3.2 20c.6 3.8-1.8 5.3-6.6 5.3s-7.6-1.5-8.2-5.4l-11.6-73c-.6-3.8 1.7-5.4 6.7-5.4 4.7 0 7.5 1.6 8.1 5.4"/><path fill="#ffe800" d="M167.3 82.2h28.4l-4 25.1h-28.4z"/></g></svg>'
});

Vue.component('linkedin-icon', {
    template: '' +
        '<span class="svg-icon">' +
            '<svg focusable="false" cxmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"></path></svg>' +
        '</span>' +
    ''
});

Vue.component('twitter-icon', {
    template: '' +
        '<span class="svg-icon">' +
            '<svg focusable="false" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path></svg>' +
        '</span>' +
    ''
});

Vue.component('youtube-icon', {
    template: '' +
        '<span class="svg-icon">' +
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 727.222 512.361"><defs><clipPath id="a"><path d="M0 123.5h595v595H0z"/></clipPath></defs><g clip-path="url(#a)" transform="matrix(1.33333 0 0 -1.33333 -33.057 817.515)"><path d="M297.5 613.136s-170.556 0-213.09-11.472c-23.47-6.314-41.95-24.914-48.224-48.534C24.793 510.32 24.793 421 24.793 421s0-89.319 11.393-132.134c6.273-23.617 24.757-42.217 48.225-48.533 42.534-11.47 213.09-11.469 213.09-11.469s170.556 0 213.086 11.47c23.472 6.315 41.953 24.915 48.225 48.532C570.21 331.681 570.21 421 570.21 421s0 89.32-11.398 132.13c-6.272 23.621-24.753 42.22-48.225 48.534-42.53 11.472-213.086 11.472-213.086 11.472zm-55.78-111.04l142.55-81.1-142.55-81.092v162.192z"/></g></svg>' +
        '</span>' +
    ''
});

Vue.component('marked-text', {
    props: ['text', 'q'],
    template: '' +
        '<span :class="css">{{ text }}</span>' +
    '',
    computed: {
        css: function () {
            return (this.q != '' && this.text.toLowerCase().indexOf(this.q) !== -1)
                ? 'bg-light-blue'
                : ''
            ;
        }
    }
});

Vue.component('icon', {
    props: ['name'],
    template: '' +
        '<i class="material-icons">{{ name }}</i>' +
    ''
});

Vue.component('institution-icon', {
    props: ['type'],
    template: '' +
        '<i class="material-icons">{{ name }}</i>' +
    '',
    computed: {
        name: function () {
            return {
                university: 'account_balance',
                lab: 'layers',
                innovation: 'device_hub',
                industry: 'business',
                sme: 'business',
                other: 'scatter_plot',
            }[this.type];
        }
    }
});

Vue.component('huge-icon', {
    props: ['name'],
    template: '' +
        '<div class="huge-icon-wrapper">' +
            '<i class="material-icons">{{ name }}</i>' +
        '</div>' +
    ''
});

Vue.component('metadata-join', {
    props: ['items'],
    template: '' +
        '<span>{{ string }}</span>' +
    '',
    computed: {
        string: function () {
            return _.pluck(this.items, 'value').join(', ');
        }
    }
});

Vue.component('display-lg', {
    template: '' +
        '<h2 class="display display-lg"><span><slot></slot></span></h2>' +
    ''
});

Vue.component('display-md', {
    template: '' +
        '<h5 class="display display-md"><span><slot></slot></span></h5>' +
    ''
});

Vue.component('display-sm', {
    template: '' +
        '<h6 class="display display-sm text-left m-0"><span><slot></slot></span></h6>' +
    ''
});

Vue.component('catchphrase', {
    template: '' +
        '<h5 class="catchphrase"><slot></slot></h5>' +
    ''
});

Vue.component('issuu-embed', {
    props: ['src'],
    template: '' +
        '<div class="embed-responsive embed-responsive-4by3 rounded">' +
            '<iframe class="embed-responsive-item" :src="src" frameborder="0" allowfullscreen></iframe>' +
        '</div>' +
    ''
});

Vue.component('youtube-embed', {
    props: ['url', 'hideInfo'],
    template: '' +
        '<div class="embed-responsive embed-responsive-16by9 rounded">' +
            '<iframe class="embed-responsive-item" :src="src" frameborder="0" allowfullscreen></iframe>' +
        '</div>' +
    '',
    computed: {
        youtubeId: function () {
            var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
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
});

var SimpleList = Vue.extend({
    methods: {
        updateLocation: function (url, target) {
            var w = window.open(url, target || '_self');
            w.focus();
        }
    }
});

var SimpleItemCard = SimpleList.extend({
    props: {
        title: {
            type: String,
            default: ''
        },
        max: {
            type: Number,
            default: 1000
        },
        showMore: {
            type: Boolean,
            default: false
        },
        externalLinks: {
            type: Boolean,
            default: false
        }
    },
    template: '' +
        '<div v-if="items">' +
            '<div v-if="visibleItems.length" class="hipeac-card">' +
                '<display-sm class="mb-3">{{ title }}</display-sm>' +
                '<table class="table pointer m-0">' +
                    '<tbody>' +
                        '<tr v-for="item in visibleItems" :key="item.id" @click="updateLocation(item.href, (externalLinks) ? \'_blank\' : \'_self\')">' +
                            '<td class="pl-0">' +
                                '<small><strong>{{ item.subheader }}</strong>, {{ item.publication_date | moment }}</small></br>' +
                                '{{ item.title }}' +
                            '</td>' +
                            '<td class="text-right align-middle pr-0">' +
                                '<a v-if="externalLinks" :href="item.href" target="_blank">' +
                                    '<i class="material-icons sm">open_in_new</i>' +
                                '</a>' +
                                '<a v-else :href="item.href">' +
                                    '<i class="material-icons sm">arrow_forward</i>' +
                                '</a>' +
                            '</td>' +
                        '</tr>' +
                    '</tbody>' +
                '</table>' +
                '<div v-if="showMore" class="text-center mt-4">' +
                    '<a href="/news/" class="btn btn-sm btn-light text-secondary ml-3">'+
                        '<span>All news <i class="material-icons sm">arrow_forward</i></span>' +
                    '</a>' +
                '</div>' +
            '</div>' +
        '</div>' +
        '<div v-else class="w-100">' +
            '<div class="hipeac-card skeleton">' +
                '<span class="text w-25"></span>' +
                '<table class="table m-0 mt-3">' +
                    '<tbody>' +
                        '<tr v-for="item in skeletons" :key="item">' +
                            '<td class="pl-0">' +
                                '<span class="text sm w-25"></span><br>' +
                                '<span class="text w-100"></span>' +
                                '<span class="text w-75"></span>' +
                            '</td>' +
                        '</tr>' +
                    '</tbody>' +
                '</table>' +
            '</div>' +
        '</div>' +
    '',
    computed: {
        skeletons: function () {
            return Array.apply(null, {length: 5}).map(Number.call, Number);
        }
    }
});

Vue.component('article-card', SimpleItemCard.extend({
    store: ComponentStore,
    props: {
        type: {
            type: String,
            default: null
        },
        eventId: {
            type: Number,
            default: null
        }
    },
    computed: _.extend(
        Vuex.mapState(['articles']),
        Vuex.mapGetters(['groupedArticles']), {
        items: function () {
            return this.articles;
        },
        visibleItems: function () {
            if (!this.articles) return false;
            if (this.type) return _.first(this.groupedArticles['type'][this.type], this.max);
            if (this.eventId) return _.first(this.groupedArticles['event'][this.eventId], this.max);
            return _.first(this.articles, this.max);
        }
    }),
    created: function () {
        this.$store.commit('fetchArticles');
    }
}));

Vue.component('event-list', SimpleList.extend({
    data: function () {
        return {
            showMore: false
        }
    },
    props: {
        items: {
            type: Array
        },
        min: {
            type: Number,
            default: 8
        },
        max: {
            type: Number,
            default: 1000
        }
    },
    template: '' +
        '<div>' +
            '<div v-if="items" v-for="(data, isPast) in visibleItems">' +
                '<display-sm v-if="isPast == \'false\'" :transparent="true" class="mb-3">Upcoming events</display-sm>' +
                '<display-sm v-else :transparent="true" class="mb-3">Past events</display-sm>' +
                '<table class="table pointer mt-0 mb-3">' +
                    '<tbody>' +
                        '<tr v-for="item in data" :key="item.id" @click="updateLocation(item.href, (item.redirect_url) ? \'_blank\' : \'_self\')">' +
                            '<td class="px-0" style="width:50px">' +
                                '<img v-if="item.images" :src="item.images.th" class="rounded w-100">' +
                                '<span v-else class="avatar rounded"></span>' +
                            '</td>' +
                            '<td>' +
                                '{{ item.name }} {{ item.is_past }}<br>' +
                                '<small><strong>{{ item.country.name }}</strong>, {{ item.datesStr }}</small>'+
                            '</td>' +
                            '<td class="text-right align-middle pr-0">' +
                                '<a v-if="item.redirect_url" :href="item.href" target="_blank">' +
                                    '<i class="material-icons sm">open_in_new</i>' +
                                '</a>' +
                                '<a v-else :href="item.href">' +
                                    '<i class="material-icons sm">arrow_forward</i>' +
                                '</a>' +
                            '</td>' +
                        '</tr>' +
                    '</tbody>' +
                '</table>' +
            '</div>' +
            '<div v-if="items && items.length > min" class="text-center mt-4">' +
                '<button @click="showMore = !showMore" type="button" class="btn btn-sm btn-light text-secondary">'+
                    '<span v-if="showMore"><i class="material-icons sm">remove</i> Show less</span>' +
                    '<span v-else><i class="material-icons sm">add</i> Show more</span>' +
                '</button>' +
                '<a v-if="max < items.length" href="/events/" class="btn btn-sm btn-light text-secondary ml-3">'+
                    '<span>All events <i class="material-icons sm">arrow_forward</i></span>' +
                '</a>' +
            '</div>' +
        '</div>' +
    '',
    computed: {
        visibleItems: function () {
            if (!this.items) return [];

            var size = (this.showMore) ? this.max : this.min;
            var items = _.groupBy(_.first(this.items, size), 'past');
            if (_.has(items, false)) items[false].reverse();
            return items;
        }
    }
}));

Vue.component('metadata-list', SimpleList.extend({
    props: ['items'],
    template: '' +
        '<p class="m-0 text-secondary compact-height">' +
            '<small class="mr-1" v-for="i in items">{{ i.value }}</small>' +
        '</p>' +
    ''
}));

Vue.component('filter-label', {
    props: ['text', 'selected'],
    template: '' +
        '<small class="filter-label pointer" :class="data[0]"><i class="material-icons" :class="data[1]" v-html="data[2]"></i> {{ text }}</small>' +
    '',
    computed: {
        data: function () {
            if (this.selected) return ['text-primary font-weight-bold', 'text-primary', '&#xE892;'];
            return ['', 'text-secondary', '&#xE893;'];
        }
    }
});

Vue.component('quotes-carousel-row', {
    store: ComponentStore,
    data: function () {
        return {
            interval: 8 * 1000,
            limit: 5,
        }
    },
    props: ['types'],
    template: '' +
        '<div v-if="items.length > 0" class="row justify-content-md-center mt-5">' +
            '<div class="col-12 col-md-8">' +
                '<div id="carousel" class="hipeac carousel slide" data-ride="carousel" :data-interval="interval">' +
                    '<ol class="carousel-indicators">' +
                        '<li v-for="(item, index) in items" :key="item.id" :data-slide-to="index" :class="{active: index == 0}" data-target="#carousel"></li>' +
                    '</ol>' +
                    '<div class="carousel-inner">' +
                        '<blockquote class="carousel-item" v-for="(item, index) in items" :key="item.id" :class="{active: index == 0}">' +
                            '<p><span>{{ item.text }}</span></p>' +
                            '<footer>— {{ item.author }}</footer>' +
                        '</blockquote>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
    '',
    computed: _.extend(
        Vuex.mapState(['quotes']), {
        items: function () {
            if (!this.quotes) return [];
            if (!this.types) return _.sample(this.quotes, this.limit);
            var types = this.types.split(',');
            return _.sample(this.quotes.filter(function (obj) {
                return _.contains(types, obj.type);
            }), this.limit);
        }
    }),
    created: function () {
        this.$store.commit('fetchQuotes');
    }
});

Vue.component('search-box', {
    data: function () {
        return {
            q: '',
            showFilters: false
        }
    },
    props: {
        eventName: {
            type: String,
            default: 'query-changed'
        },
        placeholder: {
            type: String,
            default: ''
        }
    },
    template: '' +
        '<div class="input-group search-bar pr-3">' +
            '<div class="input-group-prepend">' +
                '<div class="input-group-text">' +
                    '<i v-if="q" @click="q = \'\'" class="material-icons text-secondary pointer">&#xE5CD;</i>' +
                    '<i v-else class="material-icons text-primary">&#xE8B6;</i>' +
                '</div>' +
            '</div>' +
            '<input v-model="q" type="text" class="form-control" :placeholder="placeholder">' +
        '</div>' +
    '',
    watch: {
        'q': _.debounce(function (val, oldVal) {
            if (val != oldVal) {
                if (val != '') this.$router.replace({query: {q: val}});
                else this.$router.replace({name: this.$route.name});

                EventHub.$emit(this.eventName, val);
            }
        }, 250)
    },
    methods: {
        updateQuery: function (val) {
            this.q = val;
        }
    },
    created: function () {
        if (this.$route.query.q) {
            this.q = this.$route.query.q;
            EventHub.$emit(this.eventName, this.q);
        }
        EventHub.$on('carousel-query-sent', this.updateQuery);
    }
});

Vue.component('search-card', {
    data: function () {
        return {
            showFilters: false
        }
    },
    props: {
        showFiltersButton: {
            type: Boolean,
            default: false
        },
        placeholder: {
            type: String,
            default: ''
        }
    },
    template: '' +
        '<div class="hipeac-card py-3">' +
            '<div class="d-flex flex-row justify-content-between">' +
                '<search-box :placeholder="placeholder"></search-box>' +
                '<button v-if="showFiltersButton" class="btn btn-sm" @click="showFilters = !showFilters">' +
                    '<span v-if="showFilters"><icon name="keyboard_arrow_up"></icon><span class="d-none d-md-inline ml-1">Hide filters</span></span>' +
                    '<span v-else><icon name="filter_list"></icon><span class="d-none d-md-inline ml-1">Show filters</span></span>' +
                '</button>' +
            '</div>' +
            '<div v-if="showFilters">' +
                '<hr>' +
                '<slot></slot>' +
            '</div>' +
        '</div>' +
    ''
});

Vue.component('search-results', {
    props: ['count'],
    template: '' +
        '<button class="btn btn-sm btn-block btn-outline-secondary mb-2" disabled>' +
            'Showing top <strong>{{ count }}</strong> results.' +
        '</button>' +
    ''
});

Vue.component('filters-clear', {
    props: {
        onClick: {
            type: Function,
            required: true
        }
    },
    template: '' +
        '<button @click.prevent="onClick" class="btn btn-link text-sm text-danger float-right">&times; Clear all</button>' +
    ''
});

Vue.component('papers-table', {
    props: {
        items: {
            type: Array
        },
        showConference: {
            type: Boolean,
            default: false
        },
        filterIds: {
            type: Boolean,
            default: false
        },
        ids: {
            type: Array,
            default: function () {
                return [];
            }
        }
    },
    template: '' +
        '<table v-if="items" class="table table-sm">' +
            '<tr v-for="item in items" :key="item.id" :v-hide="filterIds && ids.indexOf(item.id) < 0">' +
                '<td><icon name="description" class="sm"></icon></td>' +
                '<td><span v-if="showConference && item.conference" class="badge badge-primary mr-2">{{ item.conference }}</span>{{ item.title }} <small class="text-secondary">{{ item.authors_string }}</small></td>' +
                '<td v-if="showConference" class="text-sm text-secondary align-middle">{{ item.year }}</td>' +
                '<td class="text-right align-middle pr-0">' +
                    '<a v-if="item.url" :href="item.url" target="_blank">' +
                        '<i class="material-icons sm">open_in_new</i>' +
                    '</a>' +
                '</td>' +
            '</tr>' +
        '</table>' +
        '<skeleton-table v-else :withHeader="true" class="m-0 mt-3"></skeleton-table>' +
    '',
    computed: {
        skeletons: function () {
            return Array.apply(null, {length: 5}).map(Number.call, Number);
        }
    }
});

Vue.component('project-cards', SimpleList.extend({
    props: {
        items: {
            type: Array
        },
        ids: {
            type: Array,
            default: function () {
                return [];
            }
        }
    },
    template: '' +
        '<div class="row mini-card-gutters">' +
            '<div v-for="item in items" :key="item.id" class="col-12 col-sm-6 col-md-4 col-lg-3 d-flex align-items-stretch" :v-hide="ids.indexOf(item.id) < 0">' +
                '<div class="hipeac-card mini-card mb-0 inherit d-flex flex-column pointer" @click="updateLocation(item.href)">' +
                    '<span class="header">' +
                        '<img v-if="item.images" :src="item.images.sm" class="logo">' +
                    '</span>' +
                    '<h6 class="title mb-auto">{{ item.acronym }}: {{ item.name }}</h6>' +
                    '<ul class="list-unstyled text-secondary">' +
                        '<li v-if="item.start_date && item.end_date">' +
                            '<strong v-if="item.isNew" class="new float-right">New</strong>' +
                            '<icon name="today" class="sm"></icon>' +
                            '<span class="deadline">{{ item.start_date | moment }} - {{ item.end_date | moment }}</span>' +
                        '</li>' +
                        '<li v-if="item.programme">' +
                            '<icon name="adjust" class="sm"></icon>{{ item.programme.value }}' +
                        '</li>' +
                        '<li><icon name="label" class="sm"></icon><metadata-join :items="item.topics"></metadata-join></li>' +
                    '</ul>' +
                '</div>' +
            '</div>' +
        '</div>' +
    ''
}));

Vue.component('job-cards', SimpleList.extend({
    props: {
        items: {
            type: Array
        },
        ids: {
            type: Array,
            default: function () {
                return [];
            }
        }
    },
    template: '' +
        '<div v-if="items.length" class="row mini-card-gutters">' +
            '<div v-for="item in items" :key="item.id" class="col-12 col-sm-6 col-md-4 col-lg-3 d-flex align-items-stretch" :v-hide="ids.indexOf(item.id) < 0">' +
                '<div class="hipeac-card mini-card mb-0 inherit d-flex flex-column pointer" @click="updateLocation(item.href)">' +
                    '<span class="header">' +
                        '<img v-if="item.institution.images" :src="item.institution.images.sm" class="logo">' +
                    '</span>' +
                    '<h6 class="title mb-auto">{{ item.title }}<br>' +
                        '<span class="text-light-weight">@ {{ item.institution.short_name }}</span>' +
                    '</h6>' +
                    '<ul class="list-unstyled text-secondary" :class="{soon: item.expiresSoon}">' +
                        '<li v-if="item.internship" class="text-primary "><icon name="info" class="sm"></icon>' +
                            '<strong>Internship</strong></li>' +
                        '<li>' +
                            '<strong v-if="item.isNew" class="new float-right">New</strong>' +
                            '<icon name="today" class="sm"></icon>' +
                            '<span class="deadline">{{ item.deadline | moment }}</span>' +
                        '</li>' +
                        '<li>' +
                            '<icon name="location_on" class="sm"></icon>' +
                            '<span v-if="item.location">{{ item.location }}<span v-if="item.country">, </span></span>' +
                            '<span v-if="item.country">{{ item.country.name }}</span>' +
                        '</li>' +
                        '<li><icon name="how_to_reg" class="sm"></icon><metadata-join :items="item.career_levels"></metadata-join></li>' +
                        '<li><icon name="label" class="sm"></icon><metadata-join :items="item.topics"></metadata-join></li>' +
                    '</ul>' +
                '</div>' +
            '</div>' +
        '</div>' +
    ''
}));

Vue.component('open-jobs-row', {
    data: function () {
        return {
            jobs: null
        }
    },
    props: {
        url: {
            type: String,
            required: true
        },
        title: {
            type: String,
            default: 'Jobs'
        }
    },
    template: '' +
        '<div v-if="jobs && jobs.length" class="row">' +
            '<div class="col-12 col-lg-2">' +
                '<div>' +
                    '<h5 class="display-sm mt-4 mb-1">{{ title }}</h5><hr>' +
                '</div>' +
            '</div>' +
            '<div class="col-12 col-lg-10">' +
                '<job-cards :items="jobs" :ids="ids"></job-cards>' +
            '</div>' +
        '</div>' +
    '',
    methods: {
        fetchData: function () {
            var self = this;
            ajax().get(this.url).done(function (res) {
                self.jobs = Object.freeze(mapper().jobs(res));
            });
        }
    },
    computed: {
        ids: function () {
            if (!this.jobs) return [];
            return _.pluck(this.jobs, 'id');
        }
    },
    created: function () {
        this.fetchData();
    }
});

Vue.component('video-cards', SimpleList.extend({
    props: {
        items: {
            type: Array
        },
        ids: {
            type: Array,
            default: function () {
                return [];
            }
        }
    },
    template: '' +
        '<div v-if="items.length" class="row mini-card-gutters">' +
            '<div v-for="item in items" :key="item.id" class="col-12 col-sm-6 col-md-4 col-lg-3 d-flex align-items-stretch" :v-hide="ids.indexOf(item.id) < 0">' +
                '<div class="hipeac-card mini-card mb-0 inherit d-flex flex-column pointer" @click="updateLocation(item.href, \'_blank\')">' +
                    '<img :src="item.snapshot" class="rounded w-100">' +
                    '<h6 class="title mb-auto">{{ item.title }}</h6>' +
                    '<ul class="list-unstyled text-secondary">' +
                        '<li v-for="user in item.users"><a :href="user.href" @click.stop="updateLocation(user.href)" class="inherit"><i class="material-icons sm">face</i>{{ user.profile.name }}</a></li>' +
                        '<li><i class="material-icons sm">label</i><metadata-join :items="item.topics"></metadata-join></li>' +
                    '</ul>' +
                '</div>' +
            '</div>' +
        '</div>' +
    ''
}));

Vue.component('videos-row', {
    data: function () {
        return {
            videos: null
        }
    },
    props: ['url'],
    template: '' +
        '<div v-if="videos && videos.length" class="row">' +
            '<div class="col-12 col-lg-2">' +
                '<div>' +
                    '<h5 class="display-sm mt-4 mb-1">Videos</h5><hr>' +
                '</div>' +
            '</div>' +
            '<div class="col-12 col-lg-10">' +
                '<video-cards :items="videos" :ids="ids"></video-cards>' +
            '</div>' +
        '</div>' +
    '',
    methods: {
        fetchData: function () {
            var self = this;
            ajax().get(this.url).done(function (res) {
                self.videos = Object.freeze(mapper().videos(res));
            });
        }
    },
    computed: {
        ids: function () {
            if (!this.videos) return [];
            return _.pluck(this.videos, 'id');
        }
    },
    created: function () {
        this.fetchData();
    }
});

Vue.component('skeleton-content', {
    template: '' +
        '<p class="skeleton m-0">' +
            '<span class="text w-100"></span>' +
            '<span class="text w-100"></span>' +
            '<span class="text w-100"></span>' +
            '<span class="text w-100"></span>' +
            '<span class="text w-25"></span>' +
        '</p>' +
    ''
});

Vue.component('skeleton-box', {
    template: '' +
        '<div class="hipeac-card mini-card mb-0 skeleton">' +
            '<span class="text w-100"></span>' +
            '<span class="text w-100"></span>' +
            '<span class="text w-25"></span>' +
        '</div>' +
    ''
});

Vue.component('skeleton-cards', {
    props: {
        number: {
            type: Number,
            default: 8
        }
    },
    template: '' +
        '<div class="row mini-card-gutters skeleton">' +
            '<div v-for="item in skeletons" :key="item" class="col-12 col-sm-6 col-md-4 col-lg-3 d-flex align-items-stretch">' +
                '<div class="hipeac-card mini-card mb-0">' +
                    '<span class="header"></span>' +
                    '<span class="text w-100"></span>' +
                    '<span class="text w-100"></span>' +
                    '<span class="text w-25"></span>' +
                    '<hr>' +
                    '<span class="text sm w-75"></span>' +
                '</div>' +
            '</div>' +
        '</div>' +
    '',
    computed: {
        skeletons: function () {
            return Array.apply(null, {length: this.number}).map(Number.call, Number);
        }
    }
});

Vue.component('skeleton-table', {
    props: {
        rows: {
            type: Number,
            default: 5
        },
        withHeader: {
            type: Boolean,
            default: false
        }
    },
    template: '' +
        '<table class="table skeleton">' +
            '<tbody>' +
                '<tr v-for="item in skeletons" :key="item">' +
                    '<td class="p-1">' +
                        '<span v-if="withHeader" class="text w-75"></span><br v-if="withHeader">' +
                        '<span class="text sm w-100"></span>' +
                    '</td>' +
                '</tr>' +
            '</tbody>' +
        '</table>' +
    '',
    computed: {
        skeletons: function () {
            return Array.apply(null, {length: this.rows}).map(Number.call, Number);
        }
    }
});

Vue.component('user-notifications-button', {
    data: function () {
        return {
            counter: 0
        }
    },
    template: '' +
        '<button v-cloak class="btn text-center px-2" :class="{\'btn-outline-danger\': counter > 0, \'btn-outline-secondary\': counter == 0}" :disabled="counter == 0" @click.prevent="show">' +
            '<i v-if="counter == 0" class="material-icons">notifications_none</i>' +
            '<strong v-else class="text-sm">' +
                '<i class="material-icons">notifications_active</i> {{ counter }}' +
            '</strong>' +
        '</button>' +
    '',
    methods: {
        updateCounter: function (num) {
            this.counter = num;
        },
        show: function () {
            if (this.counter == 0) return;
            EventHub.$emit('show-notifications');
        }
    },
    created: function () {
        EventHub.$on('update-notifications-count', this.updateCounter);
    },
    beforeDestroy: function () {
        EventHub.$off('update-notifications-count');
    }
});

Vue.component('user-notifications', {
    data: function () {
        return {
            notifications: []
        }
    },
    template: '' +
        '<div ref="notificationsModal" class="modal modal-side" tabindex="-1" role="dialog">' +
            '<div v-if="notifications.length" class="modal-dialog modal-dialog-centered modal-md" role="notifications">' +
                '<div class="modal-content">' +
                    '<div class="modal-body">' +
                        '<button type="button" class="close" style="margin-top: -0.4rem;" data-dismiss="modal" aria-label="Close">' +
                            '<span aria-hidden="true">&times;</span>' +
                        '</button>' +
                        '<display-sm class="mb-3">Notifications</display-sm>' +
                        '<table class="table mb-0">' +
                            '<tbody>' +
                                '<tr v-for="noti in notifications" :key="noti.id" @click="goTo(noti.message.path)" class="pointer">' +
                                    '<td class="sm px-0">' +
                                        '<i class="material-icons text-primary">{{ noti.icon }}</i>' +
                                    '</td>' +
                                    '<td>' +
                                        '<marked :text="noti.message.text"></marked>' +
                                    '</td>' +
                                    '<td class="sm px-0 text-light">' +
                                        '<i class="material-icons">arrow_forward_ios</i>' +
                                    '</td>' +
                                '</tr>' +
                            '</tbody>' +
                        '</table>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
    '',
    methods: {
        goTo: function (href) {
            var w = window.open(href, '_self');
            w.focus();
        },
        show: function () {
            $(this.$refs.notificationsModal).modal();
        },
        fetchNotifications: function () {
            var self = this;
            api().getNotifications().done(function (res) {
                self.notifications = Object.freeze(mapper().notifications(res));
                setTimeout(function () {
                    self.fetchNotifications();
                }, 1000 * 20);
            });
        }
    },
    watch: {
        'notifications': function (val) {
            EventHub.$emit('update-notifications-count', val.length);
        }
    },
    created: function () {
        EventHub.$on('show-notifications', this.show);
        this.fetchNotifications();
    },
    beforeDestroy: function () {
        EventHub.$off('show-notifications');
    }
});
