# Better error checking and messages for beginners

**Repository:** [sveltejs/svelte](https://github.com/sveltejs/svelte)
**Issue:** [sveltejs/svelte#1518](https://github.com/sveltejs/svelte/issues/1518)
**Reactions:** 11 👍
**Created:** 2018-05-31T17:31:41Z
**Last Activity:** 2024-09-23T00:56:27Z
**Labels:** feature request

---

## Original Description

We should have better error checking and error messages in dev mode to make it easier to learn and develop in Svelte. IMO this is a must to increase widespread adoption since people trying it out will be frustrated and drop it if they don't understand what is going on within the template.

It's very cool to see what code the template is generating, but it should be a goal that you don't _need_ to understand what is being generated to be successful using Svelte.

For example, when you have `{#each items as item}` in your template and `items` is undefined you get the error `Cannot read property 'length' of undefined`. It would be nicer if the error was `` `items` is undefined in {#each items as item}``. It might even be nicer if we output the lines before and after this from the template into the console all fancy like. Perhaps an Error Framework to make it super easy to understand issues in your app.

Other places for additional error checking:
* undefined/nulls in bind, e.g. `{ person.name }` when `person` is null

What other errors within templates we add better error checking?

---

*Resurrected by Resurrection Bot 🧬*
