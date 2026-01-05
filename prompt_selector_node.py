import sys
import os
import uuid

# Get the directory of the current script
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up two levels to get to the ComfyUI root directory
comfyui_root_dir = os.path.abspath(os.path.join(current_script_dir, "..", ".."))

# Add the ComfyUI root directory to the Python path if it's not already there
if comfyui_root_dir not in sys.path:
    sys.path.insert(0, comfyui_root_dir)

from server import PromptServer

class PromptSelectorNode:
    OUTPUT_NODE = True
    
    # Class-level dictionary to persist state per node instance
    node_states = {}

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "A beautiful landscape with REPLACE_WORD", "multiline": True}),
                "word_to_replace": ("STRING", {"default": "REPLACE_WORD", "multiline": False}),
                "replacement_words": ("STRING", {"default": "sunset\ndawn\nnoon\nmidnight", "multiline": True}),
                "auto_increment": (["enabled", "disabled"], {"default": "enabled"}),
                "selected_index": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1, "control_after_generate": "increment"}),
            },
            "hidden": {
                "unique_id": ("UNIQUE_ID",)
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "selected_word")
    FUNCTION = "replace_word"
    CATEGORY = "MisterMR/Text"

    @classmethod
    def IS_CHANGED(cls, prompt, word_to_replace, replacement_words, auto_increment, selected_index, **kwargs):
        # Always re-execute when auto_increment is enabled
        if auto_increment == "enabled":
            return float("nan")  # NaN is never equal to itself, forcing re-execution
        return (prompt, word_to_replace, replacement_words, auto_increment, selected_index)

    def replace_word(self, prompt, word_to_replace, replacement_words, auto_increment, selected_index, **kwargs):
        unique_id = kwargs.get('unique_id')
        print(f"[PromptSelector] === EXECUTION START ===")
        print(f"[PromptSelector] kwargs: {kwargs}")
        print(f"[PromptSelector] unique_id received: {unique_id} (type: {type(unique_id) if unique_id else 'None'})")
        print(f"[PromptSelector] auto_increment: {auto_increment}")
        print(f"[PromptSelector] selected_index input: {selected_index}")
        
        # Get or create state for this node instance
        node_id_for_state = unique_id
        if node_id_for_state is None:
            if hasattr(self, 'id') and self.id is not None:
                node_id_for_state = str(self.id)
                print(f"[PromptSelector] Using self.id as state key: {node_id_for_state}")
            else:
                # Generate a unique ID as last resort (shouldn't happen in normal operation)
                node_id_for_state = f"node_{uuid.uuid4().hex[:8]}"
                print(f"[PromptSelector] WARNING: Generated fallback ID: {node_id_for_state}")
        
        if node_id_for_state is None:
            raise ValueError("[PromptSelector] Cannot determine node identifier for state management")
        
        print(f"[PromptSelector] node_id_for_state: {node_id_for_state}")
        print(f"[PromptSelector] Current states: {list(PromptSelectorNode.node_states.keys())}")
        
        # Initialize state if it doesn't exist
        if node_id_for_state not in PromptSelectorNode.node_states:
            print(f"[PromptSelector] Creating new state for {node_id_for_state}")
            PromptSelectorNode.node_states[node_id_for_state] = {
                'words': [],
                'last_words_text': None
            }
        
        state = PromptSelectorNode.node_states[node_id_for_state]
        print(f"[PromptSelector] State: words_count={len(state.get('words', []))}")
        
        # Parse replacement words from multiline text
        if state['last_words_text'] != replacement_words:
            state['words'] = [word.strip() for word in replacement_words.split('\n') if word.strip()]
            state['last_words_text'] = replacement_words
            print(f"[PromptSelector] Words updated: {len(state['words'])} words")

        if not state['words']:
            return (prompt, "")

        # Clamp selected_index to valid range
        clamped_selected_index = min(selected_index, len(state['words']) - 1) if selected_index >= 0 else 0
        
        # Always use the selected_index from the widget - this is what the user sees
        use_index = clamped_selected_index
        print(f"[PromptSelector] Using index: {use_index}")
        
        # Determine what to show in UI after execution
        if auto_increment == "enabled":
            # Auto-increment: show the next index in UI
            next_index = (use_index + 1) % len(state['words'])
            print(f"[PromptSelector] Auto-increment enabled: next_index={next_index}")
        else:
            # Manual mode: keep showing the same index
            next_index = use_index
            print(f"[PromptSelector] Manual mode: keeping index={use_index}")

        # Get the replacement word
        replacement_word = state['words'][use_index]
        print(f"[PromptSelector] Using word: '{replacement_word}' at index {use_index}")
        
        # Replace the word in the prompt
        output_prompt = prompt.replace(word_to_replace, replacement_word)
        
        # Send message to update the widget in the UI
        ui_index = next_index
        print(f"[PromptSelector] Sending update: node={node_id_for_state}, index={ui_index}")
        try:
            PromptServer.instance.send_sync(
                "mrm.promptselector.update",
                {
                    "node": node_id_for_state,  # Use the same ID used for state
                    "selected_index": ui_index,
                }
            )
            print(f"[PromptSelector] Message sent successfully")
        except Exception as e:
            print(f"[PromptSelector] Error sending message: {e}")

        print(f"[PromptSelector] === EXECUTION END ===")
        return (output_prompt, replacement_word)
