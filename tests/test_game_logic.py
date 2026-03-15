from logic_utils import check_guess, get_range_for_difficulty, update_score

def test_winning_guess():
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# Bug fix: Normal (1-50) must be easier than Hard (1-100)
def test_normal_range_is_smaller_than_hard():
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert normal_high < hard_high, (
        f"Normal range (1-{normal_high}) should be smaller than Hard range (1-{hard_high})"
    )


# Bug fix: string comparison of secret caused inverted hints on even attempts.
# e.g. guess=3, secret=50 -> str "3" > "50" lexicographically -> wrongly "Too High"
def test_hint_not_inverted_by_string_comparison():
    # guess=3 is below secret=50; must be "Too Low", not "Too High"
    outcome, _ = check_guess(3, 50)
    assert outcome == "Too Low", (
        "guess 3 < secret 50 should be Too Low, not Too High "
        "(string comparison '3' > '50' is True, which was the bug)"
    )


def test_hint_direction_below_secret():
    outcome, message = check_guess(10, 80)
    assert outcome == "Too Low"
    assert "HIGHER" in message


def test_hint_direction_above_secret():
    outcome, message = check_guess(90, 20)
    assert outcome == "Too High"
    assert "LOWER" in message


# FIX: Tests written with Claude Code to verify score never goes negative.
# User spotted the issue in reflection.md; Claude generated the test cases covering
# zero-floor behavior for both "Too Low" and odd-attempt "Too High" outcomes.
def test_score_never_goes_negative_on_too_low():
    # Start at 0, "Too Low" should not drop below 0
    score = update_score(0, "Too Low", attempt_number=1)
    assert score >= 0, f"Score went negative: {score}"


def test_score_never_goes_negative_on_too_high_odd_attempt():
    # Odd attempt + "Too High" subtracts 5 — should floor at 0
    score = update_score(0, "Too High", attempt_number=1)
    assert score >= 0, f"Score went negative: {score}"


def test_score_decrements_but_floors_at_zero():
    # Repeated wrong guesses starting from a small score
    score = 3
    score = update_score(score, "Too Low", attempt_number=1)
    assert score == 0, f"Expected 0, got {score}"


def test_score_decrements_normally_when_above_zero():
    # Score above 5 should subtract correctly
    score = update_score(20, "Too Low", attempt_number=1)
    assert score == 15


def test_score_even_too_high_adds_points():
    # Even attempt + "Too High" should still add points
    score = update_score(10, "Too High", attempt_number=2)
    assert score == 15
