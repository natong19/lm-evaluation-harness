from lm_eval.math_utils import extract_answer


def process_results(doc: dict, results: list[str]) -> dict:
    completion = results[0]
    extracted_completion = extract_answer(completion).lower().strip()
    answer = doc["answer"]
    extracted_answer = answer.split('### ')[-1].lower().strip()

    is_correct = extracted_completion == extracted_answer

    return {
        "exact_match": int(is_correct),
    }
