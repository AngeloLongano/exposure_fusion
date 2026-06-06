from dataclasses import dataclass

import numpy as np
from skimage.transform import pyramid_expand, pyramid_gaussian


@dataclass(frozen=True)
class PyramidConfig:
    downscale: int = 2
    max_layer: int = -1


def build_gaussian_pyramid(
    image: np.ndarray,
    *,
    config: PyramidConfig = PyramidConfig(),
    max_layer: int | None = None,
    channel_axis: int | None = None,
) -> list[np.ndarray]:
    resolved_max_layer = config.max_layer if max_layer is None else max_layer
    return list(
        pyramid_gaussian(
            image,
            max_layer=resolved_max_layer,
            downscale=config.downscale,
            preserve_range=True,
            channel_axis=channel_axis,
        )
    )


def crop_like(image: np.ndarray, reference_shape: tuple[int, ...]) -> np.ndarray:
    slices = tuple(slice(0, size) for size in reference_shape)
    return image[slices]


def build_laplacian_pyramid(
    image: np.ndarray,
    *,
    config: PyramidConfig = PyramidConfig(),
) -> list[np.ndarray]:
    gaussian_levels = build_gaussian_pyramid(image, config=config, channel_axis=-1)
    laplacian_levels: list[np.ndarray] = []

    for level in range(len(gaussian_levels) - 1):
        expanded = pyramid_expand(
            gaussian_levels[level + 1],
            upscale=config.downscale,
            preserve_range=True,
            channel_axis=-1,
        )
        expanded = crop_like(expanded, gaussian_levels[level].shape)
        laplacian_levels.append(gaussian_levels[level] - expanded)

    laplacian_levels.append(gaussian_levels[-1])
    return laplacian_levels


def collapse_laplacian_pyramid(
    laplacian_levels: list[np.ndarray],
    *,
    config: PyramidConfig = PyramidConfig(),
) -> np.ndarray:
    if not laplacian_levels:
        raise ValueError("At least one Laplacian level is required.")

    image = laplacian_levels[-1]

    for level in reversed(laplacian_levels[:-1]):
        image = pyramid_expand(
            image,
            upscale=config.downscale,
            preserve_range=True,
            channel_axis=-1,
        )
        image = crop_like(image, level.shape)
        image = image + level

    return image
