"""Generate PWA icons for Stock Signal Bot.

Usage:
    python generate_icons.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ICONS_DIR = Path(__file__).parent / "stockbot" / "pwa" / "icons"
ICONS_DIR.mkdir(parents=True, exist_ok=True)


def create_icon(size: int, filename: str):
    """Create a simple stock chart icon."""
    img = Image.new("RGBA", (size, size), (14, 17, 23, 255))  # #0e1117
    draw = ImageDraw.Draw(img)
    
    # Draw a simple candlestick chart pattern
    margin = size // 6
    chart_top = margin
    chart_bottom = size - margin
    chart_width = size - 2 * margin
    chart_height = chart_bottom - chart_top
    
    # Background card
    card_margin = size // 8
    draw.rectangle(
        [card_margin, card_margin, size - card_margin, size - card_margin],
        fill=(26, 26, 46, 255),
        outline=(0, 255, 136, 100),
        width=max(1, size // 64),
    )
    
    # Draw a mini candlestick chart (3 candles going up)
    candle_width = chart_width // 8
    gap = candle_width // 2
    
    candles = [
        (chart_left := margin + gap, chart_left + candle_width,
         chart_bottom - chart_height * 0.6, chart_bottom - chart_height * 0.8,  # green candle
         chart_bottom - chart_height * 0.55, chart_bottom - chart_height * 0.85),
        (chart_left + candle_width + gap, chart_left + 2 * candle_width + gap,
         chart_bottom - chart_height * 0.3, chart_bottom - chart_height * 0.55,  # green candle
         chart_bottom - chart_height * 0.25, chart_bottom - chart_height * 0.6),
        (chart_left + 2 * (candle_width + gap), chart_left + 3 * candle_width + 2 * gap,
         chart_bottom - chart_height * 0.1, chart_bottom - chart_height * 0.35,  # green candle
         chart_bottom - chart_height * 0.05, chart_bottom - chart_height * 0.4),
    ]
    
    for left, right, open_y, close_y, high_y, low_y in candles:
        # Wick
        wick_x = (left + right) // 2
        draw.line([(wick_x, high_y), (wick_x, low_y)], fill=(0, 255, 136, 200), width=max(1, size // 96))
        # Body (green candle - going up, so open > close)
        if open_y > close_y:
            draw.rectangle([left, close_y, right, open_y], fill=(0, 255, 136, 220))
        else:
            draw.rectangle([left, open_y, right, close_y], fill=(255, 68, 68, 220))
    
    # Small arrow indicator on the last candle
    arrow_size = size // 16
    last_candle_right = margin + 3 * candle_width + 2 * gap
    arrow_x = last_candle_right + gap + candle_width // 2
    arrow_y = chart_bottom - chart_height * 0.5
    draw.polygon(
        [(arrow_x, arrow_y - arrow_size), (arrow_x + arrow_size, arrow_y + arrow_size // 2),
         (arrow_x - arrow_size, arrow_y + arrow_size // 2)],
        fill=(0, 255, 136, 200),
    )
    
    # Save
    img.save(ICONS_DIR / filename)
    print(f"  ✓ Created {filename} ({size}x{size})")


if __name__ == "__main__":
    print("Generating PWA icons...")
    create_icon(192, "icon-192.png")
    create_icon(512, "icon-512.png")
    print(f"Done! Icons saved to: {ICONS_DIR}")
