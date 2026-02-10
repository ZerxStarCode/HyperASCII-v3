# ZerxStar HyperASCII v3.0: Scientific Edition

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-orange)
![Version](https://img.shields.io/badge/version-3.0.0-purple)

> **A high-fidelity ASCII art rendering engine featuring chromatic interpolation, Lanczos resampling, and real-time event gating.**

---

## Table of Contents
1. [Abstract](#abstract)
2. [Technical Architecture](#technical-architecture)
3. [Mathematical Principles](#mathematical-principles)
4. [Installation](#installation)
5. [Usage Guide](#usage-guide)
6. [Roadmap](#roadmap)

---

## Abstract

HyperASCII v3.0 is designed to bridge the gap between raster graphics and text-based representation. Unlike traditional ASCII generators that rely on simple nearest-neighbor sampling, this engine implements **signal processing techniques** to preserve high-frequency spatial details. It introduces a **Chromatic Module** capable of reconstructing the original color spectrum of an image within an HTML environment using linear algebra for color mapping.

---

## Technical Architecture

### 1. Rendering Engine (Signal Processing)
* **Lanczos Resampling Kernel:** Instead of bilinear filtering, the engine utilizes Lanczos functions (sinc-based) for image resizing. This minimizes aliasing artifacts and preserves edge definition in low-resolution outputs.
* **Geometric Correction ($\phi = 0.55$):** Implements a mathematical adjustment factor to compensate for the non-square aspect ratio of standard monospace fonts (Courier, Consolas), preventing vertical distortion.
* **Density Mapping:** Features 4 preset quantization algorithms plus support for custom character sets (signatures).

### 2. Chromatic Module (Vector Color Space)
* **Linear Interpolation (Lerp):** The engine calculates the precise hexadecimal color for each character character by interpolating between two user-defined vector points (Dark/Light) based on pixel luminance ($L$).
* **HTML Export:** Generates standalone `.html` artifacts with embedded CSS for accurate cross-platform visualization.

### 3. Optimization Layer
* **Event Gating System:** A "Check-and-Process" logic gate that decouples the UI rendering loop from the image processing thread. This prevents "Main-Loop Saturation" during rapid parameter adjustments, ensuring a responsive GUI.

---

##  Mathematical Principles

The core color reconstruction relies on Linear Interpolation within the RGB vector space.

For a given pixel with normalized luminance $t$ (where $0 \le t \le 1$):

$$
\mathbf{C}_{final} = \mathbf{C}_{start} + (\mathbf{C}_{end} - \mathbf{C}_{start}) \cdot t
$$

Where:
* $\mathbf{C}_{start}$ is the RGB vector for shadow tones.
* $\mathbf{C}_{end}$ is the RGB vector for highlight tones.
* $t$ is the luminance coefficient derived from the grayscale conversion formula: $L = 0.299R + 0.587G + 0.114B$.

---

##  Installation

Ensure you have **Python 3.9+** installed.

### 1. Clone the repository
git clone [https://github.com/ZerxStarCode/HyperASCII-v3.git](https://github.com/ZerxStarCode/HyperASCII-v3.git)

### 2. Navigate to the project directory
cd HyperASCII-v3

### 3. Install dependencies (Pillow, Tkinter)
pip install -r requirements.txt ´´

##  Usage Guide
To launch the scientific interface:

python hyper_ascii.py

###  Workflow

Load Source: Import high-contrast raster images (.jpg, .png).

Parameter Tuning:

Resolution: Adjust width (suggested: 150-200 chars for text files).
Contrast (Gamma): Increase >1.5 for sharper edge definition.

Rendering Mode:

Standard: For general photography.
Block: For architectural/brutalist styles.

Export:

Save .TXT: For plain text representation.
Save .HTML: To apply the Chromatic Interpolation engine.


##  Roadmap
[x] v3.0: Chromatic Engine & Event Gating (Current)

[ ] v3.1: Multi-threading for 4K image processing.

[ ] v4.0: Video-to-ASCII (Frame-by-frame rendering).

[ ] v4.5: CLI (Command Line Interface) for batch processing.






