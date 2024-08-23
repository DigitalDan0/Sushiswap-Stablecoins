import React, { useEffect, useRef } from 'react';

const AudioMeter = ({ audioContext, sourceNode }) => {
  const canvasRef = useRef(null);
  const analyzerRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    if (audioContext && sourceNode) {
      analyzerRef.current = audioContext.createAnalyser();
      analyzerRef.current.fftSize = 256;
      sourceNode.connect(analyzerRef.current);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [audioContext, sourceNode]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext('2d');
    const analyzer = analyzerRef.current;

    const draw = () => {
      const bufferLength = analyzer.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      analyzer.getByteFrequencyData(dataArray);

      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
      canvasCtx.fillStyle = 'rgb(0, 0, 0)';
      canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 2.5;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = dataArray[i] / 2;
        canvasCtx.fillStyle = `rgb(${barHeight + 100}, 50, 50)`;
        canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
      }

      animationRef.current = requestAnimationFrame(draw);
    };

    if (analyzer) {
      draw();
    }
  }, []);

  return <canvas ref={canvasRef} width="300" height="100" />;
};

export default AudioMeter;