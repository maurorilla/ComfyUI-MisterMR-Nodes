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
- `canvas_width`, `canvas_height`: Canvas dimensions

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
- Colors can be specified in hex format (#RRGGBB)