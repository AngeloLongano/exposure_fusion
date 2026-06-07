from argparse import ArgumentParser, Namespace
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np

from exposure_fusion_core import fuse_exposures, load_images, load_rgb_float, save_grayscale_image
from exposure_fusion_core.comparison import mean_absolute_error, mean_squared_error
from exposure_fusion_core.io import save_rgb_image
from exposure_fusion_core.visualization import (
    resize_float_image,
    save_comparison_image,
    save_input_pyramids,
    save_ldr_preview,
    save_process_diagram,
    save_weights_preview,
)


def parse_args() -> Namespace:
    parser = ArgumentParser(
        description="Run the Exposure Fusion algorithm on a stack of LDR images.",
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        type=Path,
        help="Input LDR images captured at different exposures.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory where generated artifacts are saved.",
    )
    parser.add_argument(
        "--reference",
        type=Path,
        help="Optional reference image used for visual and numeric comparison.",
    )
    parser.add_argument(
        "--save-ldr",
        action="store_true",
        help="Save the loaded LDR inputs in the output directory.",
    )
    parser.add_argument(
        "--save-weights",
        action="store_true",
        help="Save normalized weight maps for each input image.",
    )
    parser.add_argument(
        "--save-result",
        action="store_true",
        help="Save the final fused image.",
    )
    parser.add_argument(
        "--save-comparison",
        action="store_true",
        help="Save a comparison image with fused result, reference, and difference map.",
    )
    parser.add_argument(
        "--save-pyramids",
        action="store_true",
        help="Save Gaussian and Laplacian pyramid visualizations for each input image.",
    )
    parser.add_argument(
        "--save-process",
        action="store_true",
        help="Save a complete process diagram with inputs, pyramids, weights, and result.",
    )
    parser.add_argument(
        "--only-pyramids",
        action="store_true",
        help="Only generate pyramid visualizations for the input images.",
    )
    parser.add_argument(
        "--only-process",
        action="store_true",
        help="Only generate the complete process diagram.",
    )
    parser.add_argument(
        "--save-all",
        action="store_true",
        help="Save LDR inputs, normalized weights, result, and comparison when possible.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Show the generated result inline when the terminal supports it.",
    )
    return parser.parse_args()


def save_requested_artifacts(
    args: Namespace,
    images: list[np.ndarray],
    result,
    reference: np.ndarray | None,
) -> None:
    save_all = args.save_all
    output_dir = args.output_dir

    if save_all or args.save_ldr:
        ldr_dir = output_dir / "ldr"
        for image, input_path in zip(images, args.inputs):
            save_rgb_image(image, ldr_dir / input_path.name)

    if save_all or args.save_weights:
        weights_dir = output_dir / "weights"
        for weight, input_path in zip(result.normalized_weights, args.inputs):
            save_grayscale_image(weight, weights_dir / f"{input_path.stem}_weight.png")

    if save_all or args.save_result:
        save_rgb_image(result.fused_image, output_dir / "fused_image.jpg")

    if reference is not None and (save_all or args.save_comparison):
        save_comparison_image(
            result.fused_image,
            reference,
            output_dir / "comparison.jpg",
        )

    if args.save_pyramids:
        save_input_pyramids(images, args.inputs, output_dir)

    if args.save_process:
        save_process_diagram(images, args.inputs, result, output_dir / "process_diagram.jpg")


def preview_paths(
    args: Namespace,
    images: list[np.ndarray],
    result,
    reference: np.ndarray | None,
) -> list[Path]:
    args.output_dir.mkdir(parents=True, exist_ok=True)

    paths = []

    ldr_preview_path = args.output_dir / "ldr_preview.jpg"
    save_ldr_preview(images, args.inputs, ldr_preview_path)
    paths.append(ldr_preview_path)

    weights_preview_path = args.output_dir / "weights_preview.jpg"
    save_weights_preview(result.normalized_weights, args.inputs, weights_preview_path)
    paths.append(weights_preview_path)

    if args.save_pyramids:
        paths.extend(save_input_pyramids(images, args.inputs, args.output_dir))

    if args.save_process:
        process_path = args.output_dir / "process_diagram.jpg"
        save_process_diagram(images, args.inputs, result, process_path)
        paths.append(process_path)

    if reference is not None:
        path = args.output_dir / "comparison.jpg"
        save_comparison_image(result.fused_image, reference, path)
        paths.append(path)
        return paths

    path = args.output_dir / "fused_image.jpg"
    save_rgb_image(result.fused_image, path)
    paths.append(path)
    return paths


def show_inline_previews(paths: list[Path]) -> None:
    imgcat = shutil.which("imgcat")
    chafa = shutil.which("chafa")

    print("\nPreview artifacts:")
    for path in paths:
        print(f"- {path}")
    sys.stdout.flush()

    if imgcat is not None:
        for path in paths:
            print(f"\n{path.name}")
            sys.stdout.flush()
            subprocess.run([imgcat, "-W", "100%", str(path)], check=False)
        return

    if chafa is not None:
        for path in paths:
            print(f"\n{path.name}")
            sys.stdout.flush()
            subprocess.run([chafa, str(path)], check=False)
        return

    print("Inline preview unavailable. Open the image paths above for visual inspection.")


def main() -> None:
    args = parse_args()

    images = load_images(args.inputs)

    if args.only_pyramids:
        paths = save_input_pyramids(images, args.inputs, args.output_dir)
        print(f"Inputs: {len(images)}")
        print(f"Output directory: {args.output_dir}")
        print(f"Saved pyramid visualizations: {len(paths)}")
        if args.preview:
            show_inline_previews(paths)
        return

    reference = load_rgb_float(args.reference) if args.reference else None
    if reference is not None and reference.shape != images[0].shape:
        print(
            "Reference image shape differs from inputs; "
            f"resizing {reference.shape[:2]} to {images[0].shape[:2]} for comparison."
        )
        reference = resize_float_image(reference, images[0].shape)

    result = fuse_exposures(images)

    if args.only_process:
        path = args.output_dir / "process_diagram.jpg"
        save_process_diagram(images, args.inputs, result, path)
        print(f"Inputs: {len(images)}")
        print(f"Output directory: {args.output_dir}")
        print(f"Saved process diagram: {path}")
        if args.preview:
            show_inline_previews([path])
        return

    save_requested_artifacts(args, images, result, reference)

    print(f"Inputs: {len(images)}")
    print(f"Output directory: {args.output_dir}")
    print(f"Fused raw range: {result.fused_raw.min():.6f} {result.fused_raw.max():.6f}")
    print(
        "Max normalized-weight sum deviation: "
        f"{np.abs(result.normalized_weights.sum(axis=0) - 1).max():.6e}"
    )

    if reference is not None:
        print(f"MAE vs reference: {mean_absolute_error(result.fused_image, reference):.6f}")
        print(f"MSE vs reference: {mean_squared_error(result.fused_image, reference):.6f}")

    if args.preview:
        show_inline_previews(preview_paths(args, images, result, reference))
