Raven.config('https://ca3e62d60cfb404fb5a64bd13e0e162e@sentry.io/291640', {
    release: GIT_REV,
    environment: 'production'
}).install();

if (USER_ID == 0) {
    Raven.setUserContext();
} else {
    Raven.setUserContext({
        id: USER_ID
    });
}
