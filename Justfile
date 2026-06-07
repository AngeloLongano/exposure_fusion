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
        --output-dir images/venice_boat/out \
        --save-all \
        --preview

process-venice-boat:
    uv run python main.py \
        --inputs images/venice_boat/image1.jpg images/venice_boat/image2.jpg images/venice_boat/image3.jpg \
        --output-dir images/venice_boat/out \
        --only-process \
        --preview

fuse-venice-carnival:
    uv run python main.py \
        --inputs images/venice_carnival/A.jpg images/venice_carnival/B.jpg images/venice_carnival/C.jpg \
        --reference images/venice_carnival/result.jpg \
        --output-dir images/venice_carnival/out \
        --save-all \
        --preview

process-venice-carnival:
    uv run python main.py \
        --inputs images/venice_carnival/A.jpg images/venice_carnival/B.jpg images/venice_carnival/C.jpg \
        --output-dir images/venice_carnival/out \
        --only-process \
        --preview

fuse-living-room-window:
    uv run python main.py \
        --inputs images/living_room_window/input_1_dark.jpg images/living_room_window/input_2_medium_dark.jpg images/living_room_window/input_3_medium_bright.jpg images/living_room_window/input_4_bright.jpg \
        --reference images/living_room_window/paper_fused.jpg \
        --output-dir images/living_room_window/out \
        --save-all \
        --preview

process-living-room-window:
    uv run python main.py \
        --inputs images/living_room_window/input_1_dark.jpg images/living_room_window/input_2_medium_dark.jpg images/living_room_window/input_3_medium_bright.jpg images/living_room_window/input_4_bright.jpg \
        --output-dir images/living_room_window/out \
        --only-process \
        --preview

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

paper-pdf:
    pandoc paper.md --pdf-engine=xelatex -V documentclass=article -V geometry:margin=2.5cm -o paper.pdf

paper:
    just paper-assets
    just paper-pdf
