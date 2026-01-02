import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

console.log("[PromptSelector] Extension file loaded!");

app.registerExtension({
  name: "PromptSelectorUI",

  // Function to update max value for selected_index based on replacement_words
  updateSelectedIndexMax(node) {
    if (!node || !node.widgets) return;
    
    let replacementWordsWidget = null;
    let selectedIndexWidget = null;
    
    // Find both widgets
    for (const widget of node.widgets) {
      if (widget.name === "replacement_words") {
        replacementWordsWidget = widget;
      } else if (widget.name === "selected_index") {
        selectedIndexWidget = widget;
      }
    }
    
    if (replacementWordsWidget && selectedIndexWidget) {
      // Count non-empty lines
      const text = replacementWordsWidget.value || "";
      const lines = text.split('\n').filter(line => line.trim().length > 0);
      const maxValue = Math.max(0, lines.length - 1); // Max is length - 1 (0-indexed)
      
      // Update the max value
      if (selectedIndexWidget.options) {
        selectedIndexWidget.options.max = maxValue;
      }
      
      // Clamp current value if it exceeds the new max
      if (selectedIndexWidget.value > maxValue) {
        selectedIndexWidget.value = maxValue;
        if (selectedIndexWidget.callback) {
          selectedIndexWidget.callback(maxValue);
        }
      }
      
      console.log(`[PromptSelector] Updated max for selected_index to ${maxValue} (${lines.length} words)`);
    }
  },

  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.python_module !== "custom_nodes.prompt_selector_node") return;
    
    // Override the node's onNodeCreated to set up dynamic max updates
    const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
      if (originalOnNodeCreated) {
        originalOnNodeCreated.call(this);
      }
      
      // Update max when node is created
      setTimeout(() => {
        const extension = app.extensions?.PromptSelectorUI;
        if (extension && extension.updateSelectedIndexMax) {
          extension.updateSelectedIndexMax(this);
        }
      }, 100);
    };
  },

  async setup() {
    console.log("[PromptSelector] Extension setup called!");
    
    const self = this;
    
    // Store extension reference for access from other methods
    if (!app.extensions) app.extensions = {};
    app.extensions.PromptSelectorUI = {
      updateSelectedIndexMax: self.updateSelectedIndexMax.bind(self)
    };
    
    // Update max for all existing PromptSelector nodes when graph loads
    const updateAllNodes = () => {
      if (app.graph && app.graph._nodes) {
        for (const node of app.graph._nodes) {
          if (node.type === "PromptSelector") {
            self.updateSelectedIndexMax(node);
          }
        }
      }
    };
    
    // Update existing nodes after a short delay
    setTimeout(updateAllNodes, 200);
    
    // Update max when nodes are added
    const originalOnNodeAdded = app.graph.onNodeAdded;
    app.graph.onNodeAdded = function(node) {
      if (originalOnNodeAdded) {
        originalOnNodeAdded.call(this, node);
      }
      
      if (node.type === "PromptSelector") {
        // Update max when node is added
        setTimeout(() => {
          const extension = app.extensions?.PromptSelectorUI;
          if (extension && extension.updateSelectedIndexMax) {
            extension.updateSelectedIndexMax(node);
          }
        }, 100);
        
        // Watch for changes to replacement_words widget
        if (node.widgets) {
          for (const widget of node.widgets) {
            if (widget.name === "replacement_words") {
              const originalCallback = widget.callback;
              widget.callback = (value) => {
                if (originalCallback) {
                  originalCallback(value);
                }
                // Update max when replacement_words changes
                setTimeout(() => {
                  const extension = app.extensions?.PromptSelectorUI;
                  if (extension && extension.updateSelectedIndexMax) {
                    extension.updateSelectedIndexMax(node);
                  }
                }, 10);
              };
            }
          }
        }
      }
    };
    
    // Listen for the update message from Python
    api.addEventListener("mrm.promptselector.update", (evt) => {
      console.log("[PromptSelector] Received update event:", evt.detail);
      
      const nodeId = evt.detail.node;
      const newIndex = evt.detail.selected_index;
      
      if (!nodeId) {
        console.warn("[PromptSelector] No node ID in event data:", evt.detail);
        return;
      }
      
      // Find the specific node by ID
      if (app.graph && app.graph._nodes) {
        const node = app.graph._nodes.find(n => n.id === nodeId);
        
        if (node) {
          console.log("[PromptSelector] Found node by ID:", nodeId);
          
          if (node.widgets) {
            for (const widget of node.widgets) {
              if (widget.name === "selected_index") {
                console.log("[PromptSelector] Updating widget from", widget.value, "to", newIndex);
                widget.value = newIndex;
                // Call the widget's callback if it exists to ensure proper update
                if (widget.callback) {
                  widget.callback(newIndex);
                }
                break;
              }
            }
          }
          
          // Force redraw to update the UI
          app.graph.setDirtyCanvas(true, true);
        } else {
          console.warn("[PromptSelector] Node not found with ID:", nodeId);
        }
      }
    });
  },
});
