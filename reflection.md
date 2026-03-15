# 💭 Reflection: Game Glitch Investigator
Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
**Problems:**
- You cannot start a new game while the current game is in progress; a new game can only begin after the current one ends.
- List for history grows infinitely large -> does not reset between games.
- Negative scores -> scores should be positive.
- Current game modes (Normal and Hard are swapped):
    - Easy (0-20)
    - Normal (0-100)
    - Hard (0-50)
- So when you are below the secret number, it tells you to go lower. But when you are above the secret number, it tells you to go higher. -> should be reverse

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
Claude Code

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

Claude Code identified that `app.py` was converting the secret number to a string on every even-numbered attempt (`secret = str(st.session_state.secret)`), then passing that string into `check_guess`. This caused Python to use lexicographic ordering instead of numeric ordering — for example, `"3" > "50"` evaluates to `True` because `"3"` sorts after `"5"` alphabetically, so a guess of 3 against a secret of 50 would incorrectly return "Too High / Go LOWER". The AI suggested removing the conditional string conversion entirely and always passing the integer secret directly to `check_guess`. I verified this by running the pytest case `test_hint_not_inverted_by_string_comparison`, which calls `check_guess(3, 50)` and asserts the outcome is `"Too Low"` and it passed after the fix. I also confirmed manually in the running app that guessing a low number against a high secret now correctly shows "Go HIGHER".

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

When I first reported the inverted hints bug, Claude Code initially proposed swapping the message strings inside `check_guess` changing the `"Go LOWER!"` and `"Go HIGHER!"` text so that `guess > secret` returned `"Go HIGHER!"` instead. This was wrong: the condition `guess > secret` correctly identifies a too-high guess, and the message "Go LOWER!" is the right response. Swapping the strings would have made the messages read correctly in the broken even-attempt case, but would have broken the odd-attempt case and left the root cause (string comparison) untouched. I caught this by re-reading the bug description carefully — the problem was that the wrong branch was being triggered, not that the messages themselves were labelled incorrectly — and traced the issue back to the string coercion in `app.py`.


---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

A bug was considered fixed only when both a targeted pytest test passed and the behaviour was confirmed in the running app. Passing the test alone was not enough — I also checked the Developer Debug Info panel in the Streamlit sidebar to confirm the secret value and hint messages matched expectations during a live session.

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.

The most revealing test was `test_hint_not_inverted_by_string_comparison` in `tests/test_game_logic.py`. It calls `check_guess(3, 50)` — a guess far below the secret — and asserts the outcome is `"Too Low"`. Before the fix this test would have failed because the string conversion path made `"3" > "50"` evaluate to `True`, returning `"Too High"` instead. After removing the coercion the test passed, which confirmed the root cause was eliminated, not just the symptom. I also ran `test_normal_range_is_smaller_than_hard` to confirm the difficulty ranges were corrected: it asserts that Normal's upper bound is less than Hard's, which would have failed with the original swapped values.

- Did AI help you design or understand any tests? How?

Yes. Claude Code wrote all four new pytest cases targeting the two bugs. It explained why `test_hint_not_inverted_by_string_comparison` needed to use the specific values `guess=3, secret=50` — those numbers expose the lexicographic ordering flaw because `"3" > "50"` is `True` while `3 > 50` is `False`, making it a precise regression test rather than a generic direction check. That explanation helped me understand the difference between testing a symptom and testing the actual root cause.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Every time you interact with a Streamlit app — clicking a button, typing in a text box — the entire Python script reruns from top to bottom, like pressing refresh on a webpage. That means any regular variable you create gets thrown away and recreated from scratch on each rerun. `st.session_state` is Streamlit's solution: it is a dictionary that persists across reruns, so values you store there survive button clicks and page refreshes. The bug in this project was that clicking "New Game" reset the secret number but forgot to also reset `status` and `history` in `session_state`, so the game was still recorded as won or lost even after a fresh secret was generated. Think of `session_state` like a sticky note attached to the browser tab — everything else on the whiteboard gets erased each rerun, but the sticky note stays until you explicitly clear it.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

Writing regression tests that target the exact input that exposed a bug — not just any input that tests the general behavior. The test `test_hint_not_inverted_by_string_comparison` uses `guess=3, secret=50` specifically because those values make the difference between string and integer comparison visible (`"3" > "50"` is `True` while `3 > 50` is `False`). A generic test like `check_guess(40, 50)` would also pass after the fix, but it would not have caught the bug in the first place. Pinning the test to the failure case means it will catch any future regression that re-introduces the same flaw.

- What is one thing you would do differently next time you work with AI on a coding task?

I would ask the AI to explain its reasoning before applying any fix to logic-related bugs, rather than reviewing the change after the fact. When Claude first suggested swapping the hint message strings, I accepted the edit and then had to undo it once I traced the actual root cause. If I had asked "why does swapping the strings fix this?" upfront, I would have immediately seen that the explanation did not hold for odd-numbered attempts and caught the mistake before touching the file. Slowing down to question the AI's reasoning at the start is faster overall than cleaning up a wrong fix later.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

AI-generated code can look completely correct at a glance — clean structure, reasonable variable names, plausible logic — while containing subtle bugs that only appear under specific conditions, like the string-coercion trick that only triggered on even-numbered attempts. This project taught me to treat AI output the same way I would treat code written by a new teammate: readable first pass, but always verify the behavior against tests and the actual running program before trusting it.
