# 🎵 Music Recommender Simulation - Applied AI System Enhancement

## Project Summary

The original music recommender simulation was built to represent songs and a user taste profile as data. It also contained a scoring rule that turned the data from the genre, mood, and energy into top song recommendations with reasoning as to why these songs are the best matches. When looking for the top songs, I originally limited it to the top 3 for each profile since the later suggestions were not as strong matches. With the new improvements to this project, I added reliability scoring and a self-critique loop to provide some testing and confidence scoring so that a user would feel confident that the songs suggested match their profile or even get new recommendations that better fit based on the reliability mechanism.

---

## Architecture Overview

### TODO: A short explanation of your system design

---

## Getting Started

### Setup Instructions

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Run the app:

```bash
python -m src.main
```

3. Run the starter tests with:

```bash
pytest
```

Tests are located in `tests/test_recommender.py`.

---

## Sample Interactions

### TODO: Include at least 2-3 examples of inputs and the resulting AI outputs to demonstrate the system is functional

```

```

---

## Reliability and Evaluation

### TODO: Your AI should prove that it works, not just seem like it does. Include at least one way to test or measure its reliability, such as:

### Automated tests (e.g., unit tests or simple checks for key functions).
### Confidence scoring (the AI rates how sure it is).
### Logging and error handling (your code records what failed and why).
### Human evaluation (you or a peer review the AI's output).

### Summarize your testing in a few lines, like:

### 5 out of 6 tests passed; the AI struggled when context was missing. Confidence scores averaged 0.8; accuracy improved after adding validation rules.


| **Test Input** | **Evaluation Criteria** | **Result** |
| -------- | -------- | -------- |
| Row 1 A  | Row 1 B  | Row 1 C  |
| Row 2 A  | Row 2 B  | Row 2 C  |
| Row 3 A  | Row 3 B  | Row 3 C  |

### TODO: What surprised you while testing your AI's reliability?

## Design Decisions

### TODO: Why you built it this way, and what trade-offs you made

```

```

---

## Limitations and Risks

### TODO: What worked, what didn't, and what you learned

```

```

---

## Reflection

Responsible AI reflection is in `model_card.md`:

[**Model Card**](model_card.md)

### TODO: A brief note on what this project taught you about AI and problem-solving. Describe what this project says about you as an AI engineer
