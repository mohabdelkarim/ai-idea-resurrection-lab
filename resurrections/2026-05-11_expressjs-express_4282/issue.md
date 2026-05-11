# Dependencies (5.0)

**Repository:** [expressjs/express](https://github.com/expressjs/express)
**Issue:** [expressjs/express#4282](https://github.com/expressjs/express/issues/4282)
**Reactions:** 57 👍
**Created:** 2020-05-16T09:47:16Z
**Last Activity:** 2025-01-11T18:01:33Z
**Labels:** ideas

---

## Original Description

It seems that we can remove a few dependencies before the `5.0` release:

- `methods` - We can use the built-in `http` module:

```javascript
const { METHODS } = require("http");
const methods = METHODS.map((method) => method.toLowerCase());
```

- `path-is-absolute` - We can use the built-in `path` module:

```javascript
const path = require("path");
const isAbsolute = path.isAbsolute("some-path");
```

- `safe-buffer` - We can use the built-in `Buffer`:

```javascript
const a = Buffer.from("something");
```

- `setprototypeof` - We can use the `Object.setPrototypeOf()`

```javascript
Object.setPrototypeOf(this.request, parent.request);
```

- `utils-merge` - We can use the spread operator:

```javascript
const opts = { expires: new Date(1), path: '/' , ...options};
```

---

*Resurrected by Resurrection Bot 🧬*
