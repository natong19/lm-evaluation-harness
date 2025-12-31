import logging
import re
import signal
from importlib.metadata import version
from typing import Dict, List, Optional

import datasets
from lm_eval.math_utils import extract_answer


def process_docs(dataset: datasets.Dataset) -> datasets.Dataset:
    def _process_doc(doc: dict) -> dict:
        out_doc = {
            "problem": doc["problem"],
            "solution": doc["solution"],
        }
        if getattr(doc, "few_shot", None) is not None:
            out_doc["few_shot"] = True
        return out_doc

    return dataset.map(_process_doc)


def process_results(doc: dict, results: list[str]) -> dict:
    completion = results[0]
    extracted_completion = extract_answer(completion).lower().strip()
    answer = doc["solution"]
    extracted_answer = extract_answer(answer).lower().strip()

    if re.match(r'^\([A-Za-z]\)$', extracted_completion):
        extracted_completion = extracted_completion[1]
    if re.match(r'^\([A-Za-z]\)$', extracted_answer):
        extracted_answer = extracted_answer[1]

    is_correct = extracted_completion == extracted_answer

    return {
        "exact_match": int(is_correct),
    }
