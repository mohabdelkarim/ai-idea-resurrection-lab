# CSRF protection prevents some webkit users from submitting forms

**Repository:** [rails/rails](https://github.com/rails/rails)
**Issue:** [rails/rails#21948](https://github.com/rails/rails/issues/21948)
**Reactions:** 105 👍
**Created:** 2015-10-13T09:00:15Z
**Last Activity:** 2022-12-22T16:55:42Z
**Labels:** needs feedback, stale

---

## Original Description

Hi,

We've recently been investigating reports from our users that they are unable to submit forms.

Upon investigation it appears that browsers can get in a state where Rail's CSRF (Cross-Site Request Forgery) protection stops the form being submitted.
## To reproduce

It's possible to produce a minimal Rails app which has this problem:

``` bash
rails new csrf-test
cd csrf-test
bundle exec rails generate scaffold Test test:string
bundle exec rake db:migrate
bundle exec rails server
```
#### How to replicate it on mobile Safari (tested on iOS9):
- Load a page containing a form (will be http://localhost:3000/tests/new in this example).
- Quit Safari by double-tap the home button and swipe up.
- Open Safari from the home screen. You should see the same page with the form.
- Submit the form.

You will see the Rails invalid authenticity token error- this is a "The change you wanted was rejected" message in production, or an `ActionController::InvalidAuthenticityToken` in development. I've also made [a video that follows theese steps](https://www.youtube.com/watch?v=bKDu0qMT4HM).
#### How to replicate on Desktop Safari (tested on Safari 9.0 on OSX)
- Go to 'Safari' > 'Preferences...' > 'General' and set 'Safari opens with:' to 'All windows from last session'. 
- Load a page containing a form (will be http://localhost:3000/tests/new in this example).
- Quit Safari (with CMD+Q)
- Open Safari. You should see the same page with the form.
- Submit the form.

This problem seems to happen regardless if:
- the app is served HTTP or HTTPS
- the app's environment is `development` or `production`
- the browser is manually quit by the user, or quit by the OS (to save memory)

I have also been able to replicate on Chrome on Android. I haven't yet been able to replicate it on Chrome and Firefox on OSX using their 'restore tabs' options like I did in Safari. There may be other browsers that are affected.
## What's happening

Looking at the Rails logs, and the cookie submitted by the browser I believe that the browsers are caching the page, but clearing session cookies. This means the form has a `authenticity_token` parameter, but the Rails session cookie has been cleared so has no corresponding `_csrf_token`.

Here is a annotated log showing this:

``` log
# Browser loads the form for the first time
Started GET "/tests/new" for 127.0.0.1 at 2015-10-13 09:23:18 +0100
  ActiveRecord::SchemaMigration Load (0.1ms)  SELECT "schema_migrations".* FROM "schema_migrations"
Processing by TestsController#new as HTML
  Rendered tests/_form.html.erb (37.0ms)
  Rendered tests/new.html.erb within layouts/application (41.4ms)
Completed 200 OK in 256ms (Views: 243.3ms | ActiveRecord: 0.3ms)

# (Asset requests ommited)

# Browser quits, clearing session cookies
# Browser re-opens, reloads the page from cache without doing a request

# Browser posts the form:
Started POST "/tests" for 127.0.0.1 at 2015-10-13 09:23:37 +0100
Processing by TestsController#create as HTML
  Parameters: {"

---

*Resurrected by Resurrection Bot 🧬*
