import React, { useRef, useState } from 'react';
import axios from 'axios';
import FeaturesList from './FeaturesList.tsx';
import ImagePreview from './ImagePreview.tsx';

const API_URL = import.meta.env.PUBLIC_IMAGE_ANALYSIS_URL
  ?? 'https://kevinatruong.com/api/image-analysis/am';
const MAX_IMAGES = 5;
const MAX_TOTAL_BYTES = 25 * 1024 * 1024;

interface AestheticMatch { feature: string; probability: number; }
interface ErrorResponse { error?: string; }

function validateFiles(files: File[]) {
  if (files.length === 0) return 'Choose at least one image.';
  if (files.length > MAX_IMAGES) return `Choose no more than ${MAX_IMAGES} images at a time.`;
  if (files.some((file) => !file.type.startsWith('image/'))) return 'Every selected file must be an image.';
  if (files.reduce((total, file) => total + file.size, 0) > MAX_TOTAL_BYTES) {
    return 'The selected images must be under 25 MB combined.';
  }
  return null;
}

const ImageUploader = () => {
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [features, setFeatures] = useState<AestheticMatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? []);
    const validationError = validateFiles(files);
    setError(validationError);
    setFeatures([]);
    setSelectedImages(validationError ? [] : files);
    if (validationError) event.target.value = '';
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const validationError = validateFiles(selectedImages);
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);
    const formData = new FormData();
    selectedImages.forEach((selectedImage) => formData.append('images', selectedImage));

    try {
      const { data } = await axios.post<AestheticMatch[]>(API_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setFeatures(data);
    } catch (caughtError) {
      const responseData = axios.isAxiosError<ErrorResponse>(caughtError)
        ? caughtError.response?.data
        : null;
      setError(responseData?.error ?? 'The matcher is unavailable right now. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadClick = () => fileInputRef.current?.click();
  const mainContainer: React.CSSProperties = {
    display: 'flex', flexDirection: 'column', justifyContent: 'space-between', height: '100%',
  };
  const buttonContainer: React.CSSProperties = {
    display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '0 0 75px 0',
  };
  const button: React.CSSProperties = {
    fontFamily: 'Rowdies', backgroundColor: 'var(--secondary)', margin: '10px', padding: '20px 50px',
    border: 'none', borderRadius: '50px', cursor: 'pointer', color: 'var(--background)', fontSize: 28,
  };
  const spinnerContainer: React.CSSProperties = {
    display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100px', margin: '25px 0 100px 0',
  };
  const spinner: React.CSSProperties = {
    border: '8px solid var(--secondary)', borderTop: '8px solid var(--primary)', borderRadius: '50%',
    width: '60px', height: '60px', animation: 'spin 1s linear infinite',
  };
  const donateButton: React.CSSProperties = {
    textDecoration: 'none', backgroundColor: '#ff9c9c', margin: '20px auto', padding: '10px 20px', fontSize: 24,
  };

  return (
    <div style={mainContainer}>
      <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      <ImagePreview images={selectedImages} />
      {features.length > 0 && <FeaturesList features={features} />}
      {error && <p role="alert" style={{ color: '#ffb4b4', fontSize: '.5em', margin: '20px' }}>{error}</p>}

      {!loading ? (
        <form onSubmit={handleSubmit}>
          <input type="file" multiple accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} ref={fileInputRef} />
          <div style={buttonContainer}>
            {features.length === 0 ? (
              <>
                {selectedImages.length > 0 && <button type="submit" style={button}>match</button>}
                <button type="button" onClick={handleUploadClick} style={button}>upload</button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => { setFeatures([]); setSelectedImages([]); setError(null); handleUploadClick(); }}
                  style={button}
                >
                  new upload
                </button>
                <a href="https://ko-fi.com/truongakevin" target="_blank" rel="noopener noreferrer" style={{ ...button, ...donateButton }}>
                  buy me a beer
                </a>
              </>
            )}
          </div>
        </form>
      ) : (
        <div style={spinnerContainer} role="status" aria-label="Matching images"><div style={spinner}></div></div>
      )}
    </div>
  );
};

export default ImageUploader;
