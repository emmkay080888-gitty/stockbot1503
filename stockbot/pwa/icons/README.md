# PWA Icons

The `manifest.json` references icon files at `/icons/icon-192.png` and `/icons/icon-512.png`.

## Generate Icons

You can generate these icons using any of these methods:

### Option 1: Emoji to PNG (Online)
Go to https://emojitopng.com/ and create:
- 192x192 PNG of 📈 chart emoji → save as `icon-192.png`
- 512x512 PNG of 📈 chart emoji → save as `icon-512.png`

### Option 2: Using Python
```python
from PIL import Image, ImageDraw, ImageFont

def create_icon(size, filename):
    img = Image.new('RGBA', (size, size), (14, 17, 23, 255))  # #0e1117
    draw = ImageDraw.Draw(img)
    # Draw a simple "📈" text
    font_size = size // 2
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf", font_size)
    except:
        font = ImageFont.load_default()
    draw.text((size//4, size//4), "📈", font=font, fill=(0, 255, 136, 255))
    img.save(filename)

create_icon(192, "icon-192.png")
create_icon(512, "icon-512.png")
```

### Option 3: Command Line (using ImageMagick)
```bash
# Install: sudo apt-get install imagemagick
convert -size 192x192 xc:'#0e1117' -font Noto-Emoji -pointsize 96 -fill '#00ff88' -gravity center -annotate 0 '📈' icon-192.png
convert -size 512x512 xc:'#0e1117' -font Noto-Emoji -pointsize 256 -fill '#00ff88' -gravity center -annotate 0 '📈' icon-512.png
```

Save the generated PNG files in this directory (`pwa/icons/`).
