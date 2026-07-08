# 💡 RFC: SSR

**Repository:** [withastro/astro](https://github.com/withastro/astro)
**Issue:** [withastro/astro#80](https://github.com/withastro/astro/issues/80)
**Reactions:** 54 👍
**Created:** 2021-04-12T05:09:47Z
**Last Activity:** 2022-07-03T15:43:04Z
**Labels:** 

---

## Original Description

Our current intention is to launch Astro as a static site builder. That means all pages are built to static HTML, and no support for dynamic server-side routes. 

But, there seems to be a lot of community interest in supporting dynamic routes & pages. If there's enough interest and anyone willing to help us with an implementation, then I'd love to start putting together an RFC for experimental support. If we put this behind an experimental flag to start, then I don't think it interferes with our "static site builder" launch story.

Anyone interested in helping spec out an RFC? 

#### Some pieces that need discussion / fleshing out:
- Dynamic pages: can we borrow from Next.js's file based routing? `/pages/[id].js`, `/pages/[...id].ks`, etc.
- Dynamic props: how does a page register as dynamic? Something like `getServerSideProps`?
- Deploy targets: In addition to a Node.js server deployment, I really want us to have a good Cloudflare Workers story. SvelteKit too the approach of having different "adapters" for Node, Deno, etc. Could we do the same?

---

*Resurrected by Resurrection Bot 🧬*
