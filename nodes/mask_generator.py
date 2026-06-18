import torch
import torch.nn.functional as F

class HN_MaskGenerator:
    MAX_CHARS = 10
    RETURN_TYPES = ("MASK",) + tuple(["MASK"] * MAX_CHARS)
    RETURN_NAMES = ("base_mask",) + \
        tuple([f"mask_{i}" for i in range(1, MAX_CHARS + 1)])

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"latent": ("LATENT",), "hn_config": ("HN_CONFIG",), }}

    FUNCTION = "generate_masks"
    CATEGORY = "Hypnodes/MultiChar"

    @staticmethod
    def _gaussian_blur(tensor, sigma):
        if sigma <= 0:
            return tensor

        sigma = min(sigma, 64)
        t = tensor.unsqueeze(0).unsqueeze(0)
        kernel_size = int(sigma) | 1  # Ensure it's odd

        for _ in range(3):
            t = F.pad(t, (kernel_size//2, kernel_size//2,
                      kernel_size//2, kernel_size//2), mode='replicate')
            t = F.avg_pool2d(t, kernel_size, stride=1)

        return t.squeeze(0).squeeze(0)

    def generate_masks(self, latent, hn_config):
        if not hn_config:
            hn_config = {}

        character_count = int(hn_config.get("character_count", 1))
        layout_mode = str(hn_config.get("layout_mode", "Horizontal")).strip()
        mask_blur = hn_config.get("mask_blur", 0)

        latent_height = latent["samples"].shape[2]
        latent_width = latent["samples"].shape[3]

        # Base mask is always a full 1.0 (white) mask for the background/global pass
        base_mask = torch.ones((latent_height, latent_width),
                               dtype=torch.float32, device="cpu").unsqueeze(0)
        output_masks = [base_mask]

        for i in range(1, self.MAX_CHARS + 1):
            # If the current slot is beyond the count, output a black mask
            if i > character_count:
                empty_mask = torch.zeros(
                    (latent_height, latent_width), dtype=torch.float32, device="cpu").unsqueeze(0)
                output_masks.append(empty_mask)
                continue

            char_mask = torch.zeros(
                (latent_height, latent_width), dtype=torch.float32, device="cpu")

            # Procedural partitioning based on count
            if layout_mode.lower() == "horizontal":
                char_height = latent_height // character_count
                y_start = (i - 1) * char_height
                y_end = latent_height if i == character_count else i * char_height
                char_mask[y_start:y_end, :] = 1.0

            elif layout_mode.lower() == "vertical":
                char_width = latent_width // character_count
                x_start = (i - 1) * char_width
                x_end = latent_width if i == character_count else i * char_width
                char_mask[:, x_start:x_end] = 1.0

            else:
                char_mask[:, :] = 1.0

            # Apply the blur for smooth transitions
            blurred_mask = self._gaussian_blur(char_mask, mask_blur)
            output_masks.append(blurred_mask.unsqueeze(0))

        return tuple(output_masks)
