import { SvelteComponent, SvelteElement } from 'svelte';

class Card extends SvelteComponent {
  render() {
    return {
      c() {
        console.log('$$slots', $$slots);
      },
      m(target: HTMLElement, anchor: any) {
        console.log('mounted');
      },
      p() {},
      u() {},
      d(detaching: boolean) {
        console.log('unmounted');
      }
    };
  }
}

// Usage
const card = new Card({
  target: document.body,
  props: {
    // props
  }
});

// App.svelte
class App extends SvelteComponent {
  render() {
    return {
      c() {
        this.$$.fragment = this.$$.fragment || {
          c: () => { console.log('App rendered'); },
          m: (target: HTMLElement, anchor: any) => {
            console.log('App mounted');
          },
          p: () => {},
          u: () => {},
          d: (detaching: boolean) => {
            console.log('App unmounted');
          }
        };
      },
      m(target: HTMLElement, anchor: any) {
        console.log('App mounted');
      },
      p() {},
      u() {},
      d(detaching: boolean) {
        console.log('App unmounted');
      }
    };
  }
}

// SlotWrapper.svelte
class SlotWrapper extends SvelteComponent {
  render() {
    return {
      c() {
        console.log('SlotWrapper rendered');
      },
      m(target: HTMLElement, anchor: any) {
        console.log('SlotWrapper mounted');
      },
      p() {},
      u() {},
      d(detaching: boolean) {
        console.log('SlotWrapper unmounted');
      }
    };
  }
}

// index.ts
import { App } from './App.svelte';
import { SlotWrapper } from './SlotWrapper.svelte';
import { Card } from './Card.svelte';

const app = new App({
  target: document.body,
  props: {
    // props
  }
});

const slotWrapper = new SlotWrapper({
  target: document.body,
  props: {
    // props
  }
});

const card = new Card({
  target: document.body,
  props: {
    // props
  }
});