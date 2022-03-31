import numpy as np


def cosine_similarities(left, rights):
    return np.array(
        [np.dot(left / np.linalg.norm(left), v / np.linalg.norm(v)) for v in rights],
        dtype=np.float32,
    )


def _get_snr(value, scored_list_len, scored_list_sum):
    return value * (scored_list_len - 1) / (scored_list_sum - value)


def filter_by_snr(scored_list, snr):
    scored_list_sum = sum(s for s, _ in scored_list)
    scored_list_len = len(scored_list)
    return [
        (s, l)
        for s, l in scored_list
        if _get_snr(s, scored_list_len, scored_list_sum) > snr
    ]
