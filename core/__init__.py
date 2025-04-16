import torch

# Configuración global CUDA
if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True
    torch.set_float32_matmul_precision('high')
    
    # Configuración específica para RTX 4090
    DEVICE = torch.device("cuda")
    CUDA_AVAILABLE = True
else:
    DEVICE = torch.device("cpu")
    CUDA_AVAILABLE = False