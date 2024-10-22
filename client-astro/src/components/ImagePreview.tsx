// src/components/ImagePreview.jsx
import React from 'react';

const imagesContainer: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  justifyContent: 'center',
  margin: '10px 0',
  gap: '15px',
};

const image: React.CSSProperties = {
  width: '300px',
  height: 'auto', // Maintain aspect ratio
  borderRadius: '10px', // Rounded corners for images
  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)', // Subtle shadow effect
};

const ImagePreview = ({ images }) => {
  return (
    <div style={imagesContainer}>
      {images.map((img, index) => (
        <div key={index}>
          <img src={URL.createObjectURL(img)} alt={`Preview ${index}`} style={image} />
        </div>
      ))}
    </div>
  );
};

export default ImagePreview;