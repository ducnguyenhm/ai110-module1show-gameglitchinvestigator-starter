# FIX: Normal (1-50) and Hard (1-100) ranges were swapped in the original.
# Spotted the bug by reading reflection.md; corrected the values with Claude Code.
def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


# FIX: Refactored all core logic out of app.py into this module.
# Used Claude Code to move each function; app.py now contains only UI code.
def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


# FIX: Hint messages were inverted — "Go HIGHER!" when guess was too high, etc.
# Identified the bug by reading reflection.md; swapped the messages with Claude Code.
def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        else:
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        # FIX: Wrapped subtraction in max(0, ...) to prevent negative scores.
        # Identified by user reviewing reflection.md; fix applied with Claude Code.
        return max(0, current_score - 5)

    if outcome == "Too Low":
        # FIX: Same floor-at-zero fix applied here for consistency.
        # Identified by user reviewing reflection.md; fix applied with Claude Code.
        return max(0, current_score - 5)

    return current_score
