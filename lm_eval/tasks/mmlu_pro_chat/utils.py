from functools import partial
from typing import Optional
import re

from lm_eval.multiple_choice_utils import SINGLE_ANSWER_TEMPLATE_COT, parse_answers, prompt


def doc_to_text(doc: dict):
    question = doc["question"].strip()
    choices = doc["options"]
    formatted = prompt(question, choices, SINGLE_ANSWER_TEMPLATE_COT)
    return formatted


def process_docs(dataset, subject):
    return dataset.filter(lambda x: x["category"] == subject)


process_biology = partial(process_docs, subject="biology")
process_business = partial(process_docs, subject="business")
process_chemistry = partial(process_docs, subject="chemistry")
process_computer_science = partial(process_docs, subject="computer science")
process_economics = partial(process_docs, subject="economics")
process_engineering = partial(process_docs, subject="engineering")
process_health = partial(process_docs, subject="health")
process_history = partial(process_docs, subject="history")
process_law = partial(process_docs, subject="law")
process_math = partial(process_docs, subject="math")
process_other = partial(process_docs, subject="other")
process_philosophy = partial(process_docs, subject="philosophy")
process_physics = partial(process_docs, subject="physics")
process_psychology = partial(process_docs, subject="psychology")


def process_results(doc: dict, results: list[str]) -> dict:
    completion = results[0]
    num_choices = len(doc["options"])
    parsed_answers = parse_answers(completion, num_choices=num_choices, multiple_correct=False)

    correct_answer = doc["answer"]
    match = re.search(r'([A-Za-z])', correct_answer)
    if match:
        correct_answer = match.group(1).upper()
    
    is_correct = correct_answer in parsed_answers
    
    return {
        "exact_match": int(is_correct),
    }
