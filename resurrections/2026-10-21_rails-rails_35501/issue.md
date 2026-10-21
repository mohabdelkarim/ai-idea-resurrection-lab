# Actioncable Webpacker compilation issues with Rails 6 in production

**Repository:** [rails/rails](https://github.com/rails/rails)
**Issue:** [rails/rails#35501](https://github.com/rails/rails/issues/35501)
**Reactions:** 21 👍
**Created:** 2019-03-06T18:10:59Z
**Last Activity:** 2020-12-11T16:41:48Z
**Labels:** stale

---

## Original Description

### Steps to reproduce
1. Generate a new rails 6 app (`rails new myapp`) with all the defaults
1. Generate a new channel `bin/rails g channel test`
1. Boot the app in development to confirm the websocket is connecting as expected
1. Deploy the app to Heroku

### Expected behavior
The websocket connection is successful and there are no console errors

### Actual behavior
Console error `Uncaught TypeError: r is not a function` in action_cable.js.
In my source map the error points to the following line https://github.com/rails/rails/blob/master/actioncable/app/assets/javascripts/action_cable.js#L21

### My Theories

It seems that webpacker compiles this file incorrectly (only in production) and doesn't seem to like that the variable is named `_typeof`. I can see there are distinct differences in how the file is compiled in production vs dev (these differences cause dev to work and prod to throw the aforementioned error)

If I revert back to the yarn package `actioncable` vs `@rails/actioncable` and I revert my `consumer.js` file to use the old import syntax, everything works fine.

Things I already tried to fix this:

1. Ensure the node version between dev and production were identical (I am currently running node 11.x)
1. Ensuring my actioncable (and other rails packages) were correctly set to their beta2 versions.
1. Upgraded my webpacker version to the latest release in the Gemfile and the latest yarn package in package.json

If my bug is accurate, it stands to reason that perhaps it is not possible to deploy Rails 6 with actioncable in a production environment with the default generated files. I am curious if anyone has shipped a working actioncable feature on a brand new Rails 6 beta2 project with the default files and generators.

### System configuration
**Rails version:** 6.0.0.beta2
**Ruby version:** 2.6.1

---

*Resurrected by Resurrection Bot 🧬*
