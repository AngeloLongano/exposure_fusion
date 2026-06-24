set shell := ["zsh", "-cu"]

default:
    @just --list

run *args:
    uv run python main.py {{ args }}

fuse output_dir *inputs:
    uv run python main.py --inputs {{ inputs }} --output-dir {{ output_dir }} --save-all

fuse-ref output_dir reference *inputs:
    uv run python main.py --inputs {{ inputs }} --reference {{ reference }} --output-dir {{ output_dir }} --save-all

process output_dir *inputs:
    uv run python main.py --inputs {{ inputs }} --output-dir {{ output_dir }} --only-process --preview

fuse-venice-boat:
    uv run python main.py \
        --inputs images/venice_boat/image1.jpg images/venice_boat/image2.jpg images/venice_boat/image3.jpg \
        --reference images/venice_boat/result.jpg \
        --pyramid-max-layer 8 \
        --output-dir images/venice_boat/out \
        --save-all \
        --preview

process-venice-boat:
    uv run python main.py \
        --inputs images/venice_boat/image1.jpg images/venice_boat/image2.jpg images/venice_boat/image3.jpg \
        --pyramid-max-layer 8 \
        --output-dir images/venice_boat/out \
        --only-process \
        --preview

sweep-venice-boat:
    uv run python -m scripts.sweep_pyramid_layers \
        --inputs images/venice_boat/image1.jpg images/venice_boat/image2.jpg images/venice_boat/image3.jpg \
        --reference images/venice_boat/result.jpg \
        --min-layer 1 \
        --max-layer 12 \
        --include-full \
        --csv images/venice_boat/out/pyramid_layers.csv

fuse-venice-carnival:
    uv run python main.py \
        --inputs images/venice_carnival/A.jpg images/venice_carnival/B.jpg images/venice_carnival/C.jpg \
        --reference images/venice_carnival/result.jpg \
        --pyramid-max-layer 8 \
        --output-dir images/venice_carnival/out \
        --save-all \
        --preview

process-venice-carnival:
    uv run python main.py \
        --inputs images/venice_carnival/A.jpg images/venice_carnival/B.jpg images/venice_carnival/C.jpg \
        --pyramid-max-layer 8 \
        --output-dir images/venice_carnival/out \
        --only-process \
        --preview

sweep-venice-carnival:
    uv run python -m scripts.sweep_pyramid_layers \
        --inputs images/venice_carnival/A.jpg images/venice_carnival/B.jpg images/venice_carnival/C.jpg \
        --reference images/venice_carnival/result.jpg \
        --min-layer 1 \
        --max-layer 12 \
        --include-full \
        --csv images/venice_carnival/out/pyramid_layers.csv

fuse-living-room-window:
    uv run python main.py \
        --inputs images/living_room_window/input_1_dark.jpg images/living_room_window/input_2_medium_dark.jpg images/living_room_window/input_3_medium_bright.jpg images/living_room_window/input_4_bright.jpg \
        --reference images/living_room_window/paper_fused.jpg \
        --pyramid-max-layer 6 \
        --output-dir images/living_room_window/out \
        --save-all \
        --preview

process-living-room-window:
    uv run python main.py \
        --inputs images/living_room_window/input_1_dark.jpg images/living_room_window/input_2_medium_dark.jpg images/living_room_window/input_3_medium_bright.jpg images/living_room_window/input_4_bright.jpg \
        --pyramid-max-layer 6 \
        --output-dir images/living_room_window/out \
        --only-process \
        --preview

sweep-living-room-window:
    uv run python -m scripts.sweep_pyramid_layers \
        --inputs images/living_room_window/input_1_dark.jpg images/living_room_window/input_2_medium_dark.jpg images/living_room_window/input_3_medium_bright.jpg images/living_room_window/input_4_bright.jpg \
        --reference images/living_room_window/paper_fused.jpg \
        --min-layer 1 \
        --max-layer 12 \
        --include-full \
        --csv images/living_room_window/out/pyramid_layers.csv

fuse-iphone-example:
    @echo "immagini troppo grandi da visualizzare a terminale"
    uv run python main.py \
        --inputs images/iphone_example/input_dark.jpg images/iphone_example/input_medium.jpg  images/iphone_example/input_bright.jpg \
        --output-dir images/iphone_example/out \
        --save-all

process-iphone-example:
    @echo "immagini troppo grandi da visualizzare a terminale"
    uv run python main.py \
        --inputs images/iphone_example/input_dark.jpg images/iphone_example/input_medium.jpg  images/iphone_example/input_bright.jpg \
        --output-dir images/iphone_example/out \
        --only-process

fuse-iphone-example-2:
    @echo "immagini troppo grandi da visualizzare a terminale"
    uv run python main.py \
        --inputs images/iphone_example_2/input_dark.jpg images/iphone_example_2/input_medium.jpg  images/iphone_example_2/input_bright.jpg \
        --output-dir images/iphone_example_2/out \
        --reference images/iphone_example_2/original_hdr.jpg \
        --pyramid-max-layer -1 \
        --save-all

process-iphone-example-2:
    @echo "immagini troppo grandi da visualizzare a terminale"
    uv run python main.py \
        --inputs images/iphone_example_2/input_dark.jpg images/iphone_example_2/input_medium.jpg  images/iphone_example_2/input_bright.jpg \
        --pyramid-max-layer -1 \
        --output-dir images/iphone_example_2/out \
        --only-process

sweep-iphone-example-2:
    uv run python -m scripts.sweep_pyramid_layers \
        --inputs images/iphone_example_2/input_dark.jpg images/iphone_example_2/input_medium.jpg images/iphone_example_2/input_bright.jpg \
        --reference images/iphone_example_2/original_hdr.jpg \
        --min-layer 1 \
        --max-layer 12 \
        --include-full \
        --csv images/iphone_example_2/out/pyramid_layers.csv

sweep-all:
    just sweep-venice-boat
    just sweep-venice-carnival
    just sweep-living-room-window
    just sweep-iphone-example-2

pyramids-pyramid-blending:
    uv run python main.py \
        --inputs images/pyramid_blending/image-011.png images/pyramid_blending/image-031.png \
        --output-dir images/pyramid_blending/out \
        --only-pyramids \
        --preview

process-pyramid-blending:
    uv run python main.py \
        --inputs images/pyramid_blending/image-011.png images/pyramid_blending/image-031.png \
        --output-dir images/pyramid_blending/out \
        --only-process \
        --preview

paper-assets:
    just fuse-venice-boat
    just process-venice-boat
    just fuse-venice-carnival
    just process-venice-carnival
    just fuse-living-room-window
    just process-living-room-window
    just process-pyramid-blending

    # The iPhone examples are not included in the paper since they are not as visually interesting as the other examples, but we can still generate the results for them.
    # just fuse-iphone-example
    # just process-iphone-example
    # just fuse-iphone-example-2
    # just process-iphone-example-2

paper-pdf:
    pandoc paper.md --pdf-engine=xelatex -V documentclass=article -V geometry:margin=2.5cm -o paper.pdf

paper:
    just paper-assets
    just paper-pdf
