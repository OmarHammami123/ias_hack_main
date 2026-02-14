import torch
import torch.nn as nn


class ConvAutoencoder(nn.Module):
    """
    Fully-connected autoencoder for acoustic anomaly detection.
    
    Architecture from the research paper:
    Encoder: FC(Input, 64, ReLU) → FC(64, 64, ReLU) → FC(64, 8, ReLU)
    Decoder: FC(8, 64, ReLU) → FC(64, 64, ReLU) → FC(64, Output, none)
    
    The input spectrogram is flattened before encoding and reshaped after decoding.
    """
    def __init__(self, input_dim: int = 64 * 64) -> None:
        """
        Args:
            input_dim: Flattened input dimension (default: n_mels * patch_frames = 64 * 64)
        """
        super().__init__()
        self.input_dim = input_dim
        
        # Encoder: Input → 64 → 64 → 8
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 8),
            nn.ReLU(inplace=True),
        )
        
        # Decoder: 8 → 64 → 64 → Output (no activation on final layer)
        self.decoder = nn.Sequential(
            nn.Linear(8, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, input_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor of shape [batch, 1, n_mels, frames]
        
        Returns:
            Reconstructed tensor of shape [batch, 1, n_mels, frames]
        """
        batch_size = x.shape[0]
        original_shape = x.shape
        
        # Flatten: [batch, 1, n_mels, frames] → [batch, n_mels * frames]
        x_flat = x.view(batch_size, -1)
        
        # Encode and decode
        z = self.encoder(x_flat)
        x_recon_flat = self.decoder(z)
        
        # Reshape back: [batch, n_mels * frames] → [batch, 1, n_mels, frames]
        x_recon = x_recon_flat.view(original_shape)
        
        return x_recon
