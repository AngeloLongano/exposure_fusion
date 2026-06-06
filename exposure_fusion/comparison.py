import numpy as np


def absolute_difference_map(image: np.ndarray, reference: np.ndarray) -> np.ndarray:
    if image.shape != reference.shape:
        raise ValueError("Image and reference must have the same shape.")

    return np.abs(image - reference).mean(axis=2)


def mean_absolute_error(image: np.ndarray, reference: np.ndarray) -> float:
    return float(absolute_difference_map(image, reference).mean())


def mean_squared_error(image: np.ndarray, reference: np.ndarray) -> float:
    if image.shape != reference.shape:
        raise ValueError("Image and reference must have the same shape.")

    return float(np.mean((image - reference) ** 2))
