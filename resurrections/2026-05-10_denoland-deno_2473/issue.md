# 1.0

**Repository:** [denoland/deno](https://github.com/denoland/deno)
**Issue:** [denoland/deno#2473](https://github.com/denoland/deno/issues/2473)
**Reactions:** 724 👍
**Created:** 2019-06-07T18:03:22Z
**Last Activity:** 2020-06-27T13:11:32Z
**Labels:** 

---

## Original Description

Update April 15, 2020: Still go for May 13.

Update March 6, 2020: There's a difficult balance to be had between trying to get it right and shipping a usable product. The repository continues to see rapid development and we have yet to make substantial progress on the major missing feature: dev tool support. Therefore we are bumping the release date yet again. However instead of blindly estimating several weeks out, we've discussed it at length and decided 2 months would be enough time. This coincidentally is around the 2 year anniversary since [the first commit](https://github.com/denoland/deno/commit/f7c5e19081920f59ce2006d3255a58fb611b6a17). Therefore **we are setting the date of May 13, 2020 as the 1.0 release date**. Contributors are encouraged to get any major API changes in before April 20 - after that date we will be polishing and bug fixing. Of course the API will continue to evolve and improve after 1.0, but we will be making explicit stability guarantees for some interfaces.

Update Jan 27, 2020: Massive progress is being made, but we still have not yet accomplished the major feature blocker: devtool support. I hate to keep kicking the release date, but we're still looking at some weeks of development. We hope to ship a 1.0 build with stability promises towards end of February.

Update Dec 23, 2019:  There is one major feature we lack that needs to be in 1.0 - that's a way to hook Deno up to Chrome DevTools. Implementing it has induced a rewrite of the bindings to V8 - that work is ongoing https://github.com/denoland/rusty_v8. We want to fork lift Deno onto that system before 1.0 happens. Current estimate for 1.0 is end of January.

- [x] replace libdeno with rusty_v8 https://github.com/denoland/deno/issues/3530
- [x] "deno --debug" https://github.com/denoland/deno/issues/1120 We need to be able to debug using Chrome Devtools. As the deno userland code base grows, it becomes in increasingly painful to work without a debugger. The way this will work is with a websocket server in Rust (port 9229) which forwards messages to V8 (using [V8InspectorClient](https://github.com/denoland/deno_third_party/blob/0761d3cee6dd43c38f676268b496a37527fc9bae/v8/include/v8-inspector.h#L163)). https://github.com/denoland/deno/pull/4484

- [x] Loading and execution of modules (either JS or TS) needs to be correct. This is the main thing we deliver actually, but there are still many bugs: <s>source maps are sometimes incorrect https://github.com/denoland/deno/issues/2390</s>, <s>double downloads happen https://github.com/denoland/deno/issues/2442</s>, the cache needs to be refactored https://github.com/denoland/deno/issues/2057.  

- [X] Import maps. It's a very reasonable standard and we can provide support via a command line flag. This allows bare imports. The feature will land very soon https://github.com/denoland/deno/pull/2360.

- [x] Dynamic import. 50% complete at the time of writing. https://github.com/denoland/deno/issues/1789 

- [

---

*Resurrected by Resurrection Bot 🧬*
