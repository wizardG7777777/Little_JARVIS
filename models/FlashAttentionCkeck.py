def is_flash_attention_available(verbose: bool = False) -> bool:
    """
    Check if Flash Attention 2 is available.

    Args:
        verbose: If True, print reason when not available (default: False)

    Returns:
        bool: True if available, False otherwise
    """
    try:
        # Linux check
        import platform
        if platform.system().lower() != 'linux':
            if verbose: print("Not Linux system")
            return False

        # Flash Attention check
        import flash_attn
        if hasattr(flash_attn, '__version__'):
            if not flash_attn.__version__.startswith('2.'):
                if verbose: print("Flash Attention version is not 2.x")
                return False

        # CUDA check
        import torch
        if not torch.cuda.is_available():
            if verbose: print("CUDA not available")
            return False

        if not torch.version.cuda:
            if verbose: print("PyTorch not compiled with CUDA")
            return False

        return True

    except ImportError as e:
        if verbose: print(f"Import error: {e}")
        return False
    except Exception as e:
        if verbose: print(f"Unexpected error: {e}")
        return False
if __name__ == "__main__":
    print(is_flash_attention_available())