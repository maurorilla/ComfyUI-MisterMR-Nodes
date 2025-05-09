# ComfyUI-MisterMR-Nodes

A collection of custom nodes for ComfyUI that add drawing capabilities to your workflow.

## Features

### AddSingleObjectNode
Allows you to draw various shapes on your images:
- Circle
- Rectangle
- Rounded Rectangle

Parameters:
- `image`: Input image
- `x`, `y`: Position coordinates
- `width`, `height`: Shape dimensions
- `object_type`: Shape type (circle/rect/round_rect)
- `border_size`: Thickness of shape border (0-100)
- `border_color`: Color of the border (hex format)
- `show_fill`: Enable/disable shape filling
- `fill_color`: Fill color (hex format) 

### AddSingleTextNode
Adds text to your images with various customization options:
- Custom positioning
- Three justification options (left/center/right)
- Adjustable font size

Parameters:
- `image`: Input image
- `text`: Text to draw
- `x`, `y`: Text position
- `width`, `height`: Text box dimensions
- `justification`: Text alignment (left/center/right)
- `font_size`: Size of the font (8-256)
- `font_family`: Font to use (defaults to Arial with system fallbacks)
- `text_color`: Color of the text (hex format)

### AddLogoNode
Overlays a logo or another image onto your base image:
- Custom positioning and sizing
- Option to preserve aspect ratio
- Adjustable opacity for transparent overlays

Parameters:
- `image`: Input base image
- `logo`: Logo image to overlay
- `x`, `y`: Logo position
- `width`, `height`: Logo dimensions
- `preserve_aspect_ratio`: Maintain original logo proportions (yes/no)
- `opacity`: Transparency of the logo (0.0-1.0)

### ColorNode
Creates color values for use with other MisterMR nodes:
- Define colors with RGBA values
- Use with border_color, fill_color, and text_color parameters

Parameters:
- `red`: Red component (0-255)
- `green`: Green component (0-255)
- `blue`: Blue component (0-255)
- `alpha`: Transparency (0.0-1.0)

Returns:
- `color`: Color object for use with other nodes
- `hex_color`: Hex string representation of the color

## Installation

1. Clone this repository into your ComfyUI custom_nodes folder:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/maurorilla/ComfyUI-MisterMR-Nodes
```

2. Restart ComfyUI

## Requirements
- PIL (Pillow)
- numpy
- torch
- matplotlib

## Usage

1. In ComfyUI, you'll find the nodes under the "MisterMR/Drawing" category
2. Connect an image input to either node
3. Configure the parameters as needed
4. The nodes will return the modified image that can be used in further processing

## Notes
- The drawing nodes support both RGB and RGBA images
- Font loading defaults to system Arial font, falls back to default font if unavailable
- Colors can be specified in hex format (#RRGGBB) or using the ColorNode
- Advanced color features include alpha transparency support
- For logo overlays, transparency is preserved when using PNG images with alpha channels