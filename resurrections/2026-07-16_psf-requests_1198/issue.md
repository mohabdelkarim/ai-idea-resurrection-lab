# max-retries-exceeded exceptions are confusing

**Repository:** [psf/requests](https://github.com/psf/requests)
**Issue:** [psf/requests#1198](https://github.com/psf/requests/issues/1198)
**Reactions:** 18 👍
**Created:** 2013-02-15T14:59:41Z
**Last Activity:** 2018-12-27T14:25:44Z
**Labels:** Feature Request

---

## Original Description

hi,
for example:

```
>>> requests.get('http://localhost:1111')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "requests/api.py", line 55, in get
    return request('get', url, **kwargs)
  File "requests/api.py", line 44, in request
    return session.request(method=method, url=url, **kwargs)
  File "requests/sessions.py", line 312, in request
    resp = self.send(prep, **send_kwargs)
  File "requests/sessions.py", line 413, in send
    r = adapter.send(request, **kwargs)
  File "requests/adapters.py", line 223, in send
    raise ConnectionError(e)
requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=1111): Max retries exceeded with url: / (Caused by <class 'socket.error'>: [Errno 61] Connection refused)
```

(assuming nothing is listening on port 1111)

the exception says "Max retries exceeded". i found this confusing because i did not specify any retry-related params. in fact, i am unable to find any documentation about specifying the retry-count. after going through the code, it seems that urllib3 is the underlying transport, and it is called with max_retries=0 (so in fact there are no retries). and requests simply wraps the exception. so it is understandable, but it confuses the end-user (end-developer)? i think something better should be done here, especially considering that it is very easy to get this error.


---

*Resurrected by Resurrection Bot 🧬*
