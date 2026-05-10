# Support having plugins as dependencies in shareable config

**Repository:** [eslint/eslint](https://github.com/eslint/eslint)
**Issue:** [eslint/eslint#3458](https://github.com/eslint/eslint/issues/3458)
**Reactions:** 507 👍
**Created:** 2015-08-20T07:09:22Z
**Last Activity:** 2022-09-07T19:56:53Z
**Labels:** backlog, core, needs bikeshedding, evaluating

---

## Original Description

My shareable config uses rules from an external plugin and I would like to make it a `dependency` so the user doesn't have to manually install the plugin manually. I couldn't find any docs on this, but it doesn't seem to work, so I'll assume it's not currently supported.

``` js
module.js:338
    throw err;
          ^
Error: Cannot find module 'eslint-plugin-no-use-extend-native'
    at Function.Module._resolveFilename (module.js:336:15)
    at Function.Module._load (module.js:278:25)
    at Module.require (module.js:365:17)
    at require (module.js:384:17)
    at /usr/local/lib/node_modules/eslint/lib/cli-engine.js:106:26
    at Array.forEach (native)
    at loadPlugins (/usr/local/lib/node_modules/eslint/lib/cli-engine.js:97:21)
    at processText (/usr/local/lib/node_modules/eslint/lib/cli-engine.js:182:5)
    at processFile (/usr/local/lib/node_modules/eslint/lib/cli-engine.js:224:12)
    at /usr/local/lib/node_modules/eslint/lib/cli-engine.js:391:26
```

I assume it's because you only try to load the plugin when the config is finished merging.

Other shareable configs that depend on a plugin [instructs the users](https://github.com/feross/eslint-config-standard#usage) to manually install the plugin too and they [have it in `peerDependencies`](https://github.com/feross/eslint-config-standard/blob/00fabb06f7622e8762d3a657a7c364993b22d0dd/package.json#L15). I find this sub-optimal though and I don't want the users to have to care what plugins my config uses internally.

The whole point of shareable configs is to minimize boilerplate and overhead, so this would be a welcome improvement.
## <bountysource-plugin>

Want to back this issue? **[Post a bounty on it!](https://www.bountysource.com/issues/25976721-support-having-plugins-as-dependencies-in-shareable-config?utm_campaign=plugin&utm_content=tracker%2F282608&utm_medium=issues&utm_source=github)** We accept bounties via [Bountysource](https://www.bountysource.com/?utm_campaign=plugin&utm_content=tracker%2F282608&utm_medium=issues&utm_source=github).
</bountysource-plugin>


---

*Resurrected by Resurrection Bot 🧬*
