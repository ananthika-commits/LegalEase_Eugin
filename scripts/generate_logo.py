"""
Logo generation script for LegalEase.
Generates a crisp, professional legal emblem and branding logo in assets/logo.png.
"""

import os
from PIL import Image, ImageDraw, ImageFont


def create_legalease_logo(output_path: str = "assets/logo.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # High-resolution canvas for retina display (scaled down when rendering)
    width, height = 700, 200
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    navy = (27, 54, 93, 255)       # Deep Navy Blue #1B365D
    gold = (212, 160, 23, 255)      # Warm Gold #D4A017
    accent_blue = (59, 130, 246, 255) # Bright Royal Blue #3B82F6
    charcoal = (51, 65, 85, 255)    # Slate/Charcoal #334155

    # 1. Draw Crest Background (Shield / Hexagon)
    crest_x, crest_y = 110, 100
    shield_pts = [
        (crest_x, crest_y - 70),       # Top center
        (crest_x + 55, crest_y - 50),  # Top right
        (crest_x + 55, crest_y + 20),  # Mid right
        (crest_x, crest_y + 70),       # Bottom point
        (crest_x - 55, crest_y + 20),  # Mid left
        (crest_x - 55, crest_y - 50),  # Top left
    ]
    draw.polygon(shield_pts, fill=(240, 244, 250, 255), outline=navy, width=4)

    # 2. Draw Scales of Justice inside Crest
    # Central Column
    draw.line([(crest_x, crest_y - 45), (crest_x, crest_y + 45)], fill=navy, width=5)
    # Column base
    draw.polygon([(crest_x - 22, crest_y + 45), (crest_x + 22, crest_y + 45), (crest_x, crest_y + 35)], fill=navy)
    # Column finial (top knob)
    draw.ellipse([(crest_x - 7, crest_y - 52), (crest_x + 7, crest_y - 38)], fill=gold)

    # Crossbeam (horizontal lever)
    beam_y = crest_y - 25
    draw.line([(crest_x - 42, beam_y), (crest_x + 42, beam_y)], fill=navy, width=4)
    draw.ellipse([(crest_x - 4, beam_y - 4), (crest_x + 4, beam_y + 4)], fill=gold)

    # Left Scale Pan & Strings
    left_x = crest_x - 38
    draw.line([(left_x, beam_y), (left_x - 12, beam_y + 30)], fill=charcoal, width=2)
    draw.line([(left_x, beam_y), (left_x + 12, beam_y + 30)], fill=charcoal, width=2)
    draw.arc([(left_x - 15, beam_y + 22), (left_x + 15, beam_y + 38)], start=0, end=180, fill=gold, width=4)

    # Right Scale Pan & Strings
    right_x = crest_x + 38
    draw.line([(right_x, beam_y), (right_x - 12, beam_y + 30)], fill=charcoal, width=2)
    draw.line([(right_x, beam_y), (right_x + 12, beam_y + 30)], fill=charcoal, width=2)
    draw.arc([(right_x - 15, beam_y + 22), (right_x + 15, beam_y + 38)], start=0, end=180, fill=gold, width=4)

    # 3. Typography
    # Try loading clean TTF fonts or fallback to default
    font_large = None
    font_tag = None
    for font_name in ["georgia.ttf", "times.ttf", "arialbd.ttf", "arial.ttf"]:
        try:
            font_large = ImageFont.truetype(font_name, 56)
            font_tag = ImageFont.truetype("arial.ttf", 16)
            break
        except Exception:
            continue

    if font_large is None:
        font_large = ImageFont.load_default()
        font_tag = ImageFont.load_default()

    # Draw Brand Title: "LegalEase"
    text_x = 200
    text_y = 52
    draw.text((text_x, text_y), "Legal", fill=navy, font=font_large)
    
    # Calculate offset for "Ease" to style with gold/accent
    try:
        legal_w = draw.textlength("Legal", font=font_large)
    except AttributeError:
        legal_w = 145

    draw.text((text_x + legal_w, text_y), "Ease", fill=accent_blue, font=font_large)

    # Subtle separator line
    draw.line([(text_x, text_y + 70), (text_x + 460, text_y + 70)], fill=gold, width=3)

    # Tagline
    draw.text((text_x + 2, text_y + 80), "AI-POWERED LEGAL DOCUMENT GENERATOR", fill=charcoal, font=font_tag)

    img.save(output_path, "PNG")
    print(f"[Success] Logo saved successfully to {output_path}")


if __name__ == "__main__":
    create_legalease_logo()
