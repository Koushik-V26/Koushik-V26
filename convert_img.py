import sys
from PIL import Image, ImageEnhance, ImageOps

def image_to_ascii(image_path, output_path, width=90, target_height=53, invert=False, contrast=1.5, brightness=1.0, sharpness=1.0, threshold=None):
    # Load image
    img = Image.open(image_path)
    
    # Crop based on the image dimensions
    if img.size[0] == 452 and img.size[1] == 588:
        crop_box = (22, 40, 406, 588)
        img = img.crop(crop_box)
        print(f"Applied crop for 452x588 image: {crop_box}")
    elif img.size[0] >= 3072 and img.size[1] >= 2800:
        crop_box = (1200, 800, 3072, 2800)
        img = img.crop(crop_box)
        print(f"Applied crop for original large image: {crop_box}")
    else:
        print(f"Skipping crop, image size {img.size} is smaller than crop box.")
    
    w_orig, h_orig = img.size
    
    # Convert to grayscale
    img_gray = img.convert("L")
    
    # Apply background thresholding if specified
    if threshold is not None:
        img_gray = img_gray.point(lambda p: 255 if p > threshold else p)
    
    # Enhance sharpness
    if sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(img_gray)
        img_gray = enhancer.enhance(sharpness)
    
    # Enhance contrast
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img_gray)
        img_gray = enhancer.enhance(contrast)
    
    # Enhance brightness
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img_gray)
        img_gray = enhancer.enhance(brightness)
    
    # Aspect ratio of monospace font characters in the SVG is about 0.4375.
    # For a square image of W x W, to display it without stretching:
    # character_height = W * 0.4375
    # Let's calculate the correct height for the ASCII art based on the image size
    img_aspect = h_orig / w_orig
    char_aspect = 0.4375  # width/height ratio of rendered font character
    
    # We want width = 90
    ascii_width = width
    ascii_height = int(ascii_width * img_aspect * char_aspect)
    
    print(f"Original size: {w_orig}x{h_orig}, aspect: {img_aspect:.3f}")
    print(f"Calculated ASCII dimensions: {ascii_width}x{ascii_height}")
    
    # Resize image
    img_resized = img_gray.resize((ascii_width, ascii_height), Image.Resampling.LANCZOS)
    
    # ASCII characters ramp (from dark/sparse to bright/dense)
    # Since we are drawing on a dark background where characters are bright (cyan),
    # a dark pixel (black) should map to a sparse character (space)
    # and a bright pixel (white) should map to a dense character (#, @).
    # If invert=True, we flip this.
    chars = [" ", ".", ":", "-", "=", "+", "*", "%", "@", "#"]
    if invert:
        chars = chars[::-1]
        
    num_chars = len(chars)
    
    ascii_lines = []
    for y in range(ascii_height):
        line = ""
        for x in range(ascii_width):
            pixel = img_resized.getpixel((x, y))
            # Map pixel (0-255) to character index
            idx = int(pixel / 256 * num_chars)
            line += chars[idx]
        ascii_lines.append(line)
        
    # Pad to target_height if needed
    if len(ascii_lines) < target_height:
        padding_needed = target_height - len(ascii_lines)
        top_padding = padding_needed // 2
        bottom_padding = padding_needed - top_padding
        
        padded_lines = [" " * ascii_width] * top_padding + ascii_lines + [" " * ascii_width] * bottom_padding
        print(f"Padded {top_padding} lines at top, {bottom_padding} lines at bottom to reach {target_height} lines.")
        ascii_lines = padded_lines
    elif len(ascii_lines) > target_height:
        # Crop vertically from the center
        start = (len(ascii_lines) - target_height) // 2
        print(f"Cropped {start} lines from top and bottom to reach {target_height} lines.")
        ascii_lines = ascii_lines[start:start+target_height]
        
    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ascii_lines))
        
    print(f"Successfully wrote ASCII art to {output_path}")

if __name__ == "__main__":
    image_to_ascii(
        image_path="C:/Users/varan/Downloads/img.jpg",
        output_path="portrait.txt",
        width=90,
        target_height=53,
        invert=True,  # Set to True if we need to invert
        contrast=2.0,
        brightness=1.0,
        sharpness=2.5,
        threshold=150
    )
