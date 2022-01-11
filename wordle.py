import re
import typing
import tqdm


def load_words(wordlist_path: str = "./words.txt") -> typing.List[str]:
    """Loads wordlist from a newline-delimited file."""
    with open(wordlist_path, "r") as f:
        return [line.strip() for line in f.readlines()]


# type alias for pair of (int, str)
# (p, l) represents a letter l in position p
PositionLetterPair = typing.Tuple[int, str]


def word_consistent(green_pairs: typing.List[PositionLetterPair],
                    yellow_pairs: typing.List[PositionLetterPair],
                    gray_letters: typing.Set[str]) -> typing.Callable[[str], bool]:
    """Returns a predicate testing whether a given word is consistent with observed:
    - green pairs (list of (position, letter) tuples)
    - yellow pairs (list of (position, letter) tuples)
    - gray letters (set of letters)
    """
    def pred(word):
        # any viable solution must:
        # - have letter l at position p for all green position-letter pairs (l, p)
        green_matches = all(word[p] == l for (p, l) in green_pairs)
        # - not have letter l at position p for any yellow position-letter pair (l, p)
        yellow_mismatches = not any(word[p] == l for (p, l) in yellow_pairs)
        # - contain letter l for all yellow position-letter pairs (l, p)
        yellow_letters = set(letter for (_, letter) in yellow_pairs)
        yellow_contains = all(l in word for l in yellow_letters)
        # - contain no gray letters l
        gray_absent = all(l not in word for l in gray_letters)

        return green_matches and yellow_mismatches and yellow_contains and gray_absent

    return pred


def generate_feedback(soln: str, guess: str) -> typing.Tuple[typing.List[PositionLetterPair], typing.List[PositionLetterPair], typing.Set[str]]:
    """Returns the feedback from guessing `guess` when the solution is `soln`.
    The feedback is returned as a tuple of (green (pos, letter) pairs, yellow (pos, letter) pairs, set of gray letters)
    """
    # sanity check
    assert len(soln) == len(guess)

    # selects all (position, letter) pairs where the letters in soln and guess are equal
    green_pairs = [(p1, soln_letter) for ((p1, soln_letter), guess_letter)
                   in zip(enumerate(soln), guess) if soln_letter == guess_letter]

    green_letters = set(letter for (_, letter) in green_pairs)

    # selects all (position, letter) pairs where the letter l from guess is
    # - in the soln word
    # - but not in the set of green letters

    yellow_pairs = [(p, guess_letter) for (p, guess_letter) in enumerate(
        guess) if guess_letter in soln and guess_letter not in green_letters]

    # all letters that are in the guess but not in the solution
    gray_letters = set(guess) - set(soln)

    return green_pairs, yellow_pairs, gray_letters


def select_guess(candidates: str) -> typing.Tuple[str, int]:
    """Selects guess among candidates based on minimax decision rule.
    Returns tuple of (word, max), where word is the guess, and max is
    the maximum possible of remaining candidates after guessing `word`.
    """
    current_minimax = None
    current_minimax_word = None

    print(f"Selecting best guess from {len(candidates)} possibilities...")

    for guess in tqdm.tqdm(candidates):
        # max loss for this guess
        maximum_remaining = None
        for possible_soln in candidates:
            # feedback guessing `guess` when the solution is `soln`
            feedback = generate_feedback(possible_soln, guess)
            # how many words remain after incorporating this feedback
            remaining = len(list(filter(word_consistent(*feedback), candidates)))

            # is this a new maximum loss?
            if maximum_remaining is None or remaining > maximum_remaining:
                maximum_remaining = remaining

            if current_minimax is not None and maximum_remaining > current_minimax:
                # the maximum for this guess is larger than the current minimax
                # not possible that this word represents a minimax, we can break early
                break

        if current_minimax is None or maximum_remaining < current_minimax:
            current_minimax = maximum_remaining
            current_minimax_word = guess

    return current_minimax_word, current_minimax


if __name__ == "__main__":
    all_words = load_words()  # load words from file

    possibilities = all_words
    while True:
        guess, worst_case = select_guess(possibilities)
        print(f"I suggest: {guess.upper()}, which leaves {worst_case} words at worst")

        input_green = input("Enter the green letters, using _ for blanks:   ")

        assert len(input_green) == 5
        green_pairs = [
            (position, letter.lower()) for (position, letter) in enumerate(input_green) if letter.isalpha()
        ]

        input_yellow = input("Enter the yellow letters, using _ for blanks:  ")

        assert len(input_yellow) == 5
        yellow_pairs = [
            (position, letter.lower()) for (position, letter) in enumerate(input_yellow) if letter.isalpha()
        ]

        input_gray = input("Enter the gray letters, using _ for blanks:    ")
        gray_letters = set(letter.lower() for letter in input_gray if letter.isalpha())

        pred = word_consistent(green_pairs, yellow_pairs, gray_letters)
        possibilities = list(filter(pred, possibilities))

        if len(possibilities) == 1:
            print("The word is:", possibilities[0].upper())
            break
        elif len(possibilities) < 1:
            print("The puzzle is impossible! Perhaps you entered results incorrectly?")
