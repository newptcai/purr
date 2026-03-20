# Lightweight mock implementation of kittentts to avoid CUDA/torch downloads
# This module provides the same interface as kittentts but with no external dependencies

import numpy as np
from typing import List, Optional


class KittenTTS:
    """Mock KittenTTS class that simulates the real implementation without dependencies."""
    
    def __init__(self, repo_id: str, cache_dir: str = None):
        """Initialize mock TTS engine."""
        self.repo_id = repo_id
        self.cache_dir = cache_dir
        self._available_voices = ["Jasper", "Luna", "Mia", "Ryan"]
    
    @property
    def available_voices(self) -> List[str]:
        """Return list of available voices."""
        return self._available_voices
    
    def generate(
        self,
        text: str,
        voice: str = "Jasper",
        speed: float = 1.0,
        clean_text: bool = True,
    ) -> np.ndarray:
        """Generate mock audio data from text."""
        # Validate voice
        if voice not in self.available_voices:
            raise ValueError(f"Unknown voice: {voice}. Available: {self.available_voices}")
        
        # Return mock audio data - sine wave for deterministic testing
        duration = len(text) * 0.1  # 100ms per character
        sample_rate = 24000
        num_samples = int(duration * sample_rate)
        
        # Generate a simple sine wave
        t = np.linspace(0, duration, num_samples, False)
        frequency = 440  # A4 note
        audio = np.sin(2 * np.pi * frequency * t)
        
        # Apply speed adjustment
        if speed != 1.0:
            # Simple resampling for speed adjustment
            new_length = int(num_samples / speed)
            audio = np.interp(
                np.linspace(0, num_samples - 1, new_length),
                np.arange(num_samples),
                audio
            )
        
        # Convert to float32 and normalize
        return audio.astype(np.float32) * 0.1
    
    def synthesize(self, *args, **kwargs):
        """Alias for generate() for backward compatibility."""
        return self.generate(*args, **kwargs)


def __version__():
    """Mock version function."""
    return "1.0.0-mock"