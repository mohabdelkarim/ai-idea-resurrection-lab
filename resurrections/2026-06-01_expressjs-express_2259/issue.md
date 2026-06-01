# promises

**Repository:** [expressjs/express](https://github.com/expressjs/express)
**Issue:** [expressjs/express#2259](https://github.com/expressjs/express/issues/2259)
**Reactions:** 44 👍
**Created:** 2014-07-24T01:27:09Z
**Last Activity:** 2019-02-15T14:13:56Z
**Labels:** discuss, enhancement, 5.x

---

## Original Description

now that promises are going mainstream, i'm trying to think of how to make express more async friendly. an idea is to use promises.
- `next()` now returns a promise
- if middleware returns a promise, that promise is resolved and propagated up `next()`s

``` js
app.use(function (req, res, next) {
  // a promise must be returned, 
  // otherwise the function will be assumed to be synchronous
  return User.get(req.session.userid).then(function (user) {
    req.user = user
  })
  .then(next) // execute all downstream middleware
  .then(function () {
    // send a response after all downstream middleware have executed
    // this is equivalent to koa's "upstream"
    res.send(user)
  })
})
```

Error handlers are now more koa-like:

``` js
app.use(function (req, res, next) {
  return next().catch(function (err) {
    // a custom error handler
    if (res.headerSent) return
    res.statusCode = err.status || 500
    res.send(err.message) 
  })
})

app.use(function (req, res) {
  throw new Error('hahahah')
})
```

Pros:
- it **should** be backwards compatible since you don't have to resolve the promise returned from `next()`
- much easier error handling including `throw`ing
- solves issues shown in https://github.com/visionmedia/express/issues/2255
- no more `fn.length` checking ~_~
- could probably easily upgrade to es7 async functions

Cons:
- promises
- upgrading middleware and supporting both signatures might be a pain in the ass
- probably a lot slower


---

*Resurrected by Resurrection Bot 🧬*
