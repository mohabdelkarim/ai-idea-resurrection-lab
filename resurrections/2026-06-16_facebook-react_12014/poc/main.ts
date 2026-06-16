import * as React from 'react';

interface Props {
  children?: React.ReactNode;
  dangerouslySetInnerHTML?: {
    __html: string;
  };
}

const Fragment: React.FC<Props> = (props) => {
  if (props.dangerouslySetInnerHTML) {
    return React.createElement({
      __html: props.dangerouslySetInnerHTML.__html
    });
  }

  if (props.children) {
    return React.Fragment(props.children);
  }

  return null;
};

const App = () => {
  const html = '<span>Hello World</span>';

  return (
    <div>
      <Fragment dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
};

const root = React.createRoot(document.getElementById('root'));
root.render(<App />);