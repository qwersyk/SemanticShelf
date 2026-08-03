import torch
import torch.nn as nn
import torch.nn.functional as F

class BookGenreLMHead(nn.Module):
    def __init__(self, input_dim=384, num_classes=10, hidden_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.net(x)

    def predict_probabilities(self, x):
        self.eval()
        with torch.no_grad():
            tensor_x = torch.tensor(x, dtype=torch.float32) if isinstance(x, list) else x
            if tensor_x.dim() == 1:
                tensor_x = tensor_x.unsqueeze(0)
            logits = self.forward(tensor_x)
            return F.softmax(logits, dim=1)[0].tolist()
