# backend/summarizer.py

from pathlib import Path
from typing import List
from backend.config import PROMPT_FILES, MAX_CHARS_PER_CHUNK, MODEL_PATH

from ctransformers import AutoModelForCausalLM

# Ініціалізація моделі (один раз)
llm = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH.parent,
    model_file=MODEL_PATH.name,
    model_type="mistral",  # або "llama" для llama-типу моделей
    max_new_tokens=1024,
    context_length=4096
)


def load_prompt(doc_type: str) -> str:
    path = PROMPT_FILES[doc_type]
    return path.read_text(encoding="utf-8")


def chunk_text(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> List[str]:
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start = end
    return chunks


def build_prompt(template: str, doc_text: str) -> str:
    if "<<<input>>>" in template:
        return template.replace("<<<input>>>", doc_text)
    elif "[TEKST_OM_SAMEN_TE_VATTEN]" in template:
        return template.replace(
            "[TEKST_OM_SAMEN_TE_VATTEN]",
            f"[TEKST_OM_SAMEN_TE_VATTEN]\n\n{doc_text}\n\n"
        )
    else:
        return template + "\n\n[TEKST_OM_SAMEN_TE_VATTEN]\n\n" + doc_text


def generate(prompt: str) -> str:
    return llm(prompt).strip()


def summarize_document(doc_type: str, text: str) -> str:
    template = load_prompt(doc_type)
    chunks = chunk_text(text)

    if len(chunks) == 1:
        prompt = build_prompt(template, chunks[0])
        return generate(prompt)

    partial_summaries = []
    for i, chunk in enumerate(chunks):
        prompt = build_prompt(template, chunk)
        summary = generate(prompt)
        partial_summaries.append(f"Deelsamenvatting {i + 1}:\n{summary}")

    combined = "\n\n".join(partial_summaries)

    meta_prompt = (
        "Je krijgt hieronder meerdere deelsamenvattingen van een langer document in het Nederlands.\n"
        "Maak op basis hiervan één samenhangende, professionele en formele samenvatting, "
        "alsof je dezelfde instructies volgt als in de oorspronkelijke prompt.\n\n"
        f"{combined}"
    )

    return generate(meta_prompt)
