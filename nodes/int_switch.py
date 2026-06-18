class HN_OnOff:
    """
    A simple toggle that returns 1 for True (ON) and 0 for False (OFF).
    Now upgraded with a second output for pure BOOLEAN data!
    Consistent branding for the Hypnodes suite!
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "on": ("BOOLEAN", {"default": True}),
            }
        }

    # Define BOTH output types and names in order
    RETURN_TYPES = ("INT", "BOOLEAN")
    RETURN_NAMES = ("INT", "BOOLEAN")
    FUNCTION = "return_on_off"
    CATEGORY = "Hypnodes/Logic"

    def return_on_off(self, on):
        # Calculate the integer value (1 or 0)
        val_int = 1 if on else 0

        # Return BOTH values as a tuple matching RETURN_TYPES order!
        return (val_int, on)

    @classmethod
    def IS_CHANGED(cls, on):
        return on
