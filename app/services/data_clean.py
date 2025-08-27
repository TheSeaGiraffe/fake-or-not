import re

from demoji import replace

USER_MENTIONS_PATTERN = re.compile(r"(?:@)\S+")
URL_PATTERN = re.compile(r"(?:https?://)\S+")
HASHTAG_PATTERN = re.compile(r"(?:#)\S+")
WHITESPACE_PATTERN = re.compile(r"\s{2,}")


def clean_text(text: str) -> str:
    """Clean text

    Perform the same data cleaning operations for cleaning the data used to train the
    misinformation detection model on `text`. These operations are:

    - Converting text to lowercase
    - Removing emojis
    - Replacing URLs, mentions, and hashtags with placeholders
    - Removing excess whitespace

    Parameters
    ----------
    text: str
        The text to be cleaned

    Returns
    -------
    str
        The cleaned text
    """
    text_clean = text.lower()
    text_clean = replace(text_clean)
    text_clean = USER_MENTIONS_PATTERN.sub("<user>", text_clean)
    text_clean = URL_PATTERN.sub("<url>", text_clean)
    text_clean = HASHTAG_PATTERN.sub("<hashtag>", text_clean)
    text_clean = WHITESPACE_PATTERN.sub(" ", text_clean)
    text_clean = text_clean.lstrip()
    if not text_clean.endswith("\n"):
        text_clean += "\n"
    return text_clean


def clean_all_texts(texts: list[str]) -> list[str]:
    """Apply data cleaning operations to all texts in a list

    Parameters
    ----------
    texts: list[str]
        A list of texts

    Returns
    -------
    list[str]
        A list containing the cleaned text where each element directly corresponds to
        the element of `texts` at the same index.
    """
    return [clean_text(text) for text in texts]
