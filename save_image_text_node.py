import torch
import numpy as np
from PIL import Image
import os
import json
from datetime import datetime

import folder_paths


class SaveImageAndTextNode:
    """Node for saving an image and optionally a text file with the same filename prefix."""
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
            },
            "optional": {
                "text": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            }
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "save_image_and_text"
    CATEGORY = "MisterMR/IO"

    def save_image_and_text(self, image, filename_prefix="ComfyUI", text=None, prompt=None, extra_pnginfo=None):
        """Save image as PNG and optionally save text file if text is provided."""
        
        filename_prefix += self.prefix_append
        
        # Get full output folder path with subfolder support
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, image.shape[2], image.shape[1]
        )
        
        results = []
        
        for batch_index, img_tensor in enumerate(image):
            # Convert tensor to PIL Image
            img_array = img_tensor.cpu().numpy()
            img_array = (img_array * 255).astype(np.uint8)
            pil_image = Image.fromarray(img_array)
            
            # Prepare metadata for PNG
            metadata = None
            if not (prompt is None and extra_pnginfo is None):
                from PIL.PngImagePlugin import PngInfo
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for key in extra_pnginfo:
                        metadata.add_text(key, json.dumps(extra_pnginfo[key]))
            
            # Generate filename with counter
            if batch_index == 0:
                file_base = f"{filename}_{counter:05d}_"
            else:
                file_base = f"{filename}_{counter:05d}_{batch_index:02d}_"
            
            # Save image as PNG
            image_filename = f"{file_base}.png"
            image_path = os.path.join(full_output_folder, image_filename)
            
            pil_image.save(image_path, pnginfo=metadata, compress_level=self.compress_level)
            
            # Save text file only if text is provided and not empty
            if text is not None and text.strip():
                text_filename = f"{file_base}.txt"
                text_path = os.path.join(full_output_folder, text_filename)
                
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(text)
            
            results.append({
                "filename": image_filename,
                "subfolder": subfolder,
                "type": self.type
            })
            
            counter += 1
        
        return {"ui": {"images": results}}
