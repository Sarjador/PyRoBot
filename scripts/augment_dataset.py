"""scripts/augment_dataset.py — Aumentación de dataset para YOLO.
FASE 2: Genera variantes de las imágenes para mejorar robustez del OCR
        y detección en diferentes condiciones de luz/contraste.
"""
import os
import random
import shutil
from pathlib import Path
import cv2
import numpy as np
from albumentations import (
    RandomBrightnessContrast,
    GaussNoise,
    ShiftScaleRotate,
    Blur,
    RandomGamma,
    Compose,
)

# Directorios
SCRIPT_DIR = Path(__file__).parent
DATASET_DIR = SCRIPT_DIR.parent / "dataset"
AUG_DIR = DATASET_DIR / "augmented"
TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR   = DATASET_DIR / "val"

# ─── Pipeline de augmentación ─────────────────────────────────────────────────
AUGMENT_PIPELINE = Compose([
    RandomBrightnessContrast(
        brightness_limit=0.25,
        contrast_limit=0.25,
        p=0.6
    ),
    GaussNoise(
        var_limit=(5.0, 30.0),
        mean=0,
        p=0.3
    ),
    ShiftScaleRotate(
        shift_limit=0.05,
        scale_limit=0.1,
        rotate_limit=8,
        border_mode=cv2.BORDER_CONSTANT,
        value=0,
        p=0.4
    ),
    Blur(blur_limit=3, p=0.2),
    RandomGamma(gamma_limit=(80, 120), p=0.3),
])


def augment_image(image_path: Path, output_dir: Path, num_variants: int = 3) -> list:
    """
    Genera `num_variants` variantes aumentadas de una imagen.

    Args:
        image_path: ruta a la imagen original
        output_dir: directorio de salida
        num_variants: número de variantes a generar

    Returns:
        Lista de rutas de las imágenes generadas
    """
    image = cv2.imread(str(image_path))
    if image is None:
        return []

    label_path = image_path.with_suffix(".txt")
    if label_path.exists():
        shutil.copy2(label_path, output_dir / label_path.name)

    output = []
    for i in range(num_variants):
        try:
            augmented = AUGMENT_PIPELINE(image=image)["image"]
            name = f"{image_path.stem}_aug{i}{image_path.suffix}"
            out_path = output_dir / name
            cv2.imwrite(str(out_path), augmented)
            output.append(out_path)
        except Exception as e:
            print(f"[WARN] Augmentation falló para {image_path}: {e}")
            continue

    return output


def augment_directory(source_dir: Path, target_dir: Path, num_variants: int = 3):
    """Procesa todas las imágenes en un directorio."""
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    target_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for image_path in source_dir.rglob("*"):
        if image_path.suffix.lower() in image_extensions:
            results = augment_image(image_path, target_dir, num_variants)
            count += len(results)

    print(f"[OK] Generadas {count} variantes en {target_dir}")
    return count


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Aumentar dataset YOLO")
    parser.add_argument("--source", default=str(TRAIN_DIR), help="Directorio fuente")
    parser.add_argument("--output", default=str(AUG_DIR), help="Directorio de salida")
    parser.add_argument("--variants", type=int, default=3, help="Variantes por imagen")
    args = parser.parse_args()

    print(f"Augmenting {args.source} → {args.output}")
    augment_directory(
        source_dir=Path(args.source),
        target_dir=Path(args.output),
        num_variants=args.variants,
    )
