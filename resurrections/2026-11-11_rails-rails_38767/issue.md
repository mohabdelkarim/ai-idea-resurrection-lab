# [guides] Explain how to use Webpacker for Javascript, or mention it exists

**Repository:** [rails/rails](https://github.com/rails/rails)
**Issue:** [rails/rails#38767](https://github.com/rails/rails/issues/38767)
**Reactions:** 12 👍
**Created:** 2020-03-19T15:18:18Z
**Last Activity:** 2020-09-04T09:51:15Z
**Labels:** docs, stale

---

## Original Description

For now, there is no mention of Webpack in the official guides – neither on edge guides – except for Ruby on Rails 6 release notes and upgrade guide. The documentation of the Webpacker gem is quite good, but a newcomer to Rails wouldn't know at first that he needs to have a look to it.

Specifically, it would be good to have a mention of Webpack in the following guides:
* The Asset Pipeline
* Working with JavaScript in Rails

In case of more than a simple mention, there could be a quite thorough explanation of the current state of the recommended use of the Rails asset pipeline together with Webpack – e.g. use asset pipeline for normal CSS and images, and use Webpack for JS. It would be good also to mention that Turbolinks and UJS are (now) just Yarn packages.

Also, because of Webpack, Rails now depend on having a JS runtime on your computer and Yarn. This is briefly mentionned in the Getting Started guide, section Starting up the Web Server, but it could be more explicit in the Installing Rails part.

---

*Resurrected by Resurrection Bot 🧬*
