from .image_text_nodes import AddSingleObjectNode, AddSingleTextNode, ColorNode

NODE_CLASS_MAPPINGS = {
    "AddSingleObject": AddSingleObjectNode, 
    "AddSingleText": AddSingleTextNode,
    "ColorNode": ColorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AddSingleObject": "MisterMR - Object", 
    "AddSingleText": "MisterMR - Text",
    "ColorNode": "MisterMR - Color"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']