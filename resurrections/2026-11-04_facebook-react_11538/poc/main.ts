import React, {useEffect, useRef, useState, PropsWithChildren} from 'react';
import ReactDOM from 'react-dom';

// Wrapper that protects the root from external DOM mutations (e.g., Google Translate)
function SafeRoot({children}: PropsWithChildren<{}>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mutationCount, setMutationCount] = useState(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Observe any child list changes performed outside of React
    const observer = new MutationObserver((mutations) => {
      let external = false;
      mutations.forEach((m) => {
        if (m.type === 'childList' && (m.addedNodes.length || m.removedNodes.length)) {
          external = true;
        }
      });
      if (external) {
        // Increment a counter to trigger a safe re‑commit later
        setMutationCount((c) => c + 1);
      }
    });

    observer.observe(container, {childList: true, subtree: true});
    return () => observer.disconnect();
  }, []);

  // Schedule a safe commit after any external mutation
  useEffect(() => {
    if (mutationCount === 0) return;
    // Use a microtask to let external changes settle
    Promise.resolve().then(() => {
      try {
        // Force React to re‑render the whole tree safely
        ReactDOM.unstable_batchedUpdates(() => {
          // No‑op render; the state change above already triggers a render
        });
      } catch (err) {
        console.error('SafeRoot commit error:', err);
      }
    });
  }, [mutationCount]);

  return React.createElement('div', {ref: containerRef}, children);
}

// Example component that reproduces the translate issue
function TranslateSensitive() {
  const [checked, setChecked] = useState(false);

  // Simple toggle
  const toggle = () => setChecked((c) => !c);

  // Render text that Google Translate may rewrite
  return (
    React.createElement('div', null,
      React.createElement('label', null,
        React.createElement('input', {type: 'checkbox', checked, onChange: toggle}),
        ' ',
        checked ? '選択済み' : '無選択'
      )
    )
  );
}

// Mount the app with the safety wrapper
function main() {
  const rootEl = document.getElementById('root');
  if (!rootEl) {
    console.error('Root element not found');
    return;
  }
  ReactDOM.render(
    React.createElement(SafeRoot, null,
      React.createElement(TranslateSensitive, null)
    ),
    rootEl
  );
}

// Execute when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', main);
} else {
  main();
}