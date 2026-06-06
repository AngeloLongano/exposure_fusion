from pathlib import Path

import numpy as np
from PIL import Image
from skimage import img_as_float


def load_rgb_float(path: str | Path) -> np.ndarray:
    """Load an image as RGB float values in the [0, 1] range."""
    return img_as_float(np.array(Image.open(path).convert("RGB")))


def load_images(paths: list[str | Path], *, require_same_shape: bool = True) -> list[np.ndarray]:
    """Load multiple RGB images and optionally validate matching dimensions."""
    images = [load_rgb_float(path) for path in paths]

    if not images:
        raise ValueError("At least one input image is required.")

    if require_same_shape:
        shape = images[0].shape
        if any(image.shape != shape for image in images):
            raise ValueError("All input images must have the same shape.")

    return images


def save_rgb_image(image: np.ndarray, path: str | Path) -> None:
    """Save an RGB float image after clipping it to the [0, 1] range."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(image, 0.0, 1.0)
    output = Image.fromarray((clipped * 255).astype(np.uint8))

    if output_path.suffix.lower() in {".jpg", ".jpeg"}:
        output.save(output_path, quality=95, subsampling=0)
    else:
        output.save(output_path)


def save_grayscale_image(image: np.ndarray, path: str | Path) -> None:
    """Save a 2D float image as an 8-bit grayscale image."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(image, 0.0, 1.0)
    Image.fromarray((clipped * 255).astype(np.uint8), mode="L").save(output_path)
