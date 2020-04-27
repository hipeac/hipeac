Vue.component('institutions-carousel', {
    props: {
        eventName: {
            type: String,
            default: 'carousel-query-sent'
        },
        institutions: {
            type: Array
        },
        targetRoute: {
            type: String,
            default: ''
        }
    },
    template: '' +
        '<div v-if="institutions.length">' +
            '<div ref="carousel" class="carousel-logos">' +
                '<ul>' +
                    '<li v-for="institution in institutions" :key="institution.id">' +
                        '<a @click="emitQuery(institution.short_name)" class="pointer">' +
                            '<span :style="{\'background-image\': \'url( \'+ institution.images.md + \')\' }"></span>' +
                        '</a>' +
                    '</li>' +
                '</ul>' +
            '</div>' +
        '</div>' +
        '<loading v-else></loading>' +
    '',
    methods: {
        emitQuery: function (val) {
            EventHub.$emit(this.eventName, val);
        },
        initCarousel: function () {
            $(this.$refs.carousel).jcarousel({
                auto: 0.001,
                transforms3d: true,
                animation: {
                    duration: 2500,
                    easing: 'linear',
                }
            }).jcarouselAutoscroll({
                interval: 0
            });
        }
    },
    watch: {
        'institutions': function (val, oldVal) {
            if (!oldVal) return;

            setTimeout(function () {
                this.initCarousel();
            }.bind(this), 50);
        }
    },
    mounted: function () {
        if (this.institutions) {
            this.initCarousel();
        }
    }
});
