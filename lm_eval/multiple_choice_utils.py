import random
import re
from typing import Optional

import datasets


SINGLE_ANSWER_TEMPLATE_COT = """
Answer the following multiple choice question. The last line of your response should be of the following format: 'ANSWER: [LETTER]' (without quotes) where [LETTER] is one of {letters}. Think step by step before answering.

{question}

{choices}
""".strip()


def answer_options(choices: list[str]) -> str:
    r"""
    Returns the `choices` formatted as a multiple choice question, e.g.:

    ["choice 1", "choice 2", "choice 3"] ->
        "A) choice 1\nB) choice 2\nC) choice 3"
    """
    indexes = list(range(len(choices)))

    return '\n'.join([f'{answer_character(i)}) {choices[j]}' for i, j in enumerate(indexes)])


def format_letter_choices(choices: list[str]) -> str:
    """
    Returns the `choices` formatted as a letter list, e.g.:

    ["choice 1", "choice 2", "choice 3"] ->
        "A,B,C"
    """
    indexes = list(range(len(choices)))

    return ','.join([f'{answer_character(i)}' for i in indexes])


def prompt(question: str, choices: list[str], template: str, fewshot: Optional[str] = None) -> str:
    choices_text = answer_options(choices)
    letters = format_letter_choices(choices)
    if not fewshot:
        return template.format(
            choices=choices_text,
            letters=letters,
            question=question,
        )
    else:
        return template.format(
            choices=choices_text,
            letters=letters,
            question=question,
            fewshot=fewshot,
        )


def _fallback_parse_answer(completion: str) -> Optional[set[str]]:
    # Fallback to find the last upper case letter
    for letter in reversed(completion):
        if letter.isupper():
            return {letter}
    return None


def parse_answers(completion: str, num_choices: int = 4, multiple_correct: bool = False) -> set[str]:
    """
    Convenience function for extracting answers from the model output.

    The generated response must be in the format 'ANSWER: <answers>',
    otherwise we can't extract what the model thinks is "true". We can be a
    bit flexible whether these are "AB" vs "A,B" vs "A B".

    However, if the answer isn't in the expected format the model has
    failed in the task so we'll ultimately just mark it as incorrect
    """
    # First check whether the string strictly ends with the expected answer
    # In this case, we're looking for a single line which contains the expected
    # ANSWER: <answer> string with only whitespace or a period/full stop at the end.
    match = re.search(
        r'(?i)^ANSWER\s*:\s*([A-Za-z\d ,]+)\s*(?:$|\n|\.)',
        completion,
        flags=re.MULTILINE,
    )

    # If we couldn't match the strict version, we can try the less strict
    # version for backward compatibility
    if match is None:
        match = re.search(
            r'(?i)ANSWER\s*:\s*([A-Za-z\d ,]+)(?:[^\w]|\n|$|\.)',
            completion,
        )

    if match is None:
        fallback_answer = _fallback_parse_answer(completion)
        if fallback_answer:
            return fallback_answer

    if match is None:
        return set()

    matched = match.group(1)

    # Strip trailing period / full stop
    matched = matched.strip()
    matched = matched.rstrip('.')

    # Build allowed options based on num_choices (e.g., {"A", "B", "C", "D"} for 4 choices)
    allowed_options = set(answer_character(i) for i in range(num_choices))

    if multiple_correct:
        # Match must contain only the allowed choices
        # (may be separated by commas, spaces, the word 'and', or nothing at all)

        matched = matched.replace(' and ', '')

        matched = matched.replace(' ', '')

        split_comma = set(matched.split(','))
        if split_comma.issubset(allowed_options):
            answers = split_comma
            return answers

        split_nothing = set(matched)
        if split_nothing.issubset(allowed_options):
            answers = split_nothing
            return answers

    else:
        # Match must contain a single letter in the allowed choices
        # Uppercase for case-insensitive matching
        matched_upper = matched.upper()
        if matched_upper in allowed_options:
            answers = {matched_upper}
            return answers

    return set()


def answer_character(index: int) -> str:
    r"""
    Helper to go from array index to char, for example:

        0 -> 'A', 1 -> 'B', etc
    """
    if index < 26:
        return chr(ord('A') + index)
    else:
        return str(index - 25)
