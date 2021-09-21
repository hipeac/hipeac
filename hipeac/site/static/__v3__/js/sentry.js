var DJANGO_VARS = document.querySelector('html').dataset;


Sentry.init({
  dsn: 'https://5b2d2f25df16403cb489cab3213ec892@o124046.ingest.sentry.io/1426084',
  release: DJANGO_VARS.rev,
  environment: 'production',
  integrations: [new Sentry.Integrations.BrowserTracing()],
  tracesSampleRate: 0.2
});

if (+DJANGO_VARS.user > 0) {
  Sentry.configureScope(function (scope) {
    scope.setUser({
      id: +DJANGO_VARS.user
    });
  });
}
