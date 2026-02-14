# 🤝 Contributing to Silent Sabotage

Thank you for contributing to the Silent Sabotage leak detection system! This guide will help you get started.

## 🚀 Getting Started

> **⚡ Why uv?** We use [uv](https://github.com/astral-sh/uv) instead of pip because it's:
> - **10-100x faster** at installing packages
> - **Built in Rust** for maximum performance
> - **Modern dependency management** with lockfiles
> - **Perfect for hackathons** where speed matters!

### First Time Setup
```bash
# Clone the repository
git clone <repository-url>
cd ias_hack_main

# Install uv (if not already installed)
pip install uv

# Sync dependencies (auto-creates venv and installs packages)
uv sync

# Activate virtual environment
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Generate test data
python data/generate_data.py
```

### Adding New Dependencies
```bash
# Add a new package (automatically updates pyproject.toml and uv.lock)
uv add package-name

# Add a development dependency
uv add --dev pytest black

# Add specific version
uv add numpy==1.24.3

# After adding packages, team members just run:
uv sync  # Updates their environment to match
```

## 🌿 Branching Strategy

### Branch Naming Convention
```
model-01-isolation-forest    # For Model 01
model-02-severity            # For Model 02
model-03-leak-size           # For Model 03
model-04-acoustic            # For Model 04
model-05-forecast            # For Model 05
dashboard                    # For dashboard work
feature/add-xyz              # For new features
bugfix/fix-xyz               # For bug fixes
docs/update-xyz              # For documentation
```

### Creating a Branch
```bash
# Always start from main
git checkout main
git pull origin main

# Create your feature branch
git checkout -b model-01-isolation-forest
```

## 📝 Commit Message Guidelines

### Format
```
<type>: <subject>

<body (optional)>
```

### Types
- `feat`: New feature (e.g., "feat: Add rolling features to isolation forest")
- `fix`: Bug fix (e.g., "fix: Handle negative pressure values")
- `docs`: Documentation (e.g., "docs: Update model 01 README")
- `refactor`: Code refactoring (e.g., "refactor: Extract data loading to helper")
- `test`: Add tests (e.g., "test: Add unit tests for severity classifier")
- `chore`: Maintenance (e.g., "chore: Update requirements.txt")
- `wip`: Work in progress (e.g., "wip: Training model with new params")

### Examples
```bash
git commit -m "feat: Implement isolation forest with polynomial features"
git commit -m "fix: Handle edge case where pressure_drop is zero"
git commit -m "docs: Add troubleshooting section to Model 01 README"
git commit -m "refactor: Move data loading to utils/data_loader.py"
```

## 🔄 Pull Request Process

### 1. Before Creating PR
```bash
# Make sure your code works
python models/01_isolation_forest/train.py

# Check for syntax errors
python -m py_compile models/01_isolation_forest/train.py

# Update documentation if needed
# Edit README.md or model-specific README

# Commit all changes
git add .
git commit -m "feat: Complete isolation forest implementation"
```

### 2. Push Your Branch
```bash
git push origin model-01-isolation-forest
```

### 3. Create Pull Request on GitHub
- Go to the repository on GitHub
- Click "New Pull Request"
- Select your branch
- Fill in the PR template:

```markdown
## Description
Brief description of what this PR does

## Changes
- Added feature X
- Fixed bug Y
- Updated documentation for Z

## Model Performance (if applicable)
- Accuracy: 92.3%
- Precision: 89.1%
- Recall: 87.5%

## Testing
- [ ] Model trains successfully
- [ ] No syntax errors
- [ ] Documentation updated
- [ ] Example output included

## Screenshots (if applicable)
Add screenshots of dashboard changes or visualizations
```

### 4. Code Review
- At least one team member should review
- Address any feedback
- Once approved, merge to main

## 📂 What to Commit

### ✅ DO Commit
- Python code (`.py` files)
- Jupyter notebooks (`.ipynb` files)
- Configuration files (`pyproject.toml`)
- Lockfile (`uv.lock`) - ensures everyone has same versions
- Documentation (`.md` files)
- Small sample outputs (<1MB)

### ❌ DON'T Commit
- Large data files (`.csv`, `.json`) - Use `.gitignore`
- Model artifacts (`.pkl`, `.h5`, `.pt`) - Share via cloud storage
- Virtual environment (`.venv/`) - auto-created by `uv sync`
- `__pycache__/` directories
- Personal API keys or credentials
- Large plots or images (>1MB)

### 💡 Exception: Documentation Assets
Small images for README files are OK if stored in `docs/`:
```bash
# This is fine
git add docs/architecture_diagram.png

# This should be ignored
# Large training plots are in .gitignore
```

## 🧪 Testing Your Changes

### Before Committing
```bash
# 1. Test your training script
python models/01_isolation_forest/train.py

# 2. Check for Python errors
python -m py_compile your_file.py

# 3. Test imports
python -c "from models.model_01 import LeakAnomalyDetector"

# 4. Run a quick end-to-end test
python -c "
from models.model_01.train import LeakAnomalyDetector
detector = LeakAnomalyDetector()
print('✅ Import successful')
"
```

## 🐛 Reporting Issues

### Create an Issue on GitHub
Include:
1. **Title**: Brief description (e.g., "Model 01: KeyError when zone not in data")
2. **Description**: Detailed explanation
3. **Steps to Reproduce**: How to trigger the bug
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Environment**: Python version, OS, etc.
7. **Error Message**: Copy-paste the full traceback

### Example Issue
```markdown
**Title:** Model 01: KeyError when processing data with missing zones

**Description:**
The isolation forest model crashes when the input data doesn't contain all 4 zones.

**Steps to Reproduce:**
1. Generate data with only Zone_A and Zone_B
2. Run `python models/01_isolation_forest/train.py`
3. Error occurs during feature preparation

**Expected Behavior:**
Model should handle any number of zones gracefully

**Actual Behavior:**
```
KeyError: 'Zone_C'
at line 145 in prepare_features()
```

**Environment:**
- Python 3.10
- Windows 11
- pandas 2.0.3

**Proposed Solution:**
Add a check to filter available zones before processing
```

## 💻 Code Style Guidelines

### Python Style
Follow PEP 8 with some flexibility:

```python
# Good: Clear variable names
average_pressure = data['pressure_psi'].mean()

# Bad: Unclear abbreviations
avg_p = data['pressure_psi'].mean()

# Good: Docstrings for functions
def calculate_leak_cost(leak_size_mm: float) -> float:
    """
    Calculate annual cost of a leak.
    
    Args:
        leak_size_mm: Leak diameter in millimeters
        
    Returns:
        Annual cost in USD
    """
    pass

# Good: Type hints
def classify_severity(pressure_drop: float, flow_dev: float) -> str:
    pass

# Good: Comments for complex logic
# Calculate pressure gradient using finite difference method
gradient = (pressure[i+1] - pressure[i]) / dx
```

### File Organization
```python
"""
Module docstring explaining what this file does.
"""

# Standard library imports
import os
from pathlib import Path
from datetime import datetime

# Third-party imports
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

# Local imports
from utils.config import MODEL_CONFIG
from utils.helpers import calculate_leak_cost

# Constants
THRESHOLD = 0.95

# Classes and functions
class LeakDetector:
    pass

def main():
    pass

# Script entry point
if __name__ == "__main__":
    main()
```

## 🤝 Communication

### Team Channels
- **GitHub Issues**: Bug reports, feature requests
- **Pull Requests**: Code review discussions
- **Team Chat**: Quick questions, status updates
- **Stand-ups**: Daily progress sync

### Status Updates
Update [TEAM_GUIDE.md](TEAM_GUIDE.md) with your progress:
```markdown
| Member 1 | Isolation Forest | ✅ Must Have | 1-2h | ✅ Complete |
```

## 🆘 Getting Help

### Stuck on Something?
1. Check the model's README file
2. Look at [TEAM_GUIDE.md](TEAM_GUIDE.md) for common issues
3. Search GitHub Issues for similar problems
4. Ask in team chat
5. Create a GitHub Issue with details

### Quick Questions
- "How do I run the data generator?" → Check main README.md
- "My model won't import utils" → Check [TEAM_GUIDE.md](TEAM_GUIDE.md) Issue #1
- "Prophet won't install" → Check your model's README troubleshooting section

## 📚 Additional Resources

### Project Documentation
- [Main README](README.md) - Project overview
- [Team Guide](TEAM_GUIDE.md) - Collaboration guide
- [Strategy Doc](strategy_theme03.md) - Hackathon strategy

### Model-Specific READMEs
- [Model 01: Isolation Forest](models/01_isolation_forest/README.md)
- [Model 02: Severity Classifier](models/02_severity_classifier/README.md)
- [Model 03: Leak Size Estimator](models/03_leak_size_estimator/README.md)
- [Model 04: Acoustic Classifier](models/04_acoustic_classifier/README.md)
- [Model 05: Predictive Forecast](models/05_predictive_forecast/README.md)
- [Dashboard Guide](dashboard/README.md)

### External Resources
- [scikit-learn Documentation](https://scikit-learn.org/)
- [TensorFlow/Keras Guide](https://www.tensorflow.org/guide)
- [Prophet Documentation](https://facebook.github.io/prophet/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🏆 Best Practices

### For Fast Hackathon Development
1. **Start Simple**: Get a baseline working first, optimize later
2. **Commit Often**: Small, frequent commits are better than large ones
3. **Document as You Go**: Add comments while coding, not after
4. **Help Others**: If you finish early, assist teammates
5. **Test Integration**: Make sure your model works with others
6. **Think Demo**: Build with the presentation in mind

### Code Quality
- Write clear variable names
- Add docstrings to functions
- Include error handling
- Log important steps
- Save intermediate results

### Collaboration
- Communicate blockers early
- Review others' PRs promptly
- Share useful findings
- Ask questions - no question is stupid
- Celebrate wins together 🎉

---

## 📜 License

This project is for hackathon purposes. All team members retain equal rights to the code.

---

**Questions?** Open an issue or ask in team chat!

**Happy Coding! 🚀**
