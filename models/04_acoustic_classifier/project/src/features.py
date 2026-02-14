from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import soundfile as sf
import torch
import torchaudio
import torchaudio.functional as AF
from tqdm import tqdm

from utils import read_json, save_json


class LogMelExtractor:
    def __init__(self, config: Dict):
        fcfg = config["features"]
        self.sample_rate = int(fcfg["sample_rate"])
        self.n_fft = int(fcfg["n_fft"])
        self.hop_length = int(fcfg["hop_length"])
        self.n_mels = int(fcfg["n_mels"])
        self.patch_frames = int(fcfg["patch_frames"])
        self.patch_hop_frames = int(fcfg["patch_hop_frames"])
        self.eps = float(fcfg["eps"])

        self.mel_transform = torchaudio.transforms.MelSpectrogram(
            sample_rate=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=self.n_mels,
            power=2.0,
            center=True,
        )

    def load_waveform(self, filepath: str) -> torch.Tensor:
        # Use soundfile directly for better compatibility
        wav, sr = sf.read(filepath, dtype='float32')
        
        # Convert to tensor and ensure shape is [channels, samples]
        wav = torch.from_numpy(wav.T) if wav.ndim > 1 else torch.from_numpy(wav).unsqueeze(0)
        
        # Convert to mono if stereo
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
        
        # Resample if necessary
        if sr != self.sample_rate:
            wav = AF.resample(wav, sr, self.sample_rate)
        return wav

    def to_log_mel(self, waveform: torch.Tensor) -> torch.Tensor:
        mel = self.mel_transform(waveform).squeeze(0)
        return torch.log(mel + self.eps)

    def file_to_log_mel(self, filepath: str) -> torch.Tensor:
        return self.to_log_mel(self.load_waveform(filepath))

    def log_mel_to_patches(self, log_mel: torch.Tensor) -> torch.Tensor:
        n_mels, n_frames = log_mel.shape
        if n_mels != self.n_mels:
            raise ValueError(f"Expected n_mels={self.n_mels}, got {n_mels}")

        pf = self.patch_frames
        ph = self.patch_hop_frames

        if n_frames < pf:
            pad = pf - n_frames
            log_mel = torch.nn.functional.pad(log_mel, (0, pad), mode="replicate")
            n_frames = log_mel.shape[1]

        starts = list(range(0, n_frames - pf + 1, ph))
        if starts[-1] != n_frames - pf:
            starts.append(n_frames - pf)

        patches = [log_mel[:, s : s + pf].unsqueeze(0) for s in starts]
        return torch.stack(patches, dim=0)  # [num_patches, 1, n_mels, patch_frames]

    def file_to_patches(self, filepath: str) -> torch.Tensor:
        return self.log_mel_to_patches(self.file_to_log_mel(filepath))


def compute_train_normal_stats(train_manifest_csv: str | Path, extractor: LogMelExtractor) -> Dict[str, float]:
    df = pd.read_csv(train_manifest_csv)
    if len(df) == 0:
        raise ValueError("Empty train manifest; cannot compute normalization stats.")

    total_count = 0
    total_sum = 0.0
    total_sq_sum = 0.0

    for filepath in tqdm(df["filepath"].tolist(), desc="[features] fitting normalization"):
        patches = extractor.file_to_patches(filepath)
        arr = patches.numpy().astype(np.float64)
        total_count += arr.size
        total_sum += arr.sum()
        total_sq_sum += (arr ** 2).sum()

    mean = total_sum / total_count
    var = (total_sq_sum / total_count) - (mean**2)
    std = max(np.sqrt(var), 1e-8)
    return {"mean": float(mean), "std": float(std)}


def save_norm_stats(stats: Dict[str, float], out_path: str | Path) -> None:
    save_json(stats, out_path)


def load_norm_stats(stats_path: str | Path) -> Dict[str, float]:
    return read_json(stats_path)


def normalize_patches(patches: torch.Tensor, mean: float, std: float) -> torch.Tensor:
    return (patches - mean) / std


def manifest_to_patch_tensor(
    manifest_csv: str | Path,
    extractor: LogMelExtractor,
    norm_stats: Dict[str, float] | None = None,
) -> torch.Tensor:
    df = pd.read_csv(manifest_csv)
    if len(df) == 0:
        raise ValueError(f"Manifest has no rows: {manifest_csv}")

    all_patches: List[torch.Tensor] = []
    for filepath in tqdm(df["filepath"].tolist(), desc=f"[features] loading {Path(manifest_csv).name}"):
        patches = extractor.file_to_patches(filepath)
        if norm_stats is not None:
            patches = normalize_patches(patches, norm_stats["mean"], norm_stats["std"])
        all_patches.append(patches)
    return torch.cat(all_patches, dim=0)
