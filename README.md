# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- Explain your understanding of how real-world recommendations work
- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

- Real-world recommendations for songs are based on collaborative and content based filtering. Collaborative filtering is based on user behavior and preferences of similar users, such as liking preferences. This filtering is challenging for new song content since users have never interacted with the content before. That's where content filtering comes into play since that filtering is based on the attributes of the song itself, like is it fast/slow, tempo, genre, and other metadata. This also has its own issues if used alone like recommendations becoming predictable or repetitive. That's why real world systems combine both.
- My system focuses on the genre and mood for the categorical data, and the energy and the acousticness for the numerical data that feed into what song is ultimately recommended.
- UserProfile stores the favorite genre, favorite mood, target engery, and whether or not the user likes acoustics. This helps to determine a user's ideal song and helps the recommender to measure how far away a specific song is from the user's preference. 
- The recommender computes a score by combining three different steps as an accumulated score. The first is category matches which are exact indicators. We set an indicator variable as 1 or 0 based on string matching along with multiplying the weights (4 for genre, 2 for mood) to get a point value while also appending the reason for a score to the reasons list. The second part is the numerical closeness of a song to the user's preference. This is decided by taking the user's energy distance (abs(song energy - preferred energy)) and calculate the proximity score (1-energy distance) * weight of energy (1) while also appending the reason to the reasons list. The third step is for acoustics, if a user likes acoustics, 1 point is added when the track has an acoustic value >= .5 and if a user dislikes acoustics, 1 point is added when the track has an acoustic value < .5. These 3 point values are combined for a total score along with the reasons for the score.
- The songs with the highest point values are going to be the songs recommended first since these are the best matches to the user's preferences. We can then filter on a certain amount of top songs if desired.
- Potential biases in this system include over-prioritizing genre over mood since genre gets a weight of 4 and mood gets 2, giving a strong advantage to exact matches while under-valuing near misses, and making acousticness decisions with a simple threshold that may feel overly rigid. The model may also favor songs that are safe and similar to the profile rather than more exploratory recommendations, and because it is built from a small handcrafted dataset, it may reflect the dataset’s quirks more than broader listening preferences.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
User profile: genre=pop, mood=happy, energy=0.8, likes_acoustic=True

Top recommendations:

Sunrise City - Score: 6.98
Because: Genre matches your favorite genre; Mood matches your favorite mood; Energy score: 0.98 based on proximity to your target energy; Acousticness does not match your preference

Gym Hero - Score: 4.87
Because: Genre matches your favorite genre; Mood does not match your favorite mood; Energy score: 0.87based on proximity to your target energy; Acousticness does not match your preference

Rooftop Lights - Score: 2.96
Because: Genre does not match your favorite genre; Mood matches your favorite mood; Energy score: 0.96based on proximity to your target energy; Acousticness does not match your preference
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



