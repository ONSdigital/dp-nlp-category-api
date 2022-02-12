import numpy as np

def cosine_similarities(left, rights):
    return np.array([
        np.dot(
            left / np.linalg.norm(left),
            v / np.linalg.norm(v)
        )
        for v in rights
    ], dtype=np.float32)
