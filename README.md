# ComfyUI-MisterMR-Nodes

A collection of custom nodes for ComfyUI that add drawing capabilities and prompt manipulation features to your workflow.

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

### PromptSelectorNode
Dynamically replaces placeholder words in prompts with words from a predefined list:
- Auto-increment mode for automatic cycling through words
- Manual index selection mode
- Real-time UI updates showing current selection
- Supports manual override even when auto-increment is enabled

Parameters:
- `prompt`: The main prompt text containing a placeholder word (multiline)
- `word_to_replace`: The placeholder word to be replaced (e.g., "REPLACE_WORD")
- `replacement_words`: List of replacement words, one per line (multiline)
- `auto_increment`: Enable/disable automatic cycling through words (default: enabled)
- `selected_index`: Index of the word to use (0-based, default: 0)

Returns:
- `prompt`: The prompt with the placeholder replaced by the selected word
- `selected_word`: The currently selected replacement word

**Features:**
- When auto-increment is enabled, the node automatically cycles through words on each execution
- Manual changes to `selected_index` are respected and reset the auto-increment sequence
- The UI displays the current selected word and updates in real-time
- Control after generate: Automatically increments the index after generation

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

### Drawing Nodes
1. In ComfyUI, you'll find the drawing nodes under the "MisterMR/Drawing" category
2. Connect an image input to the node
3. Configure the parameters as needed
4. The nodes will return the modified image that can be used in further processing

### Text/Prompt Nodes
1. Find the text manipulation nodes under the "MisterMR/Text" category
2. **PromptSelectorNode**: 
   - Enter your prompt with a placeholder word (e.g., "A beautiful REPLACE_WORD sunset")
   - Set `word_to_replace` to match your placeholder (e.g., "REPLACE_WORD")
   - Add replacement words, one per line (e.g., "red", "blue", "green")
   - Enable auto-increment for automatic cycling, or manually select an index
   - Connect the `prompt` output to your text input nodes
   - Connect the `selected_word` output to other nodes that need the current selected word

## Notes

### Drawing Nodes
- The drawing nodes support both RGB and RGBA images
- Font loading defaults to system Arial font, falls back to default font if unavailable
- Colors can be specified in hex format (#RRGGBB) or using the ColorNode
- Advanced color features include alpha transparency support
- For logo overlays, transparency is preserved when using PNG images with alpha channels

### Text/Prompt Nodes
- **PromptSelectorNode**: 
  - Manual changes to `selected_index` are immediately respected, even when auto-increment is enabled
  - The node maintains state per instance, so multiple nodes can have independent word lists
  - Empty lines in `replacement_words` are automatically filtered out
  - The `selected_index` automatically adjusts its maximum based on the number of replacement words