import * as React from 'react';
import * as ReactDOM from 'react-dom';

// Define a simple React component
interface Props {}
interface State {
  inputValue: string;
}

class MyComponent extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      inputValue: '',
    };
  }

  handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ inputValue: event.target.value });
  };

  render() {
    return (
      <div>
        <input
          type="text"
          value={this.state.inputValue}
          onChange={this.handleChange}
        />
        <p>Input value: {this.state.inputValue}</p>
      </div>
    );
  }
}

// Render the component
try {
  ReactDOM.render(<MyComponent />, document.getElementById('root'));
} catch (error) {
  console.error('Error rendering component:', error);
}

// Simulate React Fire by updating the DOM directly
function simulateReactFire() {
  const inputElement = document.querySelector('input') as HTMLInputElement;
  if (inputElement) {
    // Stop reflecting input values in the `value` attribute
    inputElement.removeAttribute('value');
    console.log('Simulated React Fire: removed value attribute');
  }
}

// Call the simulateReactFire function
simulateReactFire();