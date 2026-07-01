# $$slots with conditional/reactive content?

**Repository:** [sveltejs/svelte](https://github.com/sveltejs/svelte)
**Issue:** [sveltejs/svelte#5312](https://github.com/sveltejs/svelte/issues/5312)
**Reactions:** 59 👍
**Created:** 2020-08-26T20:14:19Z
**Last Activity:** 2024-10-29T22:28:59Z
**Labels:** feature request, compiler

---

## Original Description

The new `$$slots` feature (thanks to @tanhauhau) provides information if a slot is loaded/filled or empty.
However this only works with "static" content. As soon as there is a condition `{#if}` or `{#await}` involved the
the output of `$$slots` is not really useful anymore or in case of a named slot a error is thrown.

In case of an unnamed slot in combination with `{#if}` the slot is considered *filled* and `$$slots.default` results to `true`
even if the condition passed to the slot is false. Additionally the fallback wont be rendered.

In case of a named slot value inside a `{#if}`  (example below) the line `<div slot="a">Content</div>` will throw
`ValidationError: Element with a slot='...' attribute must be a child of a component or a descendant of a custom element`

Example (tested with `commit 8adb47401e7f7b420ffabf9752a8236114aaecfc`)

``` svelte
// App.svelte

<script>
    import SlotWrapper from './SlotWrapper.svelte';
    let show = false; 
</script>

<SlotWrapper>
    {#if show}
        <div slot="a">Content</div>  <!-- throws error -->
    {/if}
</SlotWrapper>

<button on:click="{()=> show = !show}">
    { show ? 'Hide' : 'Show' }
</button>

```

``` svelte 
// SlotWrapper.svelte

<script>
    $: console.log('slots', $$slots)    
</script>

<slot name="a">Fallback Content</slot>

```

**The behaviors that I would expect, want and need are:**

1. Properties of `$$slot` are only set to true if the content passed to a slot is renderable.  
2. Conditionally pass content to named slots like in the example above. (but that one is not as important me as the first one)


**Why would I want that?**

One usecase (besides many others) is implicitly setting the state of a component with a slot.

Example: 
I have a Card component that displays data coming from a fetch request. The Card component should have a
`loading` state while it is fetching and go to its `default` state if the data is fetched and rendered.
At the moment the only way i konw of is to explicitly create a `loading` variable, set it to `true` before fetching, set it to `false`
afterwards and pass it down to the  `Card` component. 
This is okay if you have to do it one or twice but not if you have many components with similar structure.

With a properly reactive `$$slots` property this could be much cleaner and could look something like this:

```svelte

// Card.svelte
<script>
  $: loading = !$$slots.default;
</script>

<div class="card" class:loading>
   <slot />
</div>

// App.svelte
// ... script, imports. etc...
<Card>
  {#await fetch(url).then(responseToJSON) then data}
  { data.name }
  {/await}
</Card>
```

Thats it. 
Thanks you for providing such an awesome tool. 


---

*Resurrected by Resurrection Bot 🧬*
