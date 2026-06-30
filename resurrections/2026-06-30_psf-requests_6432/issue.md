# The latest version of requests (2.29.0) does not support urllib3 2.0.0

**Repository:** [psf/requests](https://github.com/psf/requests)
**Issue:** [psf/requests#6432](https://github.com/psf/requests/issues/6432)
**Reactions:** 51 👍
**Created:** 2023-04-26T17:53:09Z
**Last Activity:** 2023-08-12T19:30:38Z
**Labels:** 

---

## Original Description

## The latest version of ``requests`` (``2.29.0``) does not support ``urllib3`` ``2.0.0``

``urllib3`` ``2.0.0`` was just released: https://github.com/urllib3/urllib3/releases/tag/2.0.0

But currently ``requests`` ``2.29.0`` has a range bound on it: ``<1.27 and >=1.21.1`` for ``urllib3``.

If you try to install a package that has ``urllib3==2.0.0`` as a dependency (while using the latest version of ``requests``), there will be errors:

```
<PACKAGE> depends on urllib3==2.0.0
requests 2.29.0 depends on urllib3<1.27 and >=1.21.1
```

Expecting ``requests`` to support the latest version of ``urllib3``.

(For Python 3.7 or newer)


---

*Resurrected by Resurrection Bot 🧬*
