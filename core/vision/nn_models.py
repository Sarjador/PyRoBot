import torch
import torch.nn as nn
import torchvision.models as models
from torch.cuda.amp import autocast


class ROObjectDetector(nn.Module):
    def __init__(self):
        super().__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        backbone = models.mobilenet_v3_small(pretrained=True)
        self.features = backbone.features
        self.classifier = nn.Sequential(
            nn.Linear(576, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 10)  # 10 clases de objetos en RO
        ).to(self.device)

    @autocast()
    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        return self.classifier(x)


class RONavigationNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.resnet18(pretrained=True)
        self.model.fc = nn.Linear(512, 4)  # 4 direcciones
        self.model = self.model.to(self.device)

    def forward(self, x):
        return self.model(x)