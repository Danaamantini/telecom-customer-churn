"""Build the static portfolio dashboard shown in the GitHub README."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "processed" / "clean_customers.csv"
DEFAULT_OUTPUT = ROOT / "dashboard" / "telecom_churn_dashboard.png"

NAVY = "#132238"
BLUE = "#3B82F6"
BLUE_LIGHT = "#DBEAFE"
RED = "#E45756"
RED_LIGHT = "#FDE8E7"
TEAL = "#18A999"
GOLD = "#F2B134"
INK = "#172033"
MUTED = "#637083"
GRID = "#E6EAF0"
PANEL = "#FFFFFF"
BACKGROUND = "#F4F7FB"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size=size)
    return ImageFont.load_default()


def pct(value: float) -> str:
    return f"{value:.1%}"


def read_metrics(path: Path) -> dict[str, object]:
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        rows.extend(csv.DictReader(handle))

    existing = [row for row in rows if row["customer_status"] != "Joined"]
    churned = [row for row in existing if row["customer_status"] == "Churned"]

    def rates(field: str) -> list[tuple[str, float]]:
        totals: Counter[str] = Counter()
        churns: Counter[str] = Counter()
        for row in existing:
            label = row[field].strip() or "No internet"
            totals[label] += 1
            churns[label] += row["customer_status"] == "Churned"
        return sorted(
            ((label, churns[label] / total) for label, total in totals.items()),
            key=lambda item: item[1],
            reverse=True,
        )

    reasons: Counter[str] = Counter(row["churn_category"].strip() for row in churned)
    reasons.pop("", None)
    churned_mrr = sum(float(row["monthly_charge"]) for row in churned)

    return {
        "rows": len(rows),
        "existing": len(existing),
        "churned": len(churned),
        "churn_rate": len(churned) / len(existing),
        "churned_mrr": churned_mrr,
        "contract": rates("contract"),
        "internet": rates("internet_type"),
        "reasons": reasons.most_common(5),
    }


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int = 22) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=PANEL, outline="#E8ECF2", width=2)


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    size: int,
    color: str = INK,
    bold: bool = False,
    anchor: str | None = None,
) -> None:
    draw.text(xy, value, font=load_font(size, bold), fill=color, anchor=anchor)


def draw_kpi(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    value: str,
    accent: str,
    note: str,
) -> None:
    rounded_panel(draw, box)
    x1, y1, x2, _ = box
    draw.rounded_rectangle((x1 + 18, y1 + 18, x1 + 28, y1 + 78), radius=5, fill=accent)
    text(draw, (x1 + 48, y1 + 22), label.upper(), 17, MUTED, True)
    text(draw, (x1 + 48, y1 + 53), value, 35, INK, True)
    text(draw, (x2 - 20, y1 + 79), note, 14, MUTED, anchor="ra")


def draw_bar_chart(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    values: list[tuple[str, float]],
    color: str,
    max_value: float,
) -> None:
    rounded_panel(draw, box)
    x1, y1, x2, y2 = box
    text(draw, (x1 + 28, y1 + 25), title, 24, INK, True)
    text(draw, (x1 + 28, y1 + 59), subtitle, 15, MUTED)

    label_width = 185
    chart_x1 = x1 + label_width
    chart_x2 = x2 - 42
    chart_y1 = y1 + 105
    chart_y2 = y2 - 45
    chart_width = chart_x2 - chart_x1

    for step in range(6):
        ratio = step / 5
        x = chart_x1 + int(chart_width * ratio)
        draw.line((x, chart_y1 - 8, x, chart_y2), fill=GRID, width=2)
        text(draw, (x, chart_y2 + 12), f"{max_value * ratio:.0%}", 13, MUTED, anchor="ma")

    row_height = (chart_y2 - chart_y1) / max(len(values), 1)
    for index, (label, value) in enumerate(values):
        cy = chart_y1 + row_height * (index + 0.5)
        bar_height = min(42, int(row_height * 0.58))
        text(draw, (chart_x1 - 18, int(cy)), label, 16, INK, anchor="rm")
        bar_end = chart_x1 + int(chart_width * min(value / max_value, 1))
        draw.rounded_rectangle(
            (chart_x1, int(cy - bar_height / 2), bar_end, int(cy + bar_height / 2)),
            radius=bar_height // 2,
            fill=color,
        )
        text(draw, (bar_end + 10, int(cy)), pct(value), 15, INK, True, anchor="lm")


def draw_reason_chart(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    reasons: list[tuple[str, int]],
    churned: int,
) -> None:
    rounded_panel(draw, box)
    x1, y1, x2, y2 = box
    text(draw, (x1 + 28, y1 + 25), "Why customers churn", 24, INK, True)
    text(draw, (x1 + 28, y1 + 59), "Share of churned customers by category", 15, MUTED)

    colors = [RED, GOLD, TEAL, BLUE, "#8B5CF6"]
    start_y = y1 + 105
    available = y2 - start_y - 30
    row_height = available / max(len(reasons), 1)
    max_count = max((count for _, count in reasons), default=1)
    chart_x1 = x1 + 195
    chart_x2 = x2 - 42

    for index, (label, count) in enumerate(reasons):
        share = count / churned
        cy = start_y + row_height * (index + 0.5)
        text(draw, (chart_x1 - 18, int(cy)), label, 15, INK, anchor="rm")
        end = chart_x1 + int((chart_x2 - chart_x1) * count / max_count)
        draw.rounded_rectangle((chart_x1, int(cy - 15), end, int(cy + 15)), radius=15, fill=colors[index])
        text(draw, (end + 9, int(cy)), pct(share), 14, INK, True, anchor="lm")


def build_dashboard(input_path: Path, output_path: Path) -> None:
    metrics = read_metrics(input_path)
    image = Image.new("RGB", (1600, 1000), BACKGROUND)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, 1600, 118), fill=NAVY)
    text(draw, (62, 34), "TELECOM CUSTOMER CHURN", 34, "#FFFFFF", True)
    text(draw, (62, 78), "Portfolio analysis  •  7,043 customers  •  California", 17, "#B9C8DD")
    text(draw, (1535, 58), "EXECUTIVE OVERVIEW", 15, "#DCE6F5", True, anchor="ra")

    card_y1, card_y2 = 145, 260
    gap = 22
    card_width = (1476 - gap * 3) // 4
    cards = [
        ("Existing customers", f"{metrics['existing']:,}", BLUE, "Joined excluded"),
        ("Churned customers", f"{metrics['churned']:,}", RED, "Observed snapshot"),
        ("Churn rate", pct(float(metrics["churn_rate"])), GOLD, "of existing base"),
        ("Churned monthly revenue", f"${float(metrics['churned_mrr']) / 1000:.1f}K", TEAL, "$1.65M annualized"),
    ]
    for index, card in enumerate(cards):
        x1 = 62 + index * (card_width + gap)
        draw_kpi(draw, (x1, card_y1, x1 + card_width, card_y2), *card)

    draw_bar_chart(
        draw,
        (62, 287, 782, 625),
        "Churn rate by contract",
        "Longer commitments are associated with materially lower churn",
        list(metrics["contract"]),
        RED,
        0.60,
    )
    draw_bar_chart(
        draw,
        (810, 287, 1538, 625),
        "Churn rate by internet type",
        "Fiber Optic is the highest-churn internet segment",
        list(metrics["internet"]),
        BLUE,
        0.50,
    )
    draw_reason_chart(draw, (62, 652, 1012, 925), list(metrics["reasons"]), int(metrics["churned"]))

    rounded_panel(draw, (1040, 652, 1538, 925))
    text(draw, (1070, 680), "Priority actions", 24, INK, True)
    actions = [
        ("1", "Test annual-plan migration", "Target Month-to-Month customers with a holdout group."),
        ("2", "Investigate Fiber experience", "Separate pricing, service quality, and local competition."),
        ("3", "Strengthen early onboarding", "Test structured contacts during the first 90 days."),
    ]
    for index, (number, title, detail) in enumerate(actions):
        y = 742 + index * 58
        draw.ellipse((1070, y, 1104, y + 34), fill=BLUE_LIGHT)
        text(draw, (1087, y + 17), number, 15, BLUE, True, anchor="mm")
        text(draw, (1120, y - 1), title, 17, INK, True)
        text(draw, (1120, y + 23), detail, 13, MUTED)

    text(
        draw,
        (62, 966),
        "Rates exclude customers with status Joined. Associations are observational, not causal effects.",
        14,
        MUTED,
    )
    text(draw, (1538, 966), "Source: IBM / Maven Analytics telecom churn dataset", 14, MUTED, anchor="ra")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG", optimize=True)
    print(f"Wrote {output_path} ({image.width}x{image.height})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_dashboard(args.input, args.output)
