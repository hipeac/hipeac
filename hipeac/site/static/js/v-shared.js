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
    template: '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 366" enable-background="new 0 0 512 366" xml:space="preserve"><g id="HiPEAC"><polygon fill-rule="evenodd" clip-rule="evenodd" fill="#0055A4" points="7.502,251.803 34.273,82.29 68.763,82.29 58.552,146.936 98.179,146.936 108.39,82.29 142.88,82.29 116.107,251.803 81.619,251.803 93.453,176.884 53.824,176.884 41.992,251.803"/><path fill-rule="evenodd" clip-rule="evenodd" fill="#0055A4" d="M198.067,361.083l-17.299-109.241h18.717v-36.027h9.637 c26.395,0,35.85-7.721,35.85-38.314l-0.001-21.927c0-23.45-11.597-31.352-32.921-31.352h-22.946l-20.198,127.573h-28.543 l20.198-127.573l-11.219-70.834L457.04,4.665l19.498,123.146c-5.745-3.575-14.338-5.32-26.976-5.32h-10.709 c-21.945,0-28.082,10.775-24.822,31.378l11.306,71.401c2.657,16.755,12.242,27.71,34.183,27.71h10.71 c12.462,0,20.572-1.825,25.093-6.541l10.441,65.92L198.067,361.083z M207.921,192.47h-8.436v-44.901h8.261 c4.993,0,6.542,1.218,6.542,5.394v30.283C214.288,190.207,212.051,192.47,207.921,192.47 M258.164,124.222l0.006,127.549h58.299 v-23.345h-29.062v-31.624h25.006v-22.017l-25.006,0.003l-0.002-27.223h26.949l-0.004-23.344H258.164z M369.118,141.766 l6.908,57.239h-14.175l6.91-57.242L369.118,141.766z M345.021,124.152l-19.309,127.689h29.942l3.716-30.824h19.136l3.723,30.824 h29.94l-19.313-127.689H345.021z M459.115,151.25l2.627,16.586h21.135l5.777,36.48h-21.137l3.152,19.902 c0.61,3.842-1.728,5.413-6.547,5.413c-4.824,0-7.657-1.568-8.267-5.413l-11.559-72.969c-0.605-3.84,1.728-5.414,6.722-5.414 C455.673,145.836,458.507,147.41,459.115,151.25"/><polygon fill-rule="evenodd" clip-rule="evenodd" fill="#FFEE00" points="167.256,82.192 195.735,82.192 191.754,107.327 163.275,107.327"/></g></svg>'
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
    template: '' +
        '<h6 class="display display-sm text-left m-0 mb-3"><span><slot></slot></span></h6>' +
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
