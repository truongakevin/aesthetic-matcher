import React, { useState, useRef } from 'react';
import axios from 'axios';
import ImagePreview from './ImagePreview.tsx';
import FeaturesList from './FeaturesList.tsx';

const ImageUploader = () => {
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [features, setFeatures] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) setSelectedImages(Array.from(files));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);

    const formData = new FormData();
    selectedImages.forEach((image) => formData.append('images', image));

    try {
      const { data } = await axios.post('https://kevinatruong.com/api/flask-am', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setFeatures(data);
    } catch (error) {
      console.error("Error uploading images:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const mainContainer: React.CSSProperties = {
    paddingBottom: '50px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-around',
  };

  const buttonContainer: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  };

  const buttonStyle: React.CSSProperties = {
    fontFamily: 'Rowdies',
    backgroundColor: '#f5d6f5',
    margin: '10px',
    padding: '20px 50px',
    border: 'none',
    borderRadius: '50px',
    cursor: 'pointer',
    color: '#161616',
    fontSize: 28,
  };

  const spinnerContainer: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100px',
  };

  const spinnerStyle: React.CSSProperties = {
    border: '8px solid #616161',
    borderTop: '8px solid #D39DD3',
    borderRadius: '50%',
    width: '60px',
    height: '60px',
    animation: 'spin 1s linear infinite',
  };

  const donateButton: React.CSSProperties = {
    textDecoration: 'none',
    color: '#161616',
    backgroundColor: '#fa7d7d',
    margin: '20px auto',
    width: '200px',
    padding: '10px',
    border: 'none',
    borderRadius: '50px',
    cursor: 'pointer',
    fontSize: 24,
  };

  return (
    <div style={mainContainer}>
    <style>
      {`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}
    </style>
      
    <ImagePreview images={selectedImages} />
    <FeaturesList features={features} />

    {!loading ? (
      <form onSubmit={handleSubmit}>
        <input type="file" multiple accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} ref={fileInputRef}
        />
        <div style={buttonContainer}>
          {features.length === 0 ? (
            <>
              {selectedImages.length > 0 && (
                <button type="submit" style={buttonStyle}>
                  match
                </button>
              )}
              <button type="button" onClick={handleUploadClick} style={buttonStyle}>
                upload
              </button>
            </>
          ) : (
            <button type="button" onClick={() => { setFeatures([]); setSelectedImages([]); handleUploadClick(); }} style={buttonStyle}>
              new upload
            </button>
          )}
        </div>
      </form>
    ) : (
      <div style={spinnerContainer}>
        <div style={spinnerStyle}></div>
      </div>
    )}

    {features.length > 0 && (
      <a
        href="https://ko-fi.com/truongakevin"
        target="_blank"
        rel="noopener noreferrer"
        style={donateButton}
      >
        buy me a beer
      </a>
    )}
</div>
  );
};

export default ImageUploader;