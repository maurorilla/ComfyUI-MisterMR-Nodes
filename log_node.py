from datetime import datetime


class LogNode:
    """Node for logging messages with timestamp to ComfyUI console."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "any_input": ("*",),
            }
        }

    RETURN_TYPES = ("*",)
    FUNCTION = "log_message"
    CATEGORY = "MisterMR/Utils"
    
    def log_message(self, text, any_input=None):
        """Log message with timestamp and return the input unchanged."""
        # Format datetime as yyyy-MM-dd hh.mm.ss.fff
        timestamp = datetime.now().strftime("%Y-%m-%d %H.%M.%S.%f")[:-3]  # Remove last 3 digits to get milliseconds
        
        # Log to ComfyUI console
        log_message = f"{timestamp} - {text}"
        print(log_message)
        
        # Return the input unchanged (passthrough)
        return (any_input,)
