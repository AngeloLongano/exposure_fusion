from argparse import ArgumentParser, Namespace
from pathlib import Path

from exposure_fusion_core import fuse_exposures, load_images, load_rgb_float
from exposure_fusion_core.comparison import mean_absolute_error, mean_squared_error
from exposure_fusion_core.pyramids import PyramidConfig
from exposure_fusion_core.visualization import resize_float_image


def parse_layers(args: Namespace) -> list[int]:
    if args.layers is not None:
        layers = args.layers
    else:
        layers = list(range(args.min_layer, args.max_layer + 1))

    if args.include_full and -1 not in layers:
        layers = [-1, *layers]

    if not layers:
        raise ValueError("At least one pyramid layer must be tested.")

    return layers


def parse_args() -> Namespace:
    parser = ArgumentParser(
        description=(
            "Run Exposure Fusion with different pyramid depths and compare each "
            "result against a reference image."
        ),
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        type=Path,
        help="Input LDR images captured at different exposures.",
    )
    parser.add_argument(
        "--reference",
        required=True,
        type=Path,
        help="Reference image used to compute MAE and MSE.",
    )
    parser.add_argument(
        "--min-layer",
        type=int,
        default=1,
        help="Minimum max_layer value to test when --layers is not provided.",
    )
    parser.add_argument(
        "--max-layer",
        type=int,
        default=12,
        help="Maximum max_layer value to test when --layers is not provided.",
    )
    parser.add_argument(
        "--layers",
        nargs="+",
        type=int,
        help="Explicit max_layer values to test, for example: --layers 4 6 8 10 -1.",
    )
    parser.add_argument(
        "--include-full",
        action="store_true",
        help="Also test max_layer=-1, the full pyramid down to the smallest scale.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Optional path where the metrics table is saved as CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.layers is None and args.min_layer > args.max_layer:
        raise ValueError("--min-layer must be less than or equal to --max-layer.")

    layers = parse_layers(args)
    images = load_images(args.inputs)
    reference = load_rgb_float(args.reference)

    if reference.shape != images[0].shape:
        print(
            "Reference image shape differs from inputs; "
            f"resizing {reference.shape[:2]} to {images[0].shape[:2]} for comparison."
        )
        reference = resize_float_image(reference, images[0].shape)

    rows = []
    for max_layer in layers:
        result = fuse_exposures(
            images,
            pyramid_config=PyramidConfig(max_layer=max_layer),
        )
        rows.append(
            {
                "max_layer": max_layer,
                "levels": len(result.fused_laplacian_pyramid),
                "mae": mean_absolute_error(result.fused_image, reference),
                "mse": mean_squared_error(result.fused_image, reference),
                "raw_min": float(result.fused_raw.min()),
                "raw_max": float(result.fused_raw.max()),
            }
        )

    best_mae = min(rows, key=lambda row: row["mae"])
    best_mse = min(rows, key=lambda row: row["mse"])

    print(f"Inputs: {len(images)}")
    print(f"Reference: {args.reference}")
    print()
    print("max_layer  levels        MAE        MSE    raw_min    raw_max")
    print("---------  ------  ---------  ---------  ---------  ---------")
    for row in rows:
        print(
            f"{row['max_layer']:>9}  "
            f"{row['levels']:>6}  "
            f"{row['mae']:>9.6f}  "
            f"{row['mse']:>9.6f}  "
            f"{row['raw_min']:>9.6f}  "
            f"{row['raw_max']:>9.6f}"
        )

    print()
    print(
        "Best MAE: "
        f"max_layer={best_mae['max_layer']} "
        f"levels={best_mae['levels']} "
        f"mae={best_mae['mae']:.6f}"
    )
    print(
        "Best MSE: "
        f"max_layer={best_mse['max_layer']} "
        f"levels={best_mse['levels']} "
        f"mse={best_mse['mse']:.6f}"
    )

    if args.csv is not None:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", encoding="utf-8") as file:
            file.write("max_layer,levels,mae,mse,raw_min,raw_max\n")
            for row in rows:
                file.write(
                    f"{row['max_layer']},"
                    f"{row['levels']},"
                    f"{row['mae']:.12f},"
                    f"{row['mse']:.12f},"
                    f"{row['raw_min']:.12f},"
                    f"{row['raw_max']:.12f}\n"
                )
        print(f"Saved CSV: {args.csv}")


if __name__ == "__main__":
    main()
