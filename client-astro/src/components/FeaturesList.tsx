// src/components/FeaturesList.jsx
import React from 'react';

const featuresContainer: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  justifyContent: 'center',
  margin: '20px 0',
  gap: '10px',
  alignItems: 'center',
  fontSize: '.75em',
};

const featureContainer: React.CSSProperties = {
  width: '85%',
  display: 'flex',
  justifyContent: 'space-between',
  backgroundColor: '#d0c2d1',
  borderRadius: '10px',
  padding: '8px 15px',
  alignItems: 'center',
};

const featureLink: React.CSSProperties = {
  textDecoration: 'none',
  textAlign: 'left',
}

const featureName: React.CSSProperties = {
  color: '#161616',
};

const featureProbability: React.CSSProperties = {
  color: '#616161',
};

const FeaturesList = ({ features }) => {
  return (
    <div style={featuresContainer}>
        {features.map((item, index) => (
          <div key={index} style={featureContainer}>
          <a style={featureLink} href={`https://aesthetics.fandom.com/wiki/${(item.feature).replace(/\s+/g, '_')}`} target="_blank" rel="noopener noreferrer">
                <span style={featureName}>{item.feature.toLowerCase()}</span>
          </a>
                <span style={featureProbability}>{item.probability}%</span>
          </div>
        ))}
    </div>
  );
};

export default FeaturesList;
// `https://aesthetics.fandom.com/wiki/${(item.feature).replace(/\s+/g, '_')}`