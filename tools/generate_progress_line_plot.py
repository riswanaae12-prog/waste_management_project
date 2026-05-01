import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'project_progress_line.png'

# Phases or milestones
phases = ['Init', 'Backend', 'Frontend', 'Simulator', 'Integration', 'Final']
x = np.arange(len(phases))

# Example progress values per phase for components (0-100)
backend = [10, 70, 85, 90, 93, 95]
frontend = [5, 30, 60, 80, 88, 90]
simulator = [0, 20, 60, 100, 100, 100]
notifications = [0, 40, 70, 85, 92, 95]
truck = [0, 10, 40, 80, 88, 90]
db = [10, 50, 70, 90, 100, 100]
tests = [0, 10, 20, 40, 60, 70]

plt.figure(figsize=(10,6))
plt.plot(x, backend, '-o', label='Backend', linewidth=2)
plt.plot(x, frontend, '-o', label='Frontend', linewidth=2)
plt.plot(x, simulator, '-o', label='Simulator', linewidth=2)
plt.plot(x, notifications, '-o', label='Notifications', linewidth=2)
plt.plot(x, truck, '-o', label='Truck Responder', linewidth=2)
plt.plot(x, db, '-o', label='DB & Migrations', linewidth=2)
plt.plot(x, tests, '-o', label='Tests/Integration', linewidth=2)

plt.xticks(x, phases)
plt.ylim(0, 110)
plt.ylabel('Completion (%)')
plt.title('Project Progress Across Phases')
plt.grid(True, linestyle='--', alpha=0.4)
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig(OUT, dpi=150)
print('Wrote', OUT)
