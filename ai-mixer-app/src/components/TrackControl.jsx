import React, { useState, useEffect, useRef } from 'react';

const TrackControl = ({ trackName, audioContext, audioBuffer }) => {
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  const sourceNodeRef = useRef(null);
  const gainNodeRef = useRef(null);
  const startTimeRef = useRef(0);
  const animationFrameRef = useRef(null);

  useEffect(() => {
    if (audioContext && audioBuffer) {
      gainNodeRef.current = audioContext.createGain();
      gainNodeRef.current.connect(audioContext.destination);
    }
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [audioContext, audioBuffer]);

  useEffect(() => {
    if (gainNodeRef.current) {
      gainNodeRef.current.gain.setValueAtTime(isMuted ? 0 : volume, audioContext.currentTime);
    }
  }, [volume, isMuted, audioContext]);

  const handleVolumeChange = (e) => {
    setVolume(parseFloat(e.target.value));
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const updatePlaybackTime = () => {
    if (isPlaying) {
      setCurrentTime(audioContext.currentTime - startTimeRef.current);
      animationFrameRef.current = requestAnimationFrame(updatePlaybackTime);
    }
  };

  const togglePlayPause = () => {
    if (isPlaying) {
      sourceNodeRef.current.stop();
      setIsPlaying(false);
      cancelAnimationFrame(animationFrameRef.current);
    } else {
      sourceNodeRef.current = audioContext.createBufferSource();
      sourceNodeRef.current.buffer = audioBuffer;
      sourceNodeRef.current.connect(gainNodeRef.current);
      sourceNodeRef.current.start(0, currentTime);
      startTimeRef.current = audioContext.currentTime - currentTime;
      setIsPlaying(true);
      updatePlaybackTime();
    }
  };

  const handleSeek = (e) => {
    const seekTime = parseFloat(e.target.value);
    setCurrentTime(seekTime);
    if (isPlaying) {
      sourceNodeRef.current.stop();
      sourceNodeRef.current = audioContext.createBufferSource();
      sourceNodeRef.current.buffer = audioBuffer;
      sourceNodeRef.current.connect(gainNodeRef.current);
      sourceNodeRef.current.start(0, seekTime);
      startTimeRef.current = audioContext.currentTime - seekTime;
    }
  };

  return (
    <div className="track-control">
      <h3>{trackName}</h3>
      <button onClick={togglePlayPause}>{isPlaying ? 'Pause' : 'Play'}</button>
      <div>
        <input
          type="range"
          min="0"
          max={audioBuffer ? audioBuffer.duration : 100}
          step="0.01"
          value={currentTime}
          onChange={handleSeek}
        />
        <span>{currentTime.toFixed(2)} / {audioBuffer ? audioBuffer.duration.toFixed(2) : '0.00'}</span>
      </div>
      <div>
        <label htmlFor={`${trackName}-volume`}>Volume:</label>
        <input
          type="range"
          id={`${trackName}-volume`}
          min="0"
          max="1"
          step="0.01"
          value={volume}
          onChange={handleVolumeChange}
        />
      </div>
      <button onClick={toggleMute}>{isMuted ? 'Unmute' : 'Mute'}</button>
    </div>
  );
};

export default TrackControl;