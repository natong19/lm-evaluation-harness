from lm_eval.multiple_choice_utils import SINGLE_ANSWER_TEMPLATE_COT, parse_answers, prompt


def doc_to_text(doc: dict):
    question = doc["question"].strip()
    choices = doc["choices"]
    formatted = prompt(question, choices, SINGLE_ANSWER_TEMPLATE_COT)
    return formatted


def process_results(doc: dict, results: list[str]) -> dict:
    completion = results[0]
    num_choices = len(doc["choices"])
    parsed_answers = parse_answers(completion, num_choices=num_choices, multiple_correct=False)
    
    correct_answer = ["A","B","C","D"][doc["answer"]]
    
    is_correct = correct_answer in parsed_answers
    
    return {
        "exact_match": int(is_correct),
    }
