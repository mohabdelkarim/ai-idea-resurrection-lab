import { readFileSync, writeFileSync } from 'fs';
import { resolve } from 'path';

// Simple type representing a React component signature
type ReactComponent<Props = any> = (props: Props) => any;

// Runtime guard to validate that required keys exist on props
function validateProps<Props>(props: Props | undefined, required: (keyof Props)[]): Props {
  if (props === undefined) {
    throw new Error('Props object is undefined.');
  }
  const missing = required.filter((key) => !(key in props));
  if (missing.length > 0) {
    throw new Error(`Missing required prop(s): ${missing.join(', ')}`);
  }
  return props;
}

/**
 * Wrap a React component so that it safely destructures props.
 * The wrapper injects a guard that checks for required keys before
 * delegating to the original component.
 */
function wrapReactComponent<Props>(
  component: ReactComponent<Props>,
  requiredProps: (keyof Props)[] = []
): ReactComponent<Props> {
  return (rawProps: Props | undefined) => {
    try {
      const safeProps = validateProps(rawProps, requiredProps as (keyof Props)[]);
      // Destructure safely after validation
      const result = component(safeProps);
      return result;
    } catch (err) {
      // In dev mode we rethrow to surface the error clearly
      if (process.env.NODE_ENV !== 'production') {
        console.error('Prop validation error:', err);
        throw err;
      }
      // In production we fallback to rendering nothing
      return null;
    }
  };
}

// Example component that expects { items: string[] }
const ListComponent: ReactComponent<{ items: string[] }> = ({ items }) => {
  // Using map safely because items is guaranteed to be an array
  return items.map((item, idx) => `Item ${idx}: ${item}`).join('\n');
};

// Wrap the component with required prop validation
const SafeList = wrapReactComponent(ListComponent, ['items']);

// Simulate Astro's runtime calling the wrapped component
function simulateAstroRender() {
  const goodProps = { items: ['apple', 'banana', 'cherry'] };
  const badProps = { }; // missing items

  console.log('--- Rendering with good props ---');
  console.log(SafeList(goodProps));

  console.log('--- Rendering with bad props (should error) ---');
  try {
    console.log(SafeList(badProps as any));
  } catch (e) {
    console.error('Caught error as expected:', e.message);
  }
}

// Run the simulation when this file is executed directly
if (require.main === module) {
  simulateAstroRender();
}