import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'accuracy_plot.png'

# synthetic example data resembling training/validation curves
epochs = np.arange(0, 26)
# training accuracy: rises from 0.08 to ~0.68 with small noise
train = 0.08 + (0.60 * (1 - np.exp(-epochs/8))) + 0.02 * np.sin(epochs/2.5)
# validation accuracy: slightly higher progression
val = 0.15 + (0.65 * (1 - np.exp(-epochs/7))) + 0.02 * np.cos(epochs/3.0)

# clamp
train = np.clip(train, 0, 1)
val = np.clip(val, 0, 1)

plt.figure(figsize=(7,5))
plt.plot(epochs, train, 'r-', linewidth=2, label='Training accuracy')
plt.plot(epochs, val, 'b-', linewidth=2, label='Validation accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title('Training and validation accuracy')
plt.legend(loc='upper left')
plt.ylim(0,1)
plt.xlim(0,25)
plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig(OUT, dpi=150)
print('Wrote', OUT)
