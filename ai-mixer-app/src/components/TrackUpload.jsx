import React from 'react';

const TrackUpload = ({ onFileUpload }) => {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log('File selected:', file.name);
      onFileUpload(file);
    }
  };

  return (
    <div className="track-upload">
      <input 
        type="file" 
        onChange={handleFileChange}
        accept="audio/*"
      />
    </div>
  );
};

export default TrackUpload;