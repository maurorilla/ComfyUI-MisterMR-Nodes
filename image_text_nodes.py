import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Union
import matplotlib.colors as mcolors
import os
import sys

def color_to_rgb(color_name):
    """Convert color name to RGB tuple."""
    try:
        rgb = mcolors.to_rgb(color_name)
        return tuple(int(x * 255) for x in rgb)
    except:
        return (255, 255, 255)  # Default to white if color name is invalid

def get_system_font(font_size: int, font_family: str = None) -> ImageFont.FreeTypeFont:
    """Try to load a system font with fallbacks."""
    # If a specific font family is requested, try to load it first
    if font_family and font_family.lower() != "default":
        # First try standard paths based on OS
        if sys.platform == 'win32':
            font_dirs = [
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Windows\\Fonts')
            ]
        elif sys.platform == 'darwin':  # macOS
            font_dirs = ['/System/Library/Fonts', '/Library/Fonts', '~/Library/Fonts']
        else:  # Linux and others
            font_dirs = ['/usr/share/fonts/truetype', '/usr/local/share/fonts']
            
        # Try to find the specific font with common extensions
        for font_dir in font_dirs:
            for ext in ['.ttf', '.ttc', '.otf']:
                try:
                    font_path = os.path.join(os.path.expanduser(font_dir), f"{font_family}{ext}")
                    if os.path.exists(font_path):
                        return ImageFont.truetype(font_path, font_size)
                except Exception as e:
                    print(f"Failed to load font {font_path}: {str(e)}")
                    continue

    # Fall back to default font search if specific font not found or not specified
    if sys.platform == 'win32':
        font_dirs = [
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Windows\\Fonts')
        ]
        font_files = ['arial.ttf', 'segoeui.ttf', 'calibri.ttf', 'verdana.ttf']
    elif sys.platform == 'darwin':  # macOS
        font_dirs = ['/System/Library/Fonts', '/Library/Fonts', '~/Library/Fonts']
        font_files = ['Helvetica.ttc', 'Arial.ttf', 'Times.ttc']
    else:  # Linux and others
        font_dirs = ['/usr/share/fonts/truetype', '/usr/local/share/fonts']
        font_files = ['DejaVuSans.ttf', 'FreeSans.ttf', 'Ubuntu-R.ttf']

    # Try all combinations of directories and files
    for font_dir in font_dirs:
        for font_file in font_files:
            try:
                font_path = os.path.join(os.path.expanduser(font_dir), font_file)
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, font_size)
            except Exception as e:
                print(f"Failed to load font {font_path}: {str(e)}")
                continue

    # Fallback to default PIL font as last resort
    try:
        return ImageFont.load_default()
    except Exception as e:
        print(f"Error loading default font: {str(e)}")
        # Create a simple font as absolute fallback
        return None

def ensure_font(font, font_size):
    """Ensure we have a valid font object even if loading fails"""
    if font is None:
        try:
            # Try one more time with default
            return ImageFont.load_default()
        except:
            # If all else fails, return None and let the caller handle it
            print("Warning: Could not load any font. Text rendering may fail.")
            return None
    return font

class AddSingleObjectNode:
    """Node for drawing single shapes on images."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "x": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "y": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "width": ("INT", {"default": 100, "min": 1, "max": 10000}),
                "height": ("INT", {"default": 100, "min": 1, "max": 10000}),
                "object_type": (["circle", "rect", "round_rect"],),
                "border_size": ("INT", {"default": 2, "min": 0, "max": 100}),
                "border_color": ("COLOR", {"default": "#ffffff"}),
                "show_fill": (["yes", "no"],),
            },
            "optional": {
                "fill_color": ("COLOR", {"default": "#000000"})
            },
            "hidden": {
                "draw_area": "DRAW_AREA",
                "id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "draw_object"
    CATEGORY = "MisterMR/Drawing"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple with better type checking"""
        # First make sure we have a string
        if not isinstance(hex_color, str):
            # If we got passed a color object directly instead of its hex property
            if isinstance(hex_color, dict):
                if 'rgba' in hex_color:
                    # Include alpha handling
                    rgba = hex_color['rgba']
                    return rgba  # Return full RGBA tuple
                elif 'hex' in hex_color and isinstance(hex_color['hex'], str):
                    hex_color = hex_color['hex']
                else:
                    return (255, 255, 255, 255)  # Default white if invalid structure
            else:
                return (255, 255, 255, 255)  # Default white for any other non-string
                
        # Now we should have a string, proceed with normal processing
        hex_color = hex_color.lstrip('#')
        try:
            if len(hex_color) >= 6:
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                return rgb + (255,)  # Add full alpha
            return (255, 255, 255, 255)  # Default to white if invalid hex
        except (ValueError, IndexError):
            return (255, 255, 255, 255)  # Default to white if invalid hex
    
    def process_color(self, color):
        """Handle both string hex colors and color objects with alpha support"""
        if isinstance(color, dict) and 'rgba' in color:
            # It's a color object from ColorNode
            return tuple(color['rgba'])  # Return full RGBA tuple
        elif isinstance(color, dict) and 'hex' in color:
            # It's a color object but using hex
            # Check if there's an alpha value
            if 'a' in color:
                alpha_int = int(color['a'] * 255)
                rgb = self.hex_to_rgb(color['hex'])[:3]  # Get just the RGB part
                return rgb + (alpha_int,)  # Add the alpha
            return self.hex_to_rgb(color['hex'])
        elif isinstance(color, str):
            # It's a hex string
            return self.hex_to_rgb(color)
        else:
            # Fallback
            return (255, 255, 255, 255)

    def draw_object(self, image, x, y, width, height, object_type, border_size, border_color, show_fill, draw_area=None, id=None, fill_color=None):
        # Convert from tensor to PIL Image
        if isinstance(image, torch.Tensor):
            image = image.cpu().numpy()
            image = Image.fromarray((image[0] * 255).astype(np.uint8))
        else:
            image = Image.fromarray((image * 255).astype(np.uint8))
            
        # Create a copy of the image to draw on
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image, 'RGBA')  # Use RGBA mode for alpha support
        
        # Convert colors to RGB
        border_rgb = self.process_color(border_color)
        fill_rgb = None
        if show_fill == "yes" and fill_color is not None:
            fill_rgb = self.process_color(fill_color)
        
        try:
            if object_type == "circle":
                draw.ellipse([x, y, x + width, y + height], 
                            outline=border_rgb if border_size > 0 else None, 
                            width=border_size,
                            fill=fill_rgb if show_fill == "yes" else None)
            elif object_type == "rect":
                draw.rectangle([x, y, x + width, y + height], 
                             outline=border_rgb if border_size > 0 else None, 
                             width=border_size,
                             fill=fill_rgb if show_fill == "yes" else None)
            elif object_type == "round_rect":
                radius = min(20, min(width, height) // 4)  # Adaptive radius
                draw.rounded_rectangle([x, y, x + width, y + height], 
                                    radius=radius, 
                                    outline=border_rgb if border_size > 0 else None, 
                                    width=border_size,
                                    fill=fill_rgb if show_fill == "yes" else None)
        except Exception as e:
            print(f"Error drawing object: {str(e)}")
            return (image,)
            
        # Convert to tensor
        result = np.array(draw_image).astype(np.float32) / 255.0
        result = torch.from_numpy(result).unsqueeze(0)
        
        # Pass the preview image to the drawing area widget
        if draw_area is not None:
            preview_image = np.array(draw_image)
            draw_area = {"image": {
                "width": preview_image.shape[1],
                "height": preview_image.shape[0],
                "data": preview_image.tobytes()
            }}
        
        return (result,)

class AddSingleTextNode:
    """Node for drawing text on images."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "text": ("STRING", {"default": "Sample Text", "multiline": True}),
                "x": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "y": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "width": ("INT", {"default": 300, "min": 1, "max": 10000}),
                "height": ("INT", {"default": 100, "min": 1, "max": 10000}),
                "justification": (["left", "center", "right"],),
                "font_size": ("INT", {"default": 32, "min": 8, "max": 256}),
                "font_family": ("STRING", {"default": "Arial"}),
                "text_color": ("COLOR", {"default": "#ffffff"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "draw_text"
    CATEGORY = "MisterMR/Drawing"

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple with better type checking"""
        # First make sure we have a string
        if not isinstance(hex_color, str):
            # If we got passed a color object directly instead of its hex property
            if isinstance(hex_color, dict):
                if 'rgba' in hex_color:
                    # Include alpha handling
                    rgba = hex_color['rgba']
                    return rgba  # Return full RGBA tuple
                elif 'hex' in hex_color and isinstance(hex_color['hex'], str):
                    hex_color = hex_color['hex']
                else:
                    return (255, 255, 255, 255)  # Default white if invalid structure
            else:
                return (255, 255, 255, 255)  # Default white for any other non-string
                
        # Now we should have a string, proceed with normal processing
        hex_color = hex_color.lstrip('#')
        try:
            if len(hex_color) >= 6:
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                return rgb + (255,)  # Add full alpha
            return (255, 255, 255, 255)  # Default to white if invalid hex
        except (ValueError, IndexError):
            return (255, 255, 255, 255)  # Default to white if invalid hex
    
    def process_color(self, color):
        """Handle both string hex colors and color objects with alpha support"""
        if isinstance(color, dict) and 'rgba' in color:
            # It's a color object from ColorNode
            return tuple(color['rgba'])  # Return full RGBA tuple
        elif isinstance(color, dict) and 'hex' in color:
            # It's a color object but using hex
            # Check if there's an alpha value
            if 'a' in color:
                alpha_int = int(color['a'] * 255)
                rgb = self.hex_to_rgb(color['hex'])[:3]  # Get just the RGB part
                return rgb + (alpha_int,)  # Add the alpha
            return self.hex_to_rgb(color['hex'])
        elif isinstance(color, str):
            # It's a hex string
            return self.hex_to_rgb(color)
        else:
            # Fallback
            return (255, 255, 255, 255)

    def draw_text(self, image, text, x, y, width, height, justification, font_size, font_family, text_color):
        # Convert from tensor to PIL Image
        if isinstance(image, torch.Tensor):
            image = image.cpu().numpy()
            image = Image.fromarray((image[0] * 255).astype(np.uint8))
        else:
            image = Image.fromarray((image * 255).astype(np.uint8))
            
        # Create a copy of the image to draw on
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image, 'RGBA')  # Use RGBA mode for alpha support
        
        # Get font and convert color
        font = get_system_font(font_size, font_family)
        font = ensure_font(font, font_size)
        text_rgb = self.process_color(text_color)
        
        try:
            # Calculate text alignment
            if font:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Calculate position based on justification
                if justification == "center":
                    text_x = x + (width - text_width) // 2
                elif justification == "right":
                    text_x = x + width - text_width
                else:  # left
                    text_x = x
                    
                text_y = y + (height - text_height) // 2
                
                # Draw the text
                draw.text((text_x, text_y), text, fill=text_rgb, font=font)
            else:
                # Fallback if no font is available - draw simple text without font
                draw.text((x, y), text + " (font error)", fill=text_rgb)
        except Exception as e:
            print(f"Error drawing text: {str(e)}")
            return (image,)
        
        # Convert back to tensor
        result = np.array(draw_image).astype(np.float32) / 255.0
        result = torch.from_numpy(result).unsqueeze(0)
        
        return (result,)

class ColorNode:
    """Node for creating RGBA colors to use with other MisterMR nodes."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "red": ("INT", {"default": 255, "min": 0, "max": 255}),
                "green": ("INT", {"default": 255, "min": 0, "max": 255}),
                "blue": ("INT", {"default": 255, "min": 0, "max": 255}),
                "alpha": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("COLOR", "STRING")
    RETURN_NAMES = ("color", "hex_color")
    FUNCTION = "create_color"
    CATEGORY = "MisterMR/Drawing"
    
    def rgb_to_hex(self, r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def create_color(self, red, green, blue, alpha):
        # Create hex color string (without alpha, for backward compatibility)
        hex_color = self.rgb_to_hex(red, green, blue)
        
        # Convert alpha (0.0-1.0) to integer (0-255)
        alpha_int = int(alpha * 255)
        
        # Create color object that contains both RGB and alpha information
        color_obj = {
            "hex": hex_color,
            "r": red,
            "g": green,
            "b": blue,
            "a": alpha,
            "rgba": (red, green, blue, alpha_int)
        }
        
        return (color_obj, hex_color)

class AddLogoNode:
    """Node for adding logo images onto other images."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "logo": ("IMAGE",),
                "x": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "y": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "width": ("INT", {"default": 100, "min": 1, "max": 10000}),
                "height": ("INT", {"default": 100, "min": 1, "max": 10000}),
                "preserve_aspect_ratio": (["yes", "no"],),
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "add_logo"
    CATEGORY = "MisterMR/Drawing"
    
    def add_logo(self, image, logo, x, y, width, height, preserve_aspect_ratio, opacity):
        # Convert from tensor to PIL Image
        if isinstance(image, torch.Tensor):
            image = image.cpu().numpy()
            image = Image.fromarray((image[0] * 255).astype(np.uint8))
        else:
            image = Image.fromarray((image * 255).astype(np.uint8))
            
        if isinstance(logo, torch.Tensor):
            logo = logo.cpu().numpy()
            logo = Image.fromarray((logo[0] * 255).astype(np.uint8))
        else:
            logo = Image.fromarray((logo * 255).astype(np.uint8))
        
        # Create a copy of the image to draw on
        result_image = image.copy()
        
        # Resize the logo
        original_width, original_height = logo.size
        new_width, new_height = width, height
        
        if preserve_aspect_ratio == "yes":
            # Calculate the aspect ratio of the original logo
            aspect_ratio = original_width / original_height
            
            # Adjust dimensions to preserve aspect ratio
            if width / height > aspect_ratio:
                # Width is too large for the given height
                new_width = int(height * aspect_ratio)
            else:
                # Height is too large for the given width
                new_height = int(width / aspect_ratio)
        
        # Resize the logo
        resized_logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # If logo doesn't have alpha channel, add one
        if resized_logo.mode != 'RGBA':
            resized_logo = resized_logo.convert('RGBA')
            
        # Apply opacity if needed
        if opacity < 1.0:
            # Create a copy of the logo with modified alpha channel
            data = np.array(resized_logo)
            # Apply opacity to the alpha channel (if exists)
            if data.shape[2] >= 4:
                data[:, :, 3] = data[:, :, 3] * opacity
            # Convert back to image
            resized_logo = Image.fromarray(data)
        
        try:
            # Paste the logo onto the image
            if resized_logo.mode == 'RGBA':
                result_image.paste(resized_logo, (x, y), resized_logo)
            else:
                result_image.paste(resized_logo, (x, y))
        except Exception as e:
            print(f"Error adding logo: {str(e)}")
            return (image,)
        
        # Convert back to tensor
        result = np.array(result_image).astype(np.float32) / 255.0
        result = torch.from_numpy(result).unsqueeze(0)
        
        return (result,)