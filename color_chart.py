import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

def plot_color_chart(x, y, luminosity=None):
    """
    Generates the CIE Chromaticity Diagram and returns a base64-encoded image.
    """
    # Load CIE 1931 boundary data
    cie_boundary = np.loadtxt("cie_1931_boundary.txt")  # Pre-saved boundary points
    x_boundary, y_boundary = cie_boundary[:, 0], cie_boundary[:, 1]

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x_boundary, y_boundary, color="black", label="CIE Boundary")

    # Add region annotations
    color_regions = [
        {"name": "Red", "coords": [0.65, 0.3]},
        {"name": "Yellow", "coords": [0.45, 0.5]},
        {"name": "Green", "coords": [0.3, 0.7]},
        {"name": "Blue", "coords": [0.15, 0.1]},
    ]
    for region in color_regions:
        ax.text(region["coords"][0], region["coords"][1], region["name"], fontsize=10, color="black")

    # Plot the calculated coordinates
    ax.scatter(x, y, color="red", s=100, label="Calculated Point")
    ax.annotate(f"({x:.3f}, {y:.3f})", (x, y), textcoords="offset points", xytext=(10, -10), ha='center', fontsize=9)

    # Add metadata beside the chart
    metadata = f"""
    x Coordinate: {x:.3f}
    y Coordinate: {y:.3f}
    Luminosity (%): {luminosity:.2f if luminosity else 'N/A'}
    """
    ax.text(1.05, 0.5, metadata, transform=ax.transAxes, fontsize=10, verticalalignment="center")

    # Final adjustments
    ax.set_title("CIE Chromaticity Diagram", fontsize=14)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.set_xlim(0, 0.8)
    ax.set_ylim(0, 0.9)

    # Save plot to a BytesIO object and encode as base64
    img_io = BytesIO()
    plt.tight_layout()
    plt.savefig(img_io, format="png")
    img_io.seek(0)
    base64_image = base64.b64encode(img_io.read()).decode("utf-8")
    plt.close(fig)  # Close the figure to free up memory
    return base64_image
