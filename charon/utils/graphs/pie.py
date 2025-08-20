import matplotlib
import matplotlib.pyplot as plt
from numpy.typing import NDArray

matplotlib.use("Agg")  # Use non-interactive backend


def generate_nested_pie_chart(
    inner_values: NDArray,
    inner_labels: list,
    outer_values: NDArray,
    outer_labels: list,
    inner_colours: list,
    outer_colours: list,
    text_colour: str,
    bg_colour: str,
    title: str | None = None,
):
    fig, ax = plt.subplots()

    # First, plot the inner ring
    ax.pie(
        inner_values,
        radius=0.7,
        labels=inner_labels,
        labeldistance=0.5,
        colors=inner_colours,
        autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct / 100.0 * inner_values.sum()))})",
        textprops=dict(color=text_colour, fontsize=10, weight="bold"),
        wedgeprops=dict(width=0.3, edgecolor="w"),
        startangle=140,
    )

    # Then, plot the outer ring
    ax.pie(
        outer_values,
        radius=1.0,
        labels=outer_labels,
        labeldistance=1.1,
        colors=outer_colours,
        autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct / 100.0 * outer_values.sum()))})",
        textprops=dict(color=text_colour, fontsize=9),
        wedgeprops=dict(width=0.3, edgecolor="w"),
        startangle=140,
    )

    fig.patch.set_facecolor(bg_colour)
    ax.axis("equal")

    if title:
        fig.suptitle(title, fontsize=14, fontweight="bold", color=text_colour)

    return fig
