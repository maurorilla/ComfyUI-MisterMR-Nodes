from .image_text_nodes import AddSingleObjectNode, AddSingleTextNode, ColorNode, AddLogoNode
from .prompt_selector_node import PromptSelectorNode
from .save_image_text_node import SaveImageAndTextNode
from .log_node import LogNode

NODE_CLASS_MAPPINGS = {
    "AddSingleObject": AddSingleObjectNode, 
    "AddSingleText": AddSingleTextNode,
    "ColorNode": ColorNode,
    "AddLogo": AddLogoNode,
    "PromptSelector": PromptSelectorNode,
    "SaveImageAndText": SaveImageAndTextNode,
    "Log": LogNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AddSingleObject": "MisterMR - Object", 
    "AddSingleText": "MisterMR - Text",
    "ColorNode": "MisterMR - Color",
    "AddLogo": "MisterMR - Add Logo",
    "PromptSelector": "MisterMR - Prompt Selector",
    "SaveImageAndText": "MisterMR - Save Image and Text",
    "Log": "MisterMR - Log"
}
WEB_DIRECTORY = "./web/js"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', "WEB_DIRECTORY"]

 