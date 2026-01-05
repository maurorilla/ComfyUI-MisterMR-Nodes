# ComfyUI-MisterMR-Nodes

A collection of custom nodes for ComfyUI that add drawing capabilities, prompt manipulation, and file I/O features to your workflow.

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

---

## Nodes Overview

| Node | Display Name | Category | Description |
|------|-------------|----------|-------------|
| AddSingleObject | MisterMR - Object | MisterMR/Drawing | Draw shapes on images |
| AddSingleText | MisterMR - Text | MisterMR/Drawing | Add text to images |
| AddLogo | MisterMR - Add Logo | MisterMR/Drawing | Overlay logos/images |
| ColorNode | MisterMR - Color | MisterMR/Drawing | Create RGBA colors |
| PromptSelector | MisterMR - Prompt Selector | MisterMR/Text | Dynamic prompt word replacement |
| SaveImageAndText | MisterMR - Save Image and Text | MisterMR/IO | Save images with optional text files |

---

## Drawing Nodes

### AddSingleObjectNode
**Display Name:** MisterMR - Object

Draws various shapes on your images with customizable borders and fills.

**Shape Types:**
- Circle
- Rectangle
- Rounded Rectangle

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image` | IMAGE | - | Input image |
| `x`, `y` | INT | 0 | Position coordinates |
| `width`, `height` | INT | 100 | Shape dimensions |
| `object_type` | ENUM | circle | Shape type: `circle`, `rect`, `round_rect` |
| `border_size` | INT | 2 | Border thickness (0-100) |
| `border_color` | COLOR | #ffffff | Border color (hex or ColorNode) |
| `show_fill` | ENUM | no | Enable fill: `yes`, `no` |
| `fill_color` | COLOR | #000000 | Fill color (optional, hex or ColorNode) |

**Returns:** `IMAGE` - Modified image with shape drawn

---

### AddSingleTextNode
**Display Name:** MisterMR - Text

Adds text to images with customizable positioning, alignment, and styling.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image` | IMAGE | - | Input image |
| `text` | STRING | Sample Text | Text to draw (multiline supported) |
| `x`, `y` | INT | 0 | Text box position |
| `width`, `height` | INT | 300/100 | Text box dimensions |
| `justification` | ENUM | left | Text alignment: `left`, `center`, `right` |
| `font_size` | INT | 32 | Font size (8-256) |
| `font_family` | STRING | Arial | Font family name |
| `text_color` | COLOR | #ffffff | Text color (hex or ColorNode) |

**Returns:** `IMAGE` - Modified image with text drawn

**Notes:**
- Font loading defaults to system fonts (Arial on Windows, Helvetica on macOS)
- Falls back to default system fonts if specified font is unavailable

---

### AddLogoNode
**Display Name:** MisterMR - Add Logo

Overlays a logo or another image onto your base image with positioning and transparency controls.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image` | IMAGE | - | Base image |
| `logo` | IMAGE | - | Logo/overlay image |
| `x`, `y` | INT | 0 | Logo position |
| `width`, `height` | INT | 100 | Logo dimensions |
| `preserve_aspect_ratio` | ENUM | yes | Maintain proportions: `yes`, `no` |
| `opacity` | FLOAT | 1.0 | Logo transparency (0.0-1.0) |

**Returns:** `IMAGE` - Combined image with logo overlay

**Notes:**
- Supports PNG images with alpha channel transparency
- When aspect ratio is preserved, the logo fits within the specified dimensions

---

### ColorNode
**Display Name:** MisterMR - Color

Creates RGBA color values for use with other MisterMR drawing nodes.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `red` | INT | 255 | Red component (0-255) |
| `green` | INT | 255 | Green component (0-255) |
| `blue` | INT | 255 | Blue component (0-255) |
| `alpha` | FLOAT | 1.0 | Transparency (0.0-1.0) |

**Returns:**
- `color` - Color object for use with drawing nodes
- `hex_color` - Hex string representation (#RRGGBB)

**Usage:**
Connect the `color` output to `border_color`, `fill_color`, or `text_color` inputs of drawing nodes for full RGBA support including transparency.

---

## Text/Prompt Nodes

### PromptSelectorNode
**Display Name:** MisterMR - Prompt Selector

Dynamically replaces placeholder words in prompts with words from a predefined list. Perfect for batch generation with word variations.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | STRING | A beautiful landscape with REPLACE_WORD | Main prompt with placeholder (multiline) |
| `word_to_replace` | STRING | REPLACE_WORD | Placeholder word to replace |
| `replacement_words` | STRING | sunset, dawn... | List of replacements, one per line (multiline) |
| `auto_increment` | ENUM | enabled | Auto-cycle: `enabled`, `disabled` |
| `selected_index` | INT | 0 | Current word index (0-based) |

**Returns:**
- `prompt` - Modified prompt with placeholder replaced
- `selected_word` - Currently selected replacement word

**Features:**
- **Auto-increment mode:** Automatically cycles through words on each execution
- **Manual mode:** Select specific words by index
- **Control after generate:** Widget automatically increments after each generation
- **Real-time UI updates:** Shows current selection in the node interface
- **Per-instance state:** Multiple nodes maintain independent word lists
- **Empty line filtering:** Blank lines in word list are automatically skipped

**Example Usage:**
1. Set prompt: `"A beautiful STYLE sunset over the ocean"`
2. Set word_to_replace: `"STYLE"`
3. Add replacement_words:
   ```
   vibrant
   peaceful
   dramatic
   golden
   ```
4. Enable auto-increment
5. Each generation will use the next word in the list

---

## I/O Nodes

### SaveImageAndTextNode
**Display Name:** MisterMR - Save Image and Text

Saves images to the output folder with optional accompanying text files. Ideal for saving generated images alongside their prompts or metadata.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image` | IMAGE | - | Image to save |
| `filename_prefix` | STRING | ComfyUI | Prefix for saved files |
| `text` | STRING | - | Optional text to save (multiline, optional input) |

**Returns:** Output node (displays saved images in UI)

**Features:**
- Saves images as PNG with automatic numbering
- Optionally saves a matching `.txt` file with the same filename
- Preserves workflow metadata in PNG files
- Supports batch processing
- Files are saved to ComfyUI's output directory
- Text file is only created if text input is connected and non-empty

**Output Files:**
```
output/
├── ComfyUI_00001_.png
├── ComfyUI_00001_.txt  (if text provided)
├── ComfyUI_00002_.png
└── ComfyUI_00002_.txt  (if text provided)
```

**Example Usage:**
1. Connect your final image to the `image` input
2. Set a descriptive `filename_prefix` (e.g., "landscape_sunset")
3. Connect `selected_word` from PromptSelectorNode to `text` input to save the word used
4. Or connect any prompt/description to save alongside the image

---

## Tips & Best Practices

### Drawing Nodes
- All drawing nodes support both RGB and RGBA images
- Colors can be specified as hex strings (`#RRGGBB`) or using the ColorNode for alpha support
- For transparent overlays, use ColorNode with alpha < 1.0
- Chain multiple drawing nodes to add shapes, text, and logos in layers

### Workflow Integration
- Use **PromptSelectorNode** → **SaveImageAndTextNode** to batch generate variations and save each with its word label
- Connect the `selected_word` output to save files or for logging which variant was used
- Use **ColorNode** outputs with drawing nodes for consistent color schemes across your workflow

### Performance Notes
- Drawing nodes work with tensor images directly from other ComfyUI nodes
- Font loading is cached after first use per session
- PromptSelectorNode maintains state per instance, allowing multiple independent selectors

---

## License

MIT License - Feel free to use and modify as needed.
