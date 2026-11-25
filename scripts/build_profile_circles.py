"""Draw original score-colored profile circles from the audited indicator table.

Run from any directory: python scripts/build_profile_circles.py
Only assets/taivano-profile-circle.png and assets/kinijos-profile-circle.png
are generated. This educational adaptation uses the assignment's four domains,
not the official Circles of Sustainability domain framework or SDG thresholds.
Each sector's filled rings all use its final 1–9 score color.
"""

from pathlib import Path
import hashlib
import json
import math

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "indicators.json"
ASSETS = ROOT / "assets"
DOMAINS = [
    "Ekonomika",
    "Švietimas ir technologijos",
    "Sveikata ir demografija",
    "Ekologija",
]
PALETTE = [
    "#b2182b", "#d6604d", "#e8854a", "#f4ac5e", "#f6cf65",
    "#d9df80", "#a7cf6a", "#67ad59", "#25834a",
]
INK = "#172D3E"
MUTED = "#54616B"
GRID = "#D6DCE0"
SIZE = (2200, 2500)


def font(size, bold=False):
    """Use the same portable font preference as the existing build script."""
    paths = [
        Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu")
        / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    ]
    for path in paths:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def ring_sector(cx, cy, low, high, start, end):
    """Polygon for one of nine annular cells in a 28-sector circle."""
    angles = [math.radians(start + (end - start) * j / 12) for j in range(13)]
    return [
        (cx + high * math.cos(a), cy + high * math.sin(a)) for a in angles
    ] + [
        (cx + low * math.cos(a), cy + low * math.sin(a)) for a in reversed(angles)
    ]


def draw_circle(rows, country, filename, source_hash):
    image = Image.new("RGB", SIZE, "white")
    draw = ImageDraw.Draw(image)
    title = "Taivanas" if country == "taiwan" else "Žemyninė Kinija"
    draw.text((1100, 95), title, font=font(78, True), fill=INK, anchor="mm")
    draw.text(
        (1100, 185), "Darnaus vystymosi profilis • 28 kriterijai • 4 sritys",
        font=font(37), fill=MUTED, anchor="mm",
    )

    # Preserve the existing wheel's order: clockwise, beginning at twelve o'clock.
    cx, cy = 1100, 1130
    inner, outer = 180, 770
    radial_step = (outer - inner) / 9
    angular_step = 360 / 28
    for index, row in enumerate(rows):
        start = -90 + index * angular_step
        end = start + angular_step
        score = row["scores"][country]
        color = PALETTE[score - 1]
        for level in range(1, 10):
            points = ring_sector(
                cx, cy,
                inner + (level - 1) * radial_step,
                inner + level * radial_step,
                start + 0.30, end - 0.30,
            )
            draw.polygon(
                points, fill=color if level <= score else "white",
                outline=GRID, width=2,
            )
        angle = math.radians((start + end) / 2)
        lx = cx + (outer + 105) * math.cos(angle)
        ly = cy + (outer + 105) * math.sin(angle)
        draw.text((lx, ly - 20), row["id"], font=font(38, True), fill=INK, anchor="mm")
        draw.text((lx, ly + 27), str(score), font=font(36, True), fill=INK, anchor="mm")

    # Strong cardinal boundaries delineate four quadrants, each with seven criteria.
    for degrees in (-90, 0, 90, 180):
        a = math.radians(degrees)
        draw.line(
            [(cx + inner * math.cos(a), cy + inner * math.sin(a)),
             (cx + outer * math.cos(a), cy + outer * math.sin(a))],
            fill="#87949D", width=4,
        )
    draw.ellipse((cx - inner, cy - inner, cx + inner, cy + inner), outline=GRID, width=3)
    draw.text((cx, cy - 30), "1–9", font=font(66, True), fill=INK, anchor="mm")
    draw.text((cx, cy + 43), "balai", font=font(37), fill=MUTED, anchor="mm")

    # Domain colors would conflict with score colors, so explicit code ranges map
    # each domain instead. The order matches the clockwise quadrants above.
    legends = [
        ("ECO01–ECO07", "Ekonomika"),
        ("EDU01–EDU07", "Švietimas ir technologijos"),
        ("H1–H7", "Sveikata ir demografija"),
        ("ENV1–ENV7", "Ekologija"),
    ]
    for index, (codes, domain) in enumerate(legends):
        x = 110 + (index % 2) * 1070
        y = 2080 + (index // 2) * 66
        draw.text((x, y), codes, font=font(30, True), fill=INK, anchor="lm")
        draw.text((x + 265, y), domain, font=font(31), fill=INK, anchor="lm")

    box_width, gap, box_top, box_height = 155, 12, 2230, 60
    legend_width = 9 * box_width + 8 * gap
    left = (SIZE[0] - legend_width) / 2
    for index, color in enumerate(PALETTE):
        x = left + index * (box_width + gap)
        draw.rounded_rectangle(
            (x, box_top, x + box_width, box_top + box_height), radius=8, fill=color,
        )
        label_fill = "white" if index in (0, 8) else "#172D3E"
        draw.text(
            (x + box_width / 2, box_top + box_height / 2), str(index + 1),
            font=font(32, True), fill=label_fill, anchor="mm",
        )
    draw.text(
        (1100, 2335),
        "1 žemiausias • 5 vidurinis • 9 aukščiausias pasirinktos imties intervalas",
        font=font(31), fill=INK, anchor="mm",
    )
    draw.text(
        (1100, 2400),
        "Mokomoji Circles of Sustainability adaptacija • duomenys 2021–2024 m.",
        font=font(31), fill=MUTED, anchor="mm",
    )
    draw.text(
        (1100, 2450), "Metodo šaltinis: circlesofsustainability.com",
        font=font(28), fill=MUTED, anchor="mm",
    )

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", f"{title}: mokomasis darnaus vystymosi profilis")
    metadata.add_text("Creator", "Original chart generated by scripts/build_profile_circles.py with Pillow")
    metadata.add_text("Description", "Original drawing; 28 criteria in four assignment domains, clockwise in data order. Filled ring count and the single sector color encode the same final score. White outer cells are unfilled scale intervals.")
    metadata.add_text("MethodAttribution", "Educational adaptation inspired by Circles of Sustainability, https://circlesofsustainability.com. Domain framework adapted to this assignment. Scores refer to the selected reference samples, not official SDG thresholds.")
    metadata.add_text("SourceData", "data/indicators.json; factual observations dated 2021–2024; original data sources and reference samples are documented in that file.")
    metadata.add_text("SourceDataSHA256", source_hash)
    metadata.add_text("Palette", ",".join(PALETTE))
    metadata.add_text("CountryKey", country)
    metadata.add_text("Scores", json.dumps({row["id"]: row["scores"][country] for row in rows}, ensure_ascii=False))
    image.save(ASSETS / filename, pnginfo=metadata, dpi=(220, 220))


def main():
    raw = DATA.read_bytes()
    rows = json.loads(raw)["indicators"]
    expected_domains = [domain for domain in DOMAINS for _ in range(7)]
    if len(rows) != 28 or [row["domain"] for row in rows] != expected_domains:
        raise ValueError("Expected 28 criteria ordered in four seven-criterion domains.")
    for row in rows:
        for country in ("taiwan", "china"):
            score = row["scores"][country]
            if type(score) is not int or not 1 <= score <= 9:
                raise ValueError(f"Invalid score: {row['id']} / {country}: {score!r}")
    ASSETS.mkdir(exist_ok=True)
    digest = hashlib.sha256(raw).hexdigest()
    for country, filename in [
        ("taiwan", "taivano-profile-circle.png"),
        ("china", "kinijos-profile-circle.png"),
    ]:
        draw_circle(rows, country, filename, digest)
        print(ASSETS / filename)


if __name__ == "__main__":
    main()
