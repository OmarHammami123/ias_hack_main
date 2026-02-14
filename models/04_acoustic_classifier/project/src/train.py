import argparse
import csv
from pathlib import Path

import torch
from torch.utils.data import DataLoader, TensorDataset

from data import create_or_load_splits
from features import (
    LogMelExtractor,
    compute_train_normal_stats,
    manifest_to_patch_tensor,
    save_norm_stats,
)
from model import ConvAutoencoder
from utils import get_device, load_config, resolve_project_paths, save_config, set_seed


def make_loss(loss_name: str):
    name = loss_name.lower()
    if name == "mse":
        return torch.nn.MSELoss()
    if name == "mae":
        return torch.nn.L1Loss()
    raise ValueError(f"Unsupported loss: {loss_name}")


def run_train(config_path: str | None) -> None:
    config = load_config(config_path)
    set_seed(int(config["seed"]))
    paths = resolve_project_paths(config, config_path)
    save_config(config, paths["output_root"] / "resolved_config.yaml")

    manifests = create_or_load_splits(config, paths)

    extractor = LogMelExtractor(config)
    norm_stats = compute_train_normal_stats(manifests.train_normal, extractor)
    norm_stats_path = paths["output_root"] / "norm_stats.json"
    save_norm_stats(norm_stats, norm_stats_path)

    train_x = manifest_to_patch_tensor(manifests.train_normal, extractor, norm_stats)
    val_x = manifest_to_patch_tensor(manifests.val_normal, extractor, norm_stats)

    train_ds = TensorDataset(train_x)
    val_ds = TensorDataset(val_x)

    batch_size = int(config["training"]["batch_size"])
    num_workers = int(config["training"]["num_workers"])
    seed = int(config["seed"])
    g = torch.Generator()
    g.manual_seed(seed)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        drop_last=False,
        generator=g,
    )
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, drop_last=False)

    device = get_device(config["training"]["device"])
    model = ConvAutoencoder().to(device)
    criterion = make_loss(config["training"]["loss"])
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=float(config["training"]["learning_rate"]),
        weight_decay=float(config["training"]["weight_decay"]),
    )

    epochs = int(config["training"]["epochs"])
    patience = int(config["training"]["early_stopping_patience"])
    min_delta = float(config["training"]["min_delta"])
    best_val = float("inf")
    patience_count = 0

    best_ckpt = paths["checkpoints_dir"] / "best.pt"
    last_ckpt = paths["checkpoints_dir"] / "last.pt"
    train_log_path = paths["logs_dir"] / "training_log.csv"

    with open(train_log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "train_loss", "val_loss"])

        for epoch in range(1, epochs + 1):
            model.train()
            train_loss = 0.0
            train_count = 0
            for (x,) in train_loader:
                x = x.to(device)
                optimizer.zero_grad(set_to_none=True)
                y = model(x)
                loss = criterion(y, x)
                loss.backward()
                optimizer.step()
                train_loss += loss.item() * x.size(0)
                train_count += x.size(0)
            train_loss /= max(train_count, 1)

            model.eval()
            val_loss = 0.0
            val_count = 0
            with torch.no_grad():
                for (x,) in val_loader:
                    x = x.to(device)
                    y = model(x)
                    loss = criterion(y, x)
                    val_loss += loss.item() * x.size(0)
                    val_count += x.size(0)
            val_loss /= max(val_count, 1)

            writer.writerow([epoch, f"{train_loss:.8f}", f"{val_loss:.8f}"])
            f.flush()
            print(f"[train] epoch={epoch:03d} train_loss={train_loss:.6f} val_loss={val_loss:.6f}")

            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "val_loss": val_loss,
                },
                last_ckpt,
            )

            if val_loss < (best_val - min_delta):
                best_val = val_loss
                patience_count = 0
                torch.save(
                    {
                        "epoch": epoch,
                        "model_state_dict": model.state_dict(),
                        "val_loss": val_loss,
                    },
                    best_ckpt,
                )
            else:
                patience_count += 1
                if patience_count >= patience:
                    print(f"[train] early stopping at epoch {epoch}")
                    break

    print(f"[train] complete. best_val_loss={best_val:.6f}")
    print(f"[train] best checkpoint: {best_ckpt}")
    print(f"[train] last checkpoint: {last_ckpt}")
    print(f"[train] norm stats: {norm_stats_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=None)
    args = parser.parse_args()
    run_train(args.config)


if __name__ == "__main__":
    main()
