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
        # any guess must:
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


def score_guess(possibilities: str, guess: str, best_score: int = None):
    """Computes the size of the largest possible space of viable solutions under any single
    solution.

    For every given possible solution,
        compute how many words remain after using this guess against that solution.

    Returns the largest space of viable solutions under each solution.

    The "max" part of minimax.
    """
    # returns the size largest possible space of possible words under any possible solution

    max_possibilities = -1
    for possible_soln in possibilities:
        feedback = generate_feedback(possible_soln, guess)  # gets green pairs, yellow pairs, gray letters
        # filters possibilities to those consistent with this feedback and counts them
        remaining = len(list(filter(word_consistent(*feedback), possibilities)))

        if best_score is not None and remaining > best_score:
            # abort search, since it is already higher than the current lowest.
            return remaining

        if remaining > max_possibilities:
            max_possibilities = remaining

    assert max_possibilities != -1
    return max_possibilities


def select_guess(possibilities: str) -> str:
    current_minimax = None
    current_minimax_word = None

    print(f"Selecting best guess out of {len(possibilities)} possibilities...")

    for possible_guess in tqdm.tqdm(possibilities):
        # compute worst-case space of possibilities for this guess
        score = score_guess(possibilities, possible_guess, best_score=current_minimax)

        # update running minimax if appropriate
        if current_minimax is None or score < current_minimax:
            current_minimax = score
            current_minimax_word = possible_guess

    return (current_minimax_word, current_minimax)


if __name__ == "__main__":
    all_words = load_words()

    possibilities = all_words
    for i in range(6):
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
