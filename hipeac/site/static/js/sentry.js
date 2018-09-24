Sentry.init({
    dsn: 'https://ca3e62d60cfb404fb5a64bd13e0e162e@sentry.io/291640',
    release: GIT_REV,
    environment: 'production',
    integrations: [new Sentry.Integrations.Vue()],
});

if (USER_ID > 0) {
    Sentry.configureScope(function (scope) {
        scope.setUser({
            id: USER_ID
        });
    });
}
