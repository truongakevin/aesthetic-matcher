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
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
		height: '100%',
  };
  
  const buttonContainer: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    margin: '0 0 75px 0',
  };

  const button: React.CSSProperties = {
    fontFamily: 'Rowdies',
    backgroundColor: 'var(--secondary)',
    margin: '10px',
    padding: '20px 50px',
    border: 'none',
    borderRadius: '50px',
    cursor: 'pointer',
    color: 'var(--background)',
    fontSize: 28,
  };

  const spinnerContainer: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100px',
    margin: '25px 0 100px 0',
  };

  const spinner: React.CSSProperties = {
    border: '8px solid var(--secondary)',
    borderTop: '8px solid var(--primary)',
    borderRadius: '50%',
    width: '60px',
    height: '60px',
    animation: 'spin 1s linear infinite',
  };

  const donateButton: React.CSSProperties = {
    textDecoration: 'none',
    backgroundColor: '#ff9c9c',
    margin: '20px auto',
    padding: '10px 20px',
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

    {features.length > 0 && (
      <FeaturesList features={features} />
    )}

    {!loading ? (
      <form onSubmit={handleSubmit}>
        <input type="file" multiple accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} ref={fileInputRef}
        />
        <div style={buttonContainer}>
          {features.length === 0 ? (
            <>
              {selectedImages.length > 0 && (
                <button type="submit" style={button}>
                  match
                </button>
              )}
              <button type="button" onClick={handleUploadClick} style={button}>
                upload
              </button>
            </>
          ) : (
            <>
              <button type="button" onClick={() => { setFeatures([]); setSelectedImages([]); handleUploadClick(); }} style={button}>
                new upload
              </button>
              <a href="https://ko-fi.com/truongakevin" target="_blank" rel="noopener noreferrer" style={{ ...button, ...donateButton }} >
                buy me a beer
              </a>
            </>
          )}
        </div>
      </form>
    ) : (
      <div style={spinnerContainer}>
        <div style={spinner}></div>
      </div>
    )}
</div>
  );
};

export default ImageUploader;