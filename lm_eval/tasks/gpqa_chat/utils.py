import random
import re
from typing import Optional

import datasets
from lm_eval.multiple_choice_utils import SINGLE_ANSWER_TEMPLATE_COT, parse_answers, prompt


def preprocess(text):
    if text is None:
        return " "
    text = text.strip()
    text = text.replace(" [title]", ". ")
    text = re.sub("\\[.*?\\]", "", text)
    text = text.replace("  ", " ")
    return text


def process_docs(dataset: datasets.Dataset) -> datasets.Dataset:
    def _process_doc(doc):
        choices = [
            preprocess(doc["Incorrect Answer 1"]),
            preprocess(doc["Incorrect Answer 2"]),
            preprocess(doc["Incorrect Answer 3"]),
            preprocess(doc["Correct Answer"]),
        ]

        random.shuffle(choices)
        correct_answer_index = choices.index(preprocess(doc["Correct Answer"]))

        out_doc = {
            "choice1": choices[0],
            "choice2": choices[1],
            "choice3": choices[2],
            "choice4": choices[3],
            "choices": [choices[0], choices[1], choices[2], choices[3]],
            "answer": f"({chr(65 + correct_answer_index)})",
        }
        return out_doc

    return dataset.map(_process_doc)


def doc_to_text(doc: dict):
    question = doc["Question"].strip()
    choice1 = doc["choice1"]
    choice2 = doc["choice2"]
    choice3 = doc["choice3"]
    choice4 = doc["choice4"]
    choices = [choice1, choice2, choice3, choice4]
    formatted = prompt(question, choices, SINGLE_ANSWER_TEMPLATE_COT)
    return formatted


def process_results(doc: dict, results: list[str]) -> dict:
    completion = results[0]
    num_choices = len(doc["choices"])
    parsed_answers = parse_answers(completion, num_choices=num_choices, multiple_correct=False)
    
    correct_answer = doc["answer"]
    match = re.search(r'([A-Za-z])', correct_answer)
    if match:
        correct_answer = match.group(1).upper()

    is_correct = correct_answer in parsed_answers

    return {
        "exact_match": int(is_correct),
    }
