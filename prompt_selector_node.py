import sys
import os

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

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
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
        if node_id_for_state is None and hasattr(self, 'id'):
            node_id_for_state = self.id
            print(f"[PromptSelector] Using self.id: {node_id_for_state}")
        
        if node_id_for_state is None:
            node_id_for_state = "default"
            print(f"[PromptSelector] Using default state key")
        
        print(f"[PromptSelector] node_id_for_state: {node_id_for_state}")
        print(f"[PromptSelector] Current states: {list(PromptSelectorNode.node_states.keys())}")
        
        # Initialize state if it doesn't exist
        if node_id_for_state not in PromptSelectorNode.node_states:
            print(f"[PromptSelector] Creating new state for {node_id_for_state}")
            PromptSelectorNode.node_states[node_id_for_state] = {
                'current_index': 0,
                'words': [],
                'last_words_text': None,
                'last_ui_index': None  # Track the last index we sent to UI to detect manual changes
            }
        
        state = PromptSelectorNode.node_states[node_id_for_state]
        print(f"[PromptSelector] State before: current_index={state['current_index']}, last_ui_index={state.get('last_ui_index')}")
        
        # Parse replacement words from multiline text
        if state['last_words_text'] != replacement_words:
            state['words'] = [word.strip() for word in replacement_words.split('\n') if word.strip()]
            state['current_index'] = 0
            state['last_words_text'] = replacement_words
            state['last_ui_index'] = None  # Reset when words change
            print(f"[PromptSelector] Words updated, reset to 0")

        if not state['words']:
            return (prompt,)

        # Clamp selected_index to valid range
        clamped_selected_index = min(selected_index, len(state['words']) - 1) if selected_index >= 0 else 0
        
        # Determine which index to use
        if auto_increment == "enabled":
            # Detect manual changes: if selected_index differs from what we last sent to UI,
            # it means the user manually changed it
            manual_change = False
            if state.get('last_ui_index') is not None:
                # If selected_index doesn't match what we expect (current_index),
                # it's a manual change
                expected_index = state['current_index']
                if clamped_selected_index != expected_index:
                    manual_change = True
                    print(f"[PromptSelector] Manual change detected! selected_index={clamped_selected_index}, expected={expected_index}")
            
            if manual_change:
                # User manually changed selected_index: use it and reset auto-increment from there
                use_index = clamped_selected_index
                state['current_index'] = (clamped_selected_index + 1) % len(state['words'])
                next_index = state['current_index']
                print(f"[PromptSelector] Auto-increment with manual override: use_index={use_index}, next={next_index}")
            else:
                # Normal auto-increment behavior: use current_index and increment
                use_index = state['current_index']
                state['current_index'] = (state['current_index'] + 1) % len(state['words'])
                next_index = state['current_index']  # The next index that will be used
                print(f"[PromptSelector] Auto-increment: use_index={use_index}, next={next_index}")
        else:
            # Manual mode: always use selected_index
            use_index = clamped_selected_index
            state['current_index'] = use_index
            next_index = use_index  # For manual mode, show the index that was used
            print(f"[PromptSelector] Manual: use_index={use_index}")

        # Get the replacement word
        replacement_word = state['words'][use_index]
        print(f"[PromptSelector] Using word: '{replacement_word}' at index {use_index}")
        
        # Replace the word in the prompt
        output_prompt = prompt.replace(word_to_replace, replacement_word)
        
        # Send message to update the widget in the UI
        # When auto_increment is enabled, show the next index that will be used
        # When manual, show the index that was used
        ui_index = next_index if auto_increment == "enabled" else use_index
        print(f"[PromptSelector] Sending update: node={unique_id}, index={ui_index}")
        try:
            PromptServer.instance.send_sync(
                "mrm.promptselector.update",
                {
                    "node": unique_id,
                    "selected_index": ui_index,
                }
            )
            # Store the index we sent to UI so we can detect manual changes
            state['last_ui_index'] = ui_index
            print(f"[PromptSelector] Message sent successfully")
        except Exception as e:
            print(f"[PromptSelector] Error sending message: {e}")

        print(f"[PromptSelector] === EXECUTION END ===")
        return (output_prompt,)
