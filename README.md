# WORDLE solver
A solver for the addictive [WORDLE](https://www.powerlanguage.co.uk/wordle/), an excellent word guessing game.

I wrote [a blog post](https://www.kerrigan.dev/2022/01/10/building-a-wordle-solver-in-python.html) about this solver here.

## Output
```
I suggest: ARISE, which leaves 168 words at worst
Enter the green letters, using _ for blanks:   _____
Enter the yellow letters, using _ for blanks:  a_i__
Enter the gray letters, using _ for blanks:    _r_se
Selecting best guess from 12972 possibilities...
I suggest: CANAL, which leaves 4 words at worst
Enter the green letters, using _ for blanks:   _an__
Enter the yellow letters, using _ for blanks:  c____
Enter the gray letters, using _ for blanks:    ___al
Selecting best guess from 12972 possibilities...
I suggest: HUMPH, which leaves 1 words at worst
Enter the green letters, using _ for blanks:   _____
Enter the yellow letters, using _ for blanks:  ___p_
Enter the gray letters, using _ for blanks:    hum_h
The word is: PANIC
```

## References
I used the following blog posts when building this:
- https://blog.scubbo.org/posts/cheating-at-word-games/
- https://twitter.com/cgenco/status/1479144204043444226
- https://matt-rickard.com/wordle-whats-the-best-starting-word/