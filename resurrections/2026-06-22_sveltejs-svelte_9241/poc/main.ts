import { SvelteComponent } from 'svelte';

// Define a test component
class TestComponent extends SvelteComponent {
  private props = {};

  public $prop<T>(defaultValue: T): T {
    // Implementation of $prop rune
    if (!this.props) {
      this.props = {};
    }
    return this.props as T;
  }

  public render() {
    // Render function for testing
    let someProp: string = this.$prop<string>('default');
    let anotherProp: number = this.$prop<number>(123);
    return `<div>someProp: {someProp}, anotherProp: {anotherProp}</div>`;
  }
}

// Create an instance of TestComponent
const testComponent = new TestComponent();

// Test the $prop rune
try {
  console.log(testComponent.$prop<string>('test')); // Should print: test
  console.log(testComponent.$prop<number>(456)); // Should print: 456
} catch (error) {
  console.error(error);
}

// Svelte compiler would handle this differently,
// but for demonstration purposes,
// we're manually handling props here.
class SvelteComponentWithProps extends SvelteComponent {
  public someProp: string;
  public anotherProp: number;

  constructor() {
    super();
    this.someProp = this.$prop<string>('default');
    this.anotherProp = this.$prop<number>(123);
  }

  public render() {
    return `<div>someProp: {this.someProp}, anotherProp: {this.anotherProp}</div>`;
  }
}

// Usage example
const svelteComponentWithProps = new SvelteComponentWithProps();
console.log(svelteComponentWithProps.someProp); // Should print: default
console.log(svelteComponentWithProps.anotherProp); // Should print: 123