import typing
import tqdm


def load_words(wordlist_path: str = "./words.txt") -> typing.List[str]:
    """Loads wordlist from a newline-delimited file."""
    with open(wordlist_path, "r") as f:
        return [line.strip() for line in f.readlines()]


def word_consistent(green_pairs: typing.List[typing.Tuple[int, str]], yellow_pairs: typing.List[typing.Tuple[int, str]], gray_letters: typing.Set[str], word: str):
    """Predicate that tests whether a given word is consistent with observed:
    - green pairs (list of (index, letter) tuples)
    - yellow pairs (list of (index, letter) tuples)
    - gray letters (set of letters)
    """
    # compute sets of green/yellow letters
    yellow_letters = set(letter for (_, letter) in yellow_pairs)

    # any guess must:
    # - have letter l at position p for all green letter-position pairs (l, p)
    green_matches = all(word[p] == l for (p, l) in green_pairs)
    # - not have letter l at position p for any yellow letter-position pair (l, p)
    yellow_mismatches = not any(word[p] == l for (p, l) in yellow_pairs)
    # - contain letter l for all yellow letter-position pairs (l, p)
    yellow_contains = all(l in word for l in yellow_letters)
    # - contain no gray letters l
    gray_absent = all(l not in word for l in gray_letters)

    return green_matches and yellow_mismatches and yellow_contains and gray_absent


def filter_possibilities(soln: str, guess: str, possibilities: typing.List[str]) -> typing.List[str]:
    """Filters possibilities to only those consistent with the information gleaned
    from guessing `guess` when the real solution is `soln`."""

    # sanity check
    assert len(soln) == len(guess)

    # selects all (letter, position) pairs where the letters in soln and guess are equal
    green_pairs = [(p1, soln_letter) for ((p1, soln_letter), guess_letter)
                   in zip(enumerate(soln), guess) if soln_letter == guess_letter]

    green_letters = set(letter for (_, letter) in green_pairs)

    # selects all (letter, position) pairs where the letter l from guess is
    # - in the soln word
    # - but not in the set of green letters
    # TODO: refine to consider repeated letters
    yellow_pairs = [(p, guess_letter) for (p, guess_letter) in enumerate(
        guess) if guess_letter in soln and guess_letter not in green_letters]

    # all letters that are in the guess but not in the solution
    gray_letters = set(guess) - set(soln)

    def word_pred(word):
        return word_consistent(green_pairs, yellow_pairs, gray_letters, word)

    return filter(word_pred, possibilities)


def filter_possibilities_guess(green_pairs: typing.List[typing.Tuple[int, str]], yellow_pairs: typing.List[typing.Tuple[int, str]], gray_letters: typing.Set[str], possibilities: typing.List[str]) -> typing.List[str]:
    """Filters possible solutions based on observed green pairs, yellow pairs, and gray letters.
    """
    def word_pred(word):
        return word_consistent(green_pairs, yellow_pairs, gray_letters, word)

    return filter(word_pred, possibilities)


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
        remaining = len(list(filter_possibilities(possible_soln, guess, possibilities)))

        if best_score is not None and remaining > best_score:
            # abort search, since it is already higher than the current lowest.
            return remaining

        if remaining > max_possibilities:
            max_possibilities = remaining

    assert max_possibilities != -1
    return max_possibilities


def next_guess(possibilities: str) -> str:
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
        if i > 0:
            guess, worst_case = next_guess(possibilities)
            print(f"I suggest: {guess.upper()}, which leaves {worst_case} words at worst")

        input_green = input("Enter the green letters, using _ for blanks: ")

        assert len(input_green) == 5
        green_pairs = [
            (position, letter.lower()) for (position, letter) in enumerate(input_green) if letter.isalpha()
        ]

        input_yellow = input("Enter the yellow letters, using _ for blanks: ")

        assert len(input_yellow) == 5
        yellow_pairs = [
            (position, letter.lower()) for (position, letter) in enumerate(input_yellow) if letter.isalpha()
        ]

        input_gray = input("Enter the gray letters, using _ for blanks: ")
        gray_letters = set(letter.lower() for letter in input_gray if letter.isalpha())

        possibilities = list(filter_possibilities_guess(green_pairs, yellow_pairs, gray_letters, possibilities))

        if len(possibilities) == 1:
            print("The word is:", possibilities[0].upper())
            break
        elif len(possibilities) < 1:
            print("The puzzle is impossible! Perhaps you entered results incorrectly?")
