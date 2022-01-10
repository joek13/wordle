-- reads words from words.txt, returning a list of strings
readWords :: IO [String]
readWords = lines <$> readFile "./words.txt"

main :: IO ()
main =
  do
    words <- readWords
    putStr (show words)