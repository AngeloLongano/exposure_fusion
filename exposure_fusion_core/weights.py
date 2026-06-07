from dataclasses import dataclass

import numpy as np
from scipy.ndimage import convolve
from skimage.color import rgb2gray


LAPLACIAN_KERNEL = np.array(
    [
        [0.0, 1.0, 0.0],
        [1.0, -4.0, 1.0],
        [0.0, 1.0, 0.0],
    ]
)


@dataclass(frozen=True)
class WeightConfig:
    sigma_exposedness: float = 0.2
    omega_contrast: float = 1.0
    omega_saturation: float = 1.0
    omega_exposedness: float = 1.0
    eps: float = 1e-12


def exposedness_curve(values: np.ndarray, sigma: float = 0.2) -> np.ndarray:
    return np.exp(-((values - 0.5) ** 2) / (2 * sigma**2))


def quality_measures(
    image: np.ndarray,
    *,
    config: WeightConfig = WeightConfig(),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    gray = rgb2gray(image)
    contrast = np.abs(convolve(gray, LAPLACIAN_KERNEL, mode="reflect"))
    saturation = np.std(image, axis=2)
    well_exposedness = np.prod(
        exposedness_curve(image, sigma=config.sigma_exposedness),
        axis=2,
    )
    return contrast, saturation, well_exposedness


def weight_map(image: np.ndarray, *, config: WeightConfig = WeightConfig()) -> np.ndarray:
    contrast, saturation, well_exposedness = quality_measures(image, config=config)
    return (
        contrast**config.omega_contrast
        * saturation**config.omega_saturation
        * well_exposedness**config.omega_exposedness
    )


def normalize_weights(weights: np.ndarray, *, eps: float = 1e-12) -> np.ndarray:
    """Normalize a stack of weight maps so each pixel sums to one."""
    if weights.ndim < 3:
        raise ValueError("Expected weights with shape (num_images, height, width[, ...]).")

    weight_sum = weights.sum(axis=0, keepdims=True)
    uniform = np.full_like(weights, 1.0 / weights.shape[0])
    return np.divide(weights, weight_sum, out=uniform, where=weight_sum > eps)


def compute_weight_maps(
    images: list[np.ndarray],
    *,
    config: WeightConfig = WeightConfig(),
) -> tuple[np.ndarray, np.ndarray]:
    """Return raw and normalized weight maps for a list of RGB images."""
    if not images:
        raise ValueError("At least one input image is required.")

    raw_weights = np.stack([weight_map(image, config=config) for image in images])
    normalized = normalize_weights(raw_weights, eps=config.eps)
    return raw_weights, normalized
