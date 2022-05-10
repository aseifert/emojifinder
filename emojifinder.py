from dataclasses import dataclass
from pathlib import Path
from typing import Union

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


@dataclass
class Emoji:
    symbol: str
    keywords: list[str]


def get_vectors(
    model: SentenceTransformer,
    emojis: list[Emoji],
    embeddings_path: Union[str, Path] = Path("embeddings.npy"),
) -> np.ndarray:
    if Path(embeddings_path).exists():
        # if npy file exists load vectors from disk
        embeddings = np.load(embeddings_path)
    else:
        # otherwise embed texts and save vectors to disk
        embeddings = model.encode(sentences=[" ".join(e.keywords) for e in emojis])
        np.save(embeddings_path, embeddings)

    return embeddings


def find_emoji(
    query: str,
    emojis: list[Emoji],
    model: SentenceTransformer,
    embeddings,
    n=1,
) -> list[Emoji]:
    """embed file, calculate similarity to existing embeddings, return top n hits"""
    embedded_desc: torch.Tensor = model.encode(query, convert_to_tensor=True)  # type: ignore
    sims = cos_sim(embedded_desc, embeddings)
    top_n = sims.argsort(descending=True)[0][:n]
    return [emojis[i] for i in top_n]
