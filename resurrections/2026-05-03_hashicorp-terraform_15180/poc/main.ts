
import React, { useState, useEffect } from 'react';
import { TerraformConfig, TerraformChange } from './terraform';

interface DiffViewerProps {
  terraformConfig: TerraformConfig;
  changes: TerraformChange[];
}

const DiffViewer: React.FC<DiffViewerProps> = ({ terraformConfig, changes }) => {
  const [diff, setDiff] = useState({});

  useEffect(() => {
    const calculateDiff = async () => {
      const diff = await calculateTerraformDiff(terraformConfig, changes);
      setDiff(diff);
    };
    calculateDiff();
  }, [terraformConfig, changes]);

  return (
    <div>
      {Object.keys(diff).map((key) => (
        <div key={key}>
          <h2>{key}</h2>
          <ul>
            {diff[key].map((change) => (
              <li key={change.type}>
                {change.type === 'add' ? (
                  <span style={{ color: 'green' }}>{change.value}</span>
                ) : change.type === 'remove' ? (
                  <span style={{ color: 'red' }}>{change.value}</span>
                ) : (
                  <span style={{ color: 'yellow' }}>{change.value}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

const calculateTerraformDiff = async (terraformConfig: TerraformConfig, changes: TerraformChange[]) => {
  const diff = {};

  changes.forEach((change) => {
    const { type, value, path } = change;
    const [resource, attribute] = path.split('.');

    if (!diff[resource]) {
      diff[resource] = [];
    }

    diff[resource].push({ type, value, attribute });
  });

  return diff;
};

export default DiffViewer;
