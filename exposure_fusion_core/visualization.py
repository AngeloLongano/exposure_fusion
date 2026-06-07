from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from exposure_fusion_core.pyramids import build_gaussian_pyramid, build_laplacian_pyramid


def normalized_for_display(image: np.ndarray) -> np.ndarray:
    minimum = image.min()
    maximum = image.max()
    if maximum <= minimum:
        return np.zeros_like(image)
    return (image - minimum) / (maximum - minimum)


def rgb_uint8(image: np.ndarray) -> Image.Image:
    clipped = np.clip(image, 0.0, 1.0)
    return Image.fromarray((clipped * 255).astype(np.uint8))


def grayscale_uint8(image: np.ndarray) -> Image.Image:
    clipped = np.clip(image, 0.0, 1.0)
    return Image.fromarray((clipped * 255).astype(np.uint8)).convert("RGB")


def resize_float_image(image: np.ndarray, shape: tuple[int, int, int]) -> np.ndarray:
    target_height, target_width = shape[:2]
    pil_image = rgb_uint8(image)
    resized = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    return np.asarray(resized).astype(np.float64) / 255.0


def laplacian_for_display(level: np.ndarray) -> np.ndarray:
    max_abs = np.max(np.abs(level))
    if max_abs <= 0:
        return np.full_like(level, 0.5)
    return np.clip(0.5 + level / (2 * max_abs), 0.0, 1.0)


def labeled_panel(image: Image.Image, label: str) -> Image.Image:
    image = image.convert("RGB")
    label_height = 28
    panel = Image.new("RGB", (image.width, image.height + label_height), "white")
    panel.paste(image, (0, label_height))

    draw = ImageDraw.Draw(panel)
    draw.text((8, 8), label, fill="black")
    return panel


def resize_to_fit(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    scale = min(max_width / image.width, max_height / image.height)
    width = max(1, round(image.width * scale))
    height = max(1, round(image.height * scale))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def save_horizontal_sheet(panels: list[Image.Image], path: Path) -> None:
    if not panels:
        raise ValueError("At least one panel is required.")

    width = sum(panel.width for panel in panels)
    height = max(panel.height for panel in panels)
    sheet = Image.new("RGB", (width, height), "white")

    x_offset = 0
    for panel in panels:
        sheet.paste(panel, (x_offset, 0))
        x_offset += panel.width

    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, quality=95, subsampling=0)


def pyramid_level_image(
    level: np.ndarray,
    *,
    display_mode: str,
    is_residual: bool = False,
) -> Image.Image:
    if display_mode == "laplacian" and not is_residual:
        display = laplacian_for_display(level)
    else:
        display = np.clip(level, 0.0, 1.0)

    return grayscale_uint8(display) if display.ndim == 2 else rgb_uint8(display)


def pyramid_stack_panel(
    levels: list[np.ndarray],
    *,
    display_mode: str,
    max_levels: int = 5,
) -> Image.Image:
    canvas_width = 300
    canvas_height = 170
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    selected_levels = levels[:max_levels]

    for index, level in enumerate(selected_levels):
        image = pyramid_level_image(
            level,
            display_mode=display_mode,
            is_residual=index == len(levels) - 1,
        )
        max_width = max(22, round(canvas_width * (0.72**index)))
        max_height = max(16, round(canvas_height * (0.72**index)))
        image = resize_to_fit(image, max_width, max_height)

        x = min(canvas_width - image.width, round(index * canvas_width * 0.2))
        y = min(canvas_height - image.height, round(index * canvas_height * 0.22))
        canvas.paste(image, (x, y))
        ImageDraw.Draw(canvas).rectangle(
            [x, y, x + image.width - 1, y + image.height - 1],
            outline="white",
            width=2,
        )

    return canvas


def centered_paste(canvas: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = box
    x = left + (right - left - image.width) // 2
    y = top + (bottom - top - image.height) // 2
    canvas.paste(image, (x, y))


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int]) -> None:
    draw.line([start, end], fill="#222222", width=5)

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = max((dx**2 + dy**2) ** 0.5, 1.0)
    ux = dx / length
    uy = dy / length
    size = 16
    left = (
        end[0] - ux * size - uy * size * 0.55,
        end[1] - uy * size + ux * size * 0.55,
    )
    right = (
        end[0] - ux * size + uy * size * 0.55,
        end[1] - uy * size - ux * size * 0.55,
    )
    draw.polygon([end, left, right], fill="#222222")


def save_process_diagram(
    images: list[np.ndarray],
    input_paths: list[Path],
    result,
    path: Path,
) -> None:
    row_height = 225
    top_margin = 75
    bottom_margin = 70
    width = 1780
    height = top_margin + row_height * len(images) + bottom_margin
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)

    input_box = (70, 100, 290, 260)
    laplacian_box = (370, 95, 670, 265)
    weight_box = (710, 95, 1010, 265)
    plus_center = (1080, top_margin + row_height * len(images) // 2)
    fused_box = (1160, plus_center[1] - 90, 1460, plus_center[1] + 80)
    final_box = (1540, plus_center[1] - 80, 1725, plus_center[1] + 80)

    draw.text((120, 45), "Input Images", fill="#111111")
    draw.text((390, 45), "Image - Laplacian Pyramid", fill="#111111")
    draw.text((720, 45), "Weight Map - Gaussian Pyramid", fill="#111111")
    draw.text((1230, fused_box[1] - 28), "Fused Pyramid", fill="#111111")
    draw.text((1585, final_box[1] - 28), "Final Image", fill="#111111")

    for index, (image, input_path) in enumerate(zip(images, input_paths)):
        y_offset = row_height * index
        row_center = top_margin + y_offset + row_height // 2

        input_image = resize_to_fit(rgb_uint8(image), 220, 160)
        centered_paste(
            canvas,
            input_image,
            (input_box[0], input_box[1] + y_offset, input_box[2], input_box[3] + y_offset),
        )

        laplacian_panel = pyramid_stack_panel(
            result.image_laplacian_pyramids[index],
            display_mode="laplacian",
        )
        centered_paste(
            canvas,
            laplacian_panel,
            (
                laplacian_box[0],
                laplacian_box[1] + y_offset,
                laplacian_box[2],
                laplacian_box[3] + y_offset,
            ),
        )

        weight_panel = pyramid_stack_panel(
            result.weight_gaussian_pyramids[index],
            display_mode="gaussian",
        )
        centered_paste(
            canvas,
            weight_panel,
            (
                weight_box[0],
                weight_box[1] + y_offset,
                weight_box[2],
                weight_box[3] + y_offset,
            ),
        )

        draw.text((80, input_box[3] + y_offset + 8), input_path.name, fill="#333333")
        draw_arrow(draw, (300, row_center), (360, row_center))
        draw.text((682, row_center - 16), "*", fill="#222222")
        draw.line((1018, row_center, plus_center[0] - 22, plus_center[1]), fill="#222222", width=5)

    draw.ellipse(
        (
            plus_center[0] - 20,
            plus_center[1] - 20,
            plus_center[0] + 20,
            plus_center[1] + 20,
        ),
        outline="#222222",
        width=3,
    )
    draw.line(
        (plus_center[0] - 12, plus_center[1], plus_center[0] + 12, plus_center[1]),
        fill="#222222",
        width=3,
    )
    draw.line(
        (plus_center[0], plus_center[1] - 12, plus_center[0], plus_center[1] + 12),
        fill="#222222",
        width=3,
    )

    fused_panel = pyramid_stack_panel(result.fused_laplacian_pyramid, display_mode="laplacian")
    centered_paste(canvas, fused_panel, fused_box)
    draw_arrow(draw, (plus_center[0] + 22, plus_center[1]), (fused_box[0] - 10, plus_center[1]))

    final_image = resize_to_fit(rgb_uint8(result.fused_image), 240, 160)
    final_left = final_box[0]
    centered_paste(canvas, final_image, final_box)
    draw_arrow(draw, (fused_box[2] + 15, plus_center[1]), (final_left - 15, plus_center[1]))

    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, quality=95, subsampling=0)


def save_pyramid_sheet(
    levels: list[np.ndarray],
    path: Path,
    *,
    title: str,
    display_mode: str,
) -> None:
    panels = []

    for index, level in enumerate(levels):
        if display_mode == "laplacian" and index < len(levels) - 1:
            display = laplacian_for_display(level)
        else:
            display = np.clip(level, 0.0, 1.0)

        image = grayscale_uint8(display) if display.ndim == 2 else rgb_uint8(display)
        panels.append(labeled_panel(image, f"{title} L{index} {level.shape[1]}x{level.shape[0]}"))

    save_horizontal_sheet(panels, path)


def save_input_pyramids(
    images: list[np.ndarray],
    input_paths: list[Path],
    output_dir: Path,
) -> list[Path]:
    pyramid_dir = output_dir / "pyramids"
    paths = []

    for image, input_path in zip(images, input_paths):
        gaussian_path = pyramid_dir / f"{input_path.stem}_gaussian_pyramid.jpg"
        laplacian_path = pyramid_dir / f"{input_path.stem}_laplacian_pyramid.jpg"

        save_pyramid_sheet(
            build_gaussian_pyramid(image, channel_axis=-1),
            gaussian_path,
            title=f"{input_path.stem} Gaussian",
            display_mode="gaussian",
        )
        save_pyramid_sheet(
            build_laplacian_pyramid(image),
            laplacian_path,
            title=f"{input_path.stem} Laplacian",
            display_mode="laplacian",
        )

        paths.extend([gaussian_path, laplacian_path])

    return paths


def save_comparison_image(
    fused_image: np.ndarray,
    reference: np.ndarray,
    path: Path,
) -> None:
    difference = np.abs(fused_image - reference).mean(axis=2)
    difference_display = normalized_for_display(difference)

    save_horizontal_sheet(
        [
            labeled_panel(rgb_uint8(fused_image), "Exposure Fusion"),
            labeled_panel(rgb_uint8(reference), "Reference"),
            labeled_panel(grayscale_uint8(difference_display), "Absolute difference"),
        ],
        path,
    )


def save_ldr_preview(
    images: list[np.ndarray],
    input_paths: list[Path],
    path: Path,
) -> None:
    save_horizontal_sheet(
        [
            labeled_panel(rgb_uint8(image), f"LDR {input_path.name}")
            for image, input_path in zip(images, input_paths)
        ],
        path,
    )


def save_weights_preview(
    normalized_weights: np.ndarray,
    input_paths: list[Path],
    path: Path,
) -> None:
    save_horizontal_sheet(
        [
            labeled_panel(grayscale_uint8(weight), f"Weight {input_path.stem}")
            for weight, input_path in zip(normalized_weights, input_paths)
        ],
        path,
    )
