# Exposure Fusion: Study and Implementation

This repository contains the study and **Python** implementation of the **Exposure Fusion** technique, an image fusion algorithm that produces high-quality results without requiring the estimation or mapping of the Camera Response Function (CRF), a typical requirement for traditional High Dynamic Range (HDR) techniques.

***

### 🎯 Project Objective

The main activity focused on faithfully reproducing the algorithm described in the academic paper:

> **"Exposure Fusion"**
> *by Tom Mertens, Jan Kautz, and Frank Van Reeth*

The primary goal was to implement the method in a **Python notebook** (`sample.ipynb`) to analyze each step of the process in detail and verify the algorithm's effectiveness on source images.

***

### 🚀 Getting Started

This project uses `uv` for Python package management and `pyproject.toml` to define dependencies.

1. **Install `uv` (if not already present):**
    To use this project, you first need the `uv` installer.
    *(If you do not have `uv` installed, run:)*

    ```bash
    pip install uv
    ```

    If you want use other way to install uv, visit [uv docs](https://docs.astral.sh/uv/getting-started/installation).

2. **Clone the repository:**

    ```bash
    git clone https://github.com/AngeloLongano/exposure_fusion.git
    cd exposure_fusion
    ```

3. **Create and activate a virtual environment:**
    It is recommended to use `uv` to create the environment.

    ```bash
    # Create the virtual environment (in the .venv folder)
    uv venv
    
    # Activate the environment
    # (macOS/Linux)
    source .venv/bin/activate
    # (Windows)
    # .venv\Scripts\activate
    ```

4. **Install dependencies:**
    The `uv sync` command will read the `pyproject.toml` file and install all necessary packages.

    ```bash
    uv sync
    ```

5. **Run the Notebook:**
    Open the `sample.ipynb` file (e.g., with VS Code or Jupyter Lab) and ensure you select the Python interpreter (kernel) from the newly created `.venv` environment.

***

### ⚙️ Methodology and Technical Details

Exposure Fusion is an image processing method that combines a sequence of images captured at different exposures (Exposure Bracketing) into a single, well-exposed, and high-contrast image.

The implementation is based on the following fundamental steps:

1. **Weight Map Calculation:** A weight map is calculated for each input image based on three key metrics that evaluate the "quality" of the exposure at each pixel:
    * **Contrast:** Favors areas with high local variation.
    * **Saturation:** Rewards vivid and non-faded colors.
    * **Well-Exposedness:** Assigns higher weights to pixels with intermediate intensity values (neither too dark nor too bright), using a Gaussian curve centered at 0.5.

2. **Normalization:** The weight maps are normalized pixel by pixel, ensuring that the sum of weights for each pixel across all images equals 1.

3. **Multi-Scale Fusion (Pyramid Blending):** To avoid visual artifacts (such as halos), the fusion is performed in pyramid space:
    * A **Gaussian Pyramid** is built for each of the (normalized) weight maps.
    * A **Laplacian Pyramid** is built for each of the source images.
    * The Laplacian pyramids of the images are combined (blended) using the Gaussian pyramids of the weights.

4. **Reconstruction (Pyramid Collapse):** The resulting combined Laplacian pyramid is collapsed (summed and upsampled) to reconstruct the final fused image.

#### 🗂️ Core Files

The entire study is presented within the following notebook, which guides the user through loading images, calculating weights, and performing the pyramid-based fusion:

* **[`sample.ipynb`](https://github.com/AngeloLongano/exposure_fusion/blob/main/sample.ipynb):** The Jupyter Notebook containing the Python code, intermediate visualizations (like weight maps), and the final fusion results.

***

### 🏁 Conclusions and Future Work

This project successfully implements the core concepts of the Exposure Fusion paper within a notebook environment.

However, the work is still in a **refinement phase**. Future steps include:

* Testing and optimizing the graphical finishing and touch-ups of the resulting images.
* Refactoring the code to define a single,
