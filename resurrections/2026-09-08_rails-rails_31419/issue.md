# ActiveStorage: Allow access to backing file from Service API

**Repository:** [rails/rails](https://github.com/rails/rails)
**Issue:** [rails/rails#31419](https://github.com/rails/rails/issues/31419)
**Reactions:** 61 👍
**Created:** 2017-12-12T18:07:45Z
**Last Activity:** 2020-03-31T03:47:40Z
**Labels:** stale, activestorage

---

## Original Description

### Steps to reproduce

Currently with the `ActiveStorage::Service` api you can only get a link through the `url` method which, for most services, gives back a public URL that expires in some timeframe. It would be very useful if there was a `file` method that returned the backing file object from the service so that you have more flexibility in how you can expose those files.

### System configuration
**Rails version**: 5.2.0.beta2


---

*Resurrected by Resurrection Bot 🧬*
