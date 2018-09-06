var EventHub = new Vue();


var FETCH_WAIT = 250;
var ComponentStore = new Vuex.Store({
    state: {
        options: null,
        metadata: [],
        institutions: [],
        projects: []
    },
    mutations: {
        fetchMetadata: _.debounce(function (state) {
            if (!state.metadata.length) {
                api().getMetadata().then(function (res) {
                    state.metadata = res;
                });
            }
        }, FETCH_WAIT),
        fetchProjects: _.debounce(function (state) {
            if (!state.metadata.length) {
                api().getProjects().then(function (res) {
                    state.projects = res;
                });
            }
        }, FETCH_WAIT),
        setOptions: function (state, options) {
            state.options = options;
        }
    },
    getters: {
        requiredFields: function (state) {
            if (!state.options) return null;
            return _.keys(state.options.actions.POST);
        },
        metadataDict: function (state) {
            return _.indexBy(state.metadata, 'id');
        },
        countries: function (state) {
            if (!state.options || !_.has(state.options.actions.POST, 'country')) return null;
            return state.options.actions.POST.country.choices;
        }
    }
});


Vue.filter('moment', function (date, format) {
    return moment(date).format(format || 'll');
});

Vue.filter('markdown', function (text) {
    return marked(text, {sanitize: true});
});

Vue.component('loading', {
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
            '<a class="nav-link" :href="url"><i class="material-icons">&#xE150;</i> Edit</a>' +
        '</li>' +
    '',
    created: function () {
        var self = this;
        ajax().head(this.url).then(function (res, statusText, request) {
            if (request.status == 200) self.show = true;
        });
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

Vue.component('huge-icon', {
    template: '' +
        '<div class="huge-icon-wrapper">' +
            '<i class="material-icons"><slot></slot></i>' +
        '</div>' +
    ''
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
    props: ['transparent'],
    template: '' +
        '<h6 class="display display-sm text-left m-0 mb-3" :class="{\'transparent\': transparent}"><span><slot></slot></span></h6>' +
    ''
});

Vue.component('catchphrase', {
    template: '' +
        '<h5 class="mb-4 catchphrase"><slot></slot></h5>' +
    ''
});

Vue.component('simple-list', {
    props: ['items', 'prop'],
    template: '' +
        '<table class="table">' +
            '<tbody>' +
                '<tr v-for="item in items" :key="item.id" :item="item">' +
                    '<td>{{ item[prop] }}</td>' +
                '</tr>' +
            '</tbody>' +
        '</table>' +
    ''
});

Vue.component('event-list', {
    props: ['items'],
    template: '' +
        '<table class="table">' +
            '<tbody>' +
                '<tr v-for="item in items" :key="item.id" :item="item">' +
                    '<td>' +
                        '<a :href="item.href">{{ item.city }}<br>' +
                        '{{ item.dates }}, {{ item.city }}, {{ item.country.name }}</a>' +
                    '</td>' +
                '</tr>' +
            '</tbody>' +
        '</table>' +
    ''
});

Vue.component('metadata-list', {
    props: ['items'],
    template: '' +
        '<p class="m-0 text-secondary compact-height">' +
            '<small class="mr-1" v-for="i in items">{{ i.value }}</small>' +
        '</p>' +
    ''
});

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


Vue.component('quotes-carousel', {
    data: function () {
        return {
            interval: 8,  // seconds
            limit: 5,
            quotes: []
        }
    },
    props: ['types'],
    template: '' +
        '<div id="carousel" class="hipeac carousel slide" data-ride="carousel" :data-interval="interval * 1000">' +
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
    '',
    computed: {
        items: function () {
            if (!this.quotes) return [];
            if (!this.types) return _.sample(this.quotes, this.limit);
            var types = this.types.split(',');
            return _.sample(this.quotes.filter(function (obj) {
                return _.contains(types, obj.type);
            }), this.limit);
        }
    },
    created: function () {
        var self = this;
        api().getQuotes().then(function (res) {
            self.quotes = res;
        });
    }
});
