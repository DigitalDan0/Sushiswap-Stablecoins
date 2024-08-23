import React, { useState, useEffect } from 'react';
import TrackUpload from './components/TrackUpload';
import TrackControl from './components/TrackControl';

const App = () => {
  const [audioContext, setAudioContext] = useState(null);
  const [tracks, setTracks] = useState({});

  useEffect(() => {
    const context = new (window.AudioContext || window.webkitAudioContext)();
    setAudioContext(context);
  }, []);

  const handleFileUpload = async (file) => {
    if (!audioContext) return;

    try {
      const arrayBuffer = await file.arrayBuffer();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      
      setTracks(prevTracks => ({
        ...prevTracks,
        [file.name]: { buffer: audioBuffer }
      }));
    } catch (error) {
      console.error('Error processing audio file:', error);
    }
  };

  return (
    <div className="app">
      <h1>AI Mixer App</h1>
      <TrackUpload onFileUpload={handleFileUpload} />
      <p>Number of tracks: {Object.keys(tracks).length}</p>
      {Object.entries(tracks).map(([trackName, { buffer }]) => (
        <TrackControl
          key={trackName}
          trackName={trackName}
          audioContext={audioContext}
          audioBuffer={buffer}
        />
      ))}
    </div>
  );
};

export default App;