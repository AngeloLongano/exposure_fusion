from dataclasses import dataclass

import numpy as np

from exposure_fusion_core.pyramids import (
    PyramidConfig,
    build_gaussian_pyramid,
    build_laplacian_pyramid,
    collapse_laplacian_pyramid,
)
from exposure_fusion_core.weights import WeightConfig, compute_weight_maps, normalize_weights


@dataclass
class ExposureFusionResult:
    raw_weights: np.ndarray
    normalized_weights: np.ndarray
    image_laplacian_pyramids: list[list[np.ndarray]]
    weight_gaussian_pyramids: list[list[np.ndarray]]
    fused_laplacian_pyramid: list[np.ndarray]
    fused_raw: np.ndarray
    fused_image: np.ndarray


def validate_images(images: list[np.ndarray]) -> None:
    if not images:
        raise ValueError("At least one input image is required.")

    shape = images[0].shape
    if len(shape) != 3 or shape[2] != 3:
        raise ValueError("Input images must be RGB arrays with shape (height, width, 3).")

    if any(image.shape != shape for image in images):
        raise ValueError("All input images must have the same shape.")


def fuse_exposures(
    images: list[np.ndarray],
    *,
    weight_config: WeightConfig = WeightConfig(),
    pyramid_config: PyramidConfig = PyramidConfig(),
    clip_output: bool = True,
) -> ExposureFusionResult:
    """Fuse a stack of RGB LDR images with multi-scale exposure fusion."""
    validate_images(images)

    raw_weights, normalized_weights = compute_weight_maps(images, config=weight_config)
    image_laplacian_pyramids = [
        build_laplacian_pyramid(image, config=pyramid_config) for image in images
    ]
    num_levels = len(image_laplacian_pyramids[0])

    weight_gaussian_pyramids = [
        build_gaussian_pyramid(
            weight,
            config=pyramid_config,
            max_layer=num_levels - 1,
            channel_axis=None,
        )
        for weight in normalized_weights
    ]

    for level in range(num_levels):
        level_weights = np.stack([pyramid[level] for pyramid in weight_gaussian_pyramids])
        normalized_level_weights = normalize_weights(level_weights, eps=weight_config.eps)

        for image_index, pyramid in enumerate(weight_gaussian_pyramids):
            pyramid[level] = normalized_level_weights[image_index]

    fused_laplacian_pyramid: list[np.ndarray] = []
    for level in range(num_levels):
        fused_level = np.zeros_like(image_laplacian_pyramids[0][level])

        for image_index in range(len(images)):
            weights_at_level = weight_gaussian_pyramids[image_index][level][..., np.newaxis]
            fused_level += weights_at_level * image_laplacian_pyramids[image_index][level]

        fused_laplacian_pyramid.append(fused_level)

    fused_raw = collapse_laplacian_pyramid(fused_laplacian_pyramid, config=pyramid_config)
    fused_image = np.clip(fused_raw, 0.0, 1.0) if clip_output else fused_raw

    return ExposureFusionResult(
        raw_weights=raw_weights,
        normalized_weights=normalized_weights,
        image_laplacian_pyramids=image_laplacian_pyramids,
        weight_gaussian_pyramids=weight_gaussian_pyramids,
        fused_laplacian_pyramid=fused_laplacian_pyramid,
        fused_raw=fused_raw,
        fused_image=fused_image,
    )
