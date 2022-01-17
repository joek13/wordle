import re
import collections
import typing
import tqdm


def load_words(wordlist_path: str) -> typing.List[str]:
    """Loads wordlist from a newline-delimited file."""
    with open(wordlist_path, "r") as f:
        return [line.strip() for line in f.readlines()]


# type alias for pair of (int, str)
# (p, l) represents a letter l in position p
PositionLetterPair = typing.Tuple[int, str]


def word_consistent(green_pairs: typing.List[PositionLetterPair],
                    yellow_pairs: typing.List[PositionLetterPair],
                    gray_pairs: typing.List[PositionLetterPair]) -> typing.Callable[[str], bool]:
    """Returns a predicate testing whether a given word is consistent with observed feedback."""
    def pred(word):
        # count the letters in word
        letter_counts = collections.Counter()
        for letter in word:
            letter_counts[letter] += 1

        # any viable solution must:
        # have letter l at position p for any green pair (p, l)
        for (p, l) in green_pairs:
            if word[p] != l:
                # green pair does not match
                return False
            else:
                letter_counts[l] -= 1

        # not have letter l at position p for any yellow pair (p, l)
        for (p, l) in yellow_pairs:
            if word[p] == l:
                # letter does match, but it shoudn't
                return False
            else:  # ...and contain letter l somewhere, aside from a green space
                # doesn't contain this letter,
                # or perhaps doesn't contain it enough times
                if letter_counts[l] <= 0:
                    return False
                else:
                    letter_counts[l] -= 1

        # contain no gray letters
        for (p, l) in gray_pairs:
            if letter_counts[l] != 0:
                return False

        return True

    return pred


def generate_feedback(soln: str, guess: str) -> typing.Tuple[typing.List[PositionLetterPair],
                                                             typing.List[PositionLetterPair],
                                                             typing.List[PositionLetterPair]]:
    """Returns the feedback from guessing `guess` when the solution is `soln`.
    The feedback is returned as a tuple of (green (pos, letter) pairs, yellow (pos, letter) pairs, set of gray letters)
    """
    # sanity check
    assert len(soln) == len(guess)

    # counts all the letters in the solution word
    letter_counts = collections.Counter()
    for letter in soln:
        letter_counts[letter] += 1

    # selects all (position, letter) pairs where the letters in soln and guess are equal
    green_pairs = [(p1, soln_letter) for ((p1, soln_letter), guess_letter)
                   in zip(enumerate(soln), guess) if soln_letter == guess_letter]

    # subtract the green letters from the letter counts,
    # since green letters "use up" letters from the solution word.
    for (_, letter) in green_pairs:
        letter_counts[letter] -= 1

    yellow_pairs = []
    for pos, letter in enumerate(guess):
        # there are excess letters that aren't already marked green
        if letter_counts[letter] > 0 and (pos, letter) not in green_pairs:
            # append this pair
            yellow_pairs.append((pos, letter))
            # subtract one from excess letter count; yellow letters "use up" solution word letters.
            letter_counts[letter] -= 1

    # all remaining pairs are gray
    gray_pairs = [pair for pair in enumerate(guess) if pair not in green_pairs and pair not in yellow_pairs]

    return green_pairs, yellow_pairs, gray_pairs


def select_guess(guesses: typing.List[str],
                 candidates: typing.List[str]) -> typing.Tuple[str, int]:
    """Selects a guess based on minimax decision rule.

    Returns tuple of (word, max), where word is the guess, and max is
    the maximum possible of remaining candidates after guessing `word`.
    """
    current_minimax = None
    current_minimax_word = None

    print(f"Selecting best guess from {len(guesses)} possibilities...")

    for guess in tqdm.tqdm(guesses):
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
    all_solutions = load_words("./solutions.txt")  # load possible solution words
    all_guesses = all_solutions + load_words("./guesses.txt")  # load additional guess words

    # initialize space of candidates to all puzzle solutions
    candidates = all_solutions
    for i in range(6):
        if i > 0:
            guess, worst_case = select_guess(all_guesses, candidates)
        else:
            # hard-code first guess to save on processing time
            guess, worst_case = "arise", 168  # values obtained simply by running the code without this optimization

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
        assert len(input_gray) == 5
        gray_pairs = [
            (position, letter.lower()) for (position, letter) in enumerate(input_gray) if letter.isalpha()
        ]

        pred = word_consistent(green_pairs, yellow_pairs, gray_pairs)
        candidates = list(filter(pred, candidates))

        if len(candidates) == 1:
            print("The word is:", candidates[0].upper())
            break
        elif len(candidates) < 1:
            print("The puzzle is impossible! Perhaps you entered results incorrectly?")
            break
