# Nestable blueprints

**Repository:** [pallets/flask](https://github.com/pallets/flask)
**Issue:** [pallets/flask#593](https://github.com/pallets/flask/issues/593)
**Reactions:** 54 👍
**Created:** 2012-09-13T13:35:35Z
**Last Activity:** 2021-04-29T00:06:10Z
**Labels:** blueprints

---

## Original Description

I'd like to be able to register "sub-blueprints" using `Blueprint.register_blueprint(*args, **kwargs)`. This would register the nested blueprints with an app when the "parent" is registered with it. All parameters are preserved, other than `url_prefix`, which is handled similarly to in `add_url_rule`. A naíve implementation could look like this:

``` python
class Blueprint(object):
    ...

    def register_blueprint(self, blueprint, **options):
        def deferred(state):
            url_prefix = options.get('url_prefix')
            if url_prefix is None:
                url_prefix = blueprint.url_prefix
            if 'url_prefix' in options:
                del options['url_prefix']

            state.app.register_blueprint(blueprint, url_prefix, **options)
        self.record(deferred)
```


---

*Resurrected by Resurrection Bot 🧬*
