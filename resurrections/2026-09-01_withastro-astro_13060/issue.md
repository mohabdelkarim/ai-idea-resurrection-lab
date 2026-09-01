# Aastro preview doesn't respect vite preview allowedHostnames in astro config

**Repository:** [withastro/astro](https://github.com/withastro/astro)
**Issue:** [withastro/astro#13060](https://github.com/withastro/astro/issues/13060)
**Reactions:** 18 👍
**Created:** 2025-01-24T13:13:51Z
**Last Activity:** 2026-03-09T22:18:08Z
**Labels:** help wanted, - P3: minor bug, good first issue

---

## Original Description

### Astro Info

```block
Astro                    v5.1.9
Node                     v22.6.0
System                   Linux (x64)
Package Manager          pnpm
Output                   static
Adapter                  none
Integrations             @astrojs/starlight
```

### If this issue only occurs in one browser, which browser is a problem?

_No response_

### Describe the Bug

When running astro preview and visiting the site from another device via the hostname I am met with the below message
```
Blocked request. This host ("my-hostname") is not allowed.
To allow this host, add "my-hostname" to `preview.allowedHosts` in vite.config.js.
```

Updating the corresponding part of `astro.config.mjs` (`vite.preview.allowedHosts`) does not work, nor does setting it to true or adding a `vite.config.js` file with this set.

The corresponding property for `astro dev` (`vite.server.allowedHosts`) does work.

Note: not reproducible on stackblitz (probably because it forwards direct to the IP).
Can be done with `pnpm astro create` on the starlight template (unable to check basic template at the moment but suspect it's an issue there too).

astro config:
```js
 export default defineConfig({
   site: "http://my-hostname:54321",
   vite: {
     server: {
       allowedHosts: true,
     },
     preview: {
       allowedHosts: true,
     },
   },
...
```

package.json scripts
```json
    "dev": "astro dev --port 54321 --host",
    "preview": "astro preview --port 54321 --host",
```


### What's the expected result?

astro preview respects astro config `vite.preview.allowedHosts` - when I add `"my-hostname"`/`true` to this setting I am able to visit the site in a browser at `http://my-hostname`

### Link to Minimal Reproducible Example

https://github.com/andrewflbarnes/bug-astro-preview-allowedhosts

```bash
pnpm i
pnpm build
pnpm preview

curl yourhostname:54321
```
```
Blocked request. This host ("yourhostname") is not allowed.
To allow this host, add "yourhostname" to `preview.allowedHosts` in vite.config.js.
```


### Participation

- [ ] I am willing to submit a pull request for this issue.

---

*Resurrected by Resurrection Bot 🧬*
