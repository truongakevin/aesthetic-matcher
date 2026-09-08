import React, { useEffect, useState } from 'react';

interface ImagePreviewProps {
  images: File[];
}

interface Preview {
  name: string;
  url: string;
}

const imagesContainer: React.CSSProperties = {
  display: 'flex', flexWrap: 'wrap', justifyContent: 'center', margin: '10px 0', gap: '10px',
};

const image: React.CSSProperties = {
  height: 'auto', width: '300px', marginBottom: '-10px', borderRadius: '10px',
  boxShadow: '1px 1px 10px -8px var(--text)',
};

const ImagePreview = ({ images }: ImagePreviewProps) => {
  const [previews, setPreviews] = useState<Preview[]>([]);

  useEffect(() => {
    const nextPreviews = images.map((selectedImage) => ({
      name: selectedImage.name,
      url: URL.createObjectURL(selectedImage),
    }));
    setPreviews(nextPreviews);
    return () => nextPreviews.forEach((preview) => URL.revokeObjectURL(preview.url));
  }, [images]);

  return (
    <div style={imagesContainer}>
      {previews.map((preview, index) => (
        <div key={preview.url}>
          <img style={image} src={preview.url} alt={`Preview ${index + 1}: ${preview.name}`} />
        </div>
      ))}
    </div>
  );
};

export default ImagePreview;
