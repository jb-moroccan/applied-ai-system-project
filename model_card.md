# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

UserSongVibeFinder 1.0

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

This recommender is designed for classroom exploration and simple experiments. It suggests songs that fit a user’s genre, mood, energy, and acoustic taste. It assumes a user has a few clear preferences, even if those preferences are not perfect. It is not meant to replace a real music app.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

The system gives a score by checking how closely a song matches the user’s preferences. It looks at genre, mood, energy, and acousticness. A song gets more points when it matches more of these signals. I also changed the original logic by making the scoring more explicit and easier to explain.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The dataset includes 18 songs and a mix of genres, moods, and energy levels. Each song has features like genre, mood, energy, tempo, valence, danceability, and acousticness. The catalog is small, so the results are limited and some genres appear only once. This means the system cannot represent every kind of music taste.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The system works best when a user has clear and simple preferences. It can also be very good at catching broad patterns, such as high-energy pop or calm lofi. The recommendations often line up with what a user would expect when the preferences are straightforward.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

One weakness discovered during the experiment of doubling the energy weight and halving the genre weight is that the recommender became less clearly aligned with a user’s broader musical identity. Since the three categories were treated more evenly after the change, the system could feel less personalized for users whose genre preference is especially important to them. In those cases, the model may recommend songs that are acceptable across all categories but do not capture the user’s strongest taste signal as well as before. The recommender may be sensitive to sparse genre coverage because most genres appear only once, so a single genre match can have a large effect. Genre is weighted more heavily than mood in the scoring logic, so a user’s favorite genre can strongly influence the final ranking.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested three simple user profiles to see whether the recommender changed in sensible ways: a high-energy pop profile, a deep intense rock profile, and a chill lofi profile. The high-energy pop profile pushed the results toward bright, upbeat songs, while the chill lofi profile shifted them toward quieter, lower-energy tracks. The deep intense rock profile was useful because it tested whether the system would still favor strong, dramatic songs even when the musical style was different from the more obvious pop or lofi matches. One surprise was that the “Gym Hero” song kept appearing for the high-energy pop profile, because it scores well on several signals at once: it is pop, energetic, and upbeat. That made sense once I saw that the model values a strong overlap across multiple features, not just one exact genre match.

- High-energy pop profile vs. chill lofi profile: the high-energy pop profile favored brighter, more intense songs, while the chill lofi profile moved toward softer, lower-energy choices that feel more relaxed.
- High-energy pop profile vs. deep intense rock profile: both profiles liked strong energy, but the rock profile leaned more toward darker, heavier songs, while the pop profile stayed closer to upbeat and catchy tracks.
- Chill lofi profile vs. deep intense rock profile: these profiles produced very different outputs, which makes sense because one is built around calmness and one around intensity.
- “Gym Hero” example: this song kept showing up for the high-energy pop profile because it is a strong match for several broad preferences at once, so even a simple request like “happy pop” could still rank it highly.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

I would improve this model by adding more songs and a wider mix of genres. I would also make the scoring less rigid so small differences in energy or mood do not matter as much. Adding more features, such as artist or tempo preferences, could make the results feel more personal.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

This project helped me see how recommender systems can seem smart while still being simple and biased. I was surprised by how much one song could rise in the rankings when it matched several features at once. It also showed me that small design choices can change recommendations a lot, like changing the weight values for the scoring algorithm.
