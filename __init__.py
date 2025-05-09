from .image_text_nodes import AddSingleObjectNode, AddSingleTextNode, ColorNode, AddLogoNode

NODE_CLASS_MAPPINGS = {
    "AddSingleObject": AddSingleObjectNode, 
    "AddSingleText": AddSingleTextNode,
    "ColorNode": ColorNode,
    "AddLogo": AddLogoNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AddSingleObject": "MisterMR - Object", 
    "AddSingleText": "MisterMR - Text",
    "ColorNode": "MisterMR - Color",
    "AddLogo": "MisterMR - Add Logo"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']