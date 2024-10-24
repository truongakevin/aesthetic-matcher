// src/components/ImagePreview.jsx
import React from 'react';

const imagesContainer: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  justifyContent: 'center',
  margin: '10px 0',
  gap: '10px',
};

const image: React.CSSProperties = {
  height: 'auto',
  width: '300px',
  marginBottom: '-10px',
  borderRadius: '10px',
  boxShadow: '1px 1px 10px -8px var(--text)',
};

const ImagePreview = ({ images }) => {
  return (
    <div style={imagesContainer}>
      {images.map((img, index) => (
        <div key={index}>
          <img style={image} src={URL.createObjectURL(img)} alt={`Preview ${index}`}/>
        </div>
      ))}
    </div>
  );
};

export default ImagePreview;