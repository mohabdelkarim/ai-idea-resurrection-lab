import * as React from 'react';

interface FragmentProps {
  children?: React.ReactNode;
  dangerouslySetInnerHTML?: {
    __html: string;
  };
}

const Fragment: React.FC<FragmentProps> = (props) => {
  if (props.dangerouslySetInnerHTML) {
    return React.createElement({
      __html: props.dangerouslySetInnerHTML.__html,
    } as any);
  }

  if (props.children) {
    return <>{props.children}</>;
  }

  return <></>;
};

const App = () => {
  const htmlString = '<span>Hello World</span>';

  return (
    <div>
      <Fragment dangerouslySetInnerHTML={{ __html: htmlString }} />
      <Fragment>{htmlString}</Fragment>
    </div>
  );
};

const root = React.createRoot(document.getElementById('root'));
root.render(<App />);