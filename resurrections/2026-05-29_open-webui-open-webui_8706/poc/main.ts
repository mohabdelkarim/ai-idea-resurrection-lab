import { writable, derived } from 'svelte/store';
import { onMount } from 'svelte';
import type { Component } from 'svelte';

interface ThinkBlockProps {
  content: string;
  isExpanded: boolean;
  onToggle: () => void;
}

const ThinkBlock: Component<ThinkBlockProps> = ({ content, isExpanded, onToggle }) => {
  return (
    <div class="think-block">
      <button class="toggle-button" on:click={onToggle}>
        {isExpanded ? 'Collapse' : 'Expand'}
      </button>
      {#if isExpanded}
        <pre class="think-block-content">{content}</pre>
      {/if}
    </div>
  );
};

const App: Component = () => {
  const isExpanded = writable(false);
  const content = writable('<think>Sample thinking process</think>');

  const handleToggle = () => {
    isExpanded.update((expanded) => !expanded);
  };

  return (
    <div>
      <ThinkBlock
        content={$content}
        isExpanded={$isExpanded}
        onToggle={handleToggle}
      />
    </div>
  );
};

// Utility function to render HTML content
function renderHtml(html: string): HTMLElement {
  const div = document.createElement('div');
  div.innerHTML = html;
  return div.firstElementChild as HTMLElement;
}

// Example usage
const htmlContent = '<think>This is a sample <b>thinking</b> process</think>';
const thinkBlockElement = renderHtml(htmlContent);

document.body.appendChild(thinkBlockElement);

// Svelte component usage
import { render } from 'svelte/server';
import App from './App.svelte';

const AppComponent = App;
const { html } = render(AppComponent, {});

document.body.innerHTML = html;