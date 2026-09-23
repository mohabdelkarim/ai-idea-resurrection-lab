# Easy printing of Requests and Responses, two new utils?

**Repository:** [psf/requests](https://github.com/psf/requests)
**Issue:** [psf/requests#3013](https://github.com/psf/requests/issues/3013)
**Reactions:** 9 👍
**Created:** 2016-02-14T12:25:29Z
**Last Activity:** 2021-09-08T18:00:54Z
**Labels:** Feature Request

---

## Original Description

Several times now I've stumbled over cases where I would like to print the request and response objects as strings to the console. Simply to see when headers and content are sent. Seems more people than I have had this problem: http://stackoverflow.com/questions/20658572/python-requests-print-entire-http-request-raw

My suggestion: add two util methods that print requests and responses according to the HTTP spec. They are fully optional to use, and would not break backwards compatibility:

To be clear, I'm suggesting something link this be added to requests.utils:

``` python
def print_request(req):
    print('HTTP/1.1 {method} {url}\n{headers}\n\n{body}'.format(
        method=req.method,
        url=req.url,
        headers='\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        body=req.body,
    ))

def print_response(res):
    print('HTTP/1.1 {status_code}\n{headers}\n\n{body}'.format(
        status_code=res.status_code,
        headers='\n'.join('{}: {}'.format(k, v) for k, v in res.headers.items()),
        body=res.content,
    ))
```

Is this a good idea?


---

*Resurrected by Resurrection Bot 🧬*
