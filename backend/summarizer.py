# backend/summarizer.py

from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import re

from ctransformers import AutoModelForCausalLM
from backend.config import (
    PROMPT_FILES,
    MAX_CHARS_PER_CHUNK,
    MODEL_PATH,
    N_CTX,
    MAX_NEW_TOKENS,
    AGGREGATE_GROUP_SIZE,
    AGGREGATE_MAX_PARTIALS,
)

# === Глобальні змінні =========================================================
GPU_LAYERS = 20  # скільки шарів гнати на GPU; потім можна збільшити до 30–35

_llm = None
_effective_ctx = int(N_CTX)   # фактичний ліміт контексту; за замовчуванням беремо N_CTX

STOP_WORDS = [
    "<|user|>", "<|system|>",
    "</TEKST>", "</TEKST_WAAR_HET_OM_GAAT>",
    "JOUW ANTWOORD:", "JOUW ANTWOORD",
    "[TEKST_OM_SAMEN_TE_VATTEN]",
]

# === Завантаження моделі (БЕЗ config=dict) ===================================
def get_llm():
    """
    Завантажує TinyLlama через ctransformers.
    - НЕ використовуємо параметр config=..., щоб уникнути помилки 'dict has no attribute config'.
    - Передаємо context_length як ТОР-РІВНЕВИЙ kwargs (як підтримує ctransformers).
    """
    global _llm
    if _llm is not None:
        return _llm

    mp = Path(str(MODEL_PATH))
    if not mp.exists():
        raise FileNotFoundError(f"LLM model not found: {mp}")

    if mp.is_file():
        _llm = AutoModelForCausalLM.from_pretrained(
            str(mp.parent),               # model_path_or_repo_id (папка)
            model_file=mp.name,           # ім’я .gguf
            model_type="mistral",
            gpu_layers=0,
            context_length=int(N_CTX),    # <-- безпечно для нових/старих збірок
        )
    else:
        _llm = AutoModelForCausalLM.from_pretrained(
            str(mp),                      # папка з .gguf
            model_type="mistral",
            gpu_layers=GPU_LAYERS,
            context_length=int(N_CTX),
        )
    print(f"[summarizer] model loaded, requested context_length={int(N_CTX)}")
    return _llm

# === Утиліти ==================================================================
def _count_tokens_rough(s: str) -> int:
    # ~1 токен / 3.6 символа для LLaMA-подібних
    return max(1, int(len(s) / 3.6))

def _sanitize(s: str) -> str:
    s = (s or "").replace("\r\n", "\n")
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"(?i)Pagina\s+\d+\s+van\s+\d+\s*", "", s)
    s = re.sub(r"(?im)^\s*Retouradres.*$", "", s)
    # прибираємо зайві ** із PDF-екстракції
    s = s.replace("**", "")
    return s.strip()

def _chatml(system_msg: str, user_msg: str) -> str:
    # Лаконічна system-роль, щоб не провокувати ехо "Je bent..."
    return f"<|system|>\n{system_msg}\n<|user|>\n{user_msg}\n<|assistant|>\n"

def _chunk(text: str, max_chars: int) -> List[str]:
    t = (text or "").strip()
    if not t:
        return []
    out: List[str] = []
    i, n = 0, len(t)
    while i < n:
        piece = t[i : i + max_chars]
        j = piece.rfind("\n")
        if j > int(max_chars * 0.6):
            piece = piece[:j]
        out.append(piece.strip())
        i += len(piece)
    return out

def _load_template(doc_type: str) -> str:
    path = PROMPT_FILES.get(doc_type.upper()) or PROMPT_FILES["UNKNOWN"]
    return Path(path).read_text(encoding="utf-8")

def _wrap_user(template: str, body: str, max_sents: int = 4) -> str:
    return (
        template.strip()
        + "\n[TEKST]\n"
        + (body or "").strip()
        + "\n</TEKST>\n"
        + f"Geef maximaal {max_sents} zinnen."
    )

def _fit_prompt_to_ctx(system_msg: str, template: str, body: str, target_ctx: int) -> str:
    """
    Будує ChatML і, якщо довго, поступово ріже body під target_ctx.
    """
    ch = (body or "").strip()
    # 90% від ліміту — запас на службові токени
    limit = max(256, int(target_ctx * 0.90))
    while True:
        user_msg = _wrap_user(template, ch, max_sents=4)
        prompt = _chatml(system_msg, user_msg)
        if _count_tokens_rough(prompt) <= limit or len(ch) < 200:
            return prompt
        ch = ch[: int(len(ch) * 0.85)]  # зменшуємо на 15%

def _reduce_group(summaries: List[str], system_msg: str, target_ctx: int) -> str:
    user = (
        "Vat de volgende deelsamenvattingen samen tot één tekst van max. 4 zinnen.\n\n"
        + "\n\n".join(f"— {i+1}. {t}" for i, t in enumerate(summaries))
    )
    prompt = _chatml(system_msg, user)
    if _count_tokens_rough(prompt) > int(target_ctx * 0.90):
        summaries = summaries[: max(1, len(summaries) // 2)]
        user = "Vat kort samen (max. 3 zinnen):\n\n" + "\n\n".join(summaries)
        prompt = _chatml(system_msg, user)
    return _generate(prompt).strip()

def _clean_echo(txt: str) -> str:
    t = (txt or "").strip()
    # прибрати рядки, що починаються із системної інструкції
    t = re.sub(r"(?i)^\s*je bent.*?\n", "", t)
    # згорнути надмірні повтори "je bent ..."
    t = re.sub(r"(?i)(\bje bent\b[\s,;:.!?]*){2,}", "Je bent ", t)
    return t.strip()

# === Генерація ================================================================
def _generate(prompt: str, *, max_new: Optional[int] = None) -> str:
    llm = get_llm()
    return llm(
        prompt,
        max_new_tokens=int(max_new or MAX_NEW_TOKENS),
        temperature=0.2,
        top_p=0.9,
        repetition_penalty=1.15,
        stop=STOP_WORDS,
    )

# === Публічний інтерфейс ======================================================
def summarize_document(
    doc_type: str,
    doc_text: Optional[str] = None,
    **kwargs,
) -> str:
    """
    1) MAP: короткі саммарі шматків із підрізанням під доступний контекст.
    2) REDUCE: ієрархічне зведення групами.
    Сумісність: приймає doc_text=..., text=..., document_text=...
    """
    global _effective_ctx
    if doc_text is None:
        doc_text = kwargs.get("text") or kwargs.get("document_text") or ""

    template = _load_template(doc_type)
    text = _sanitize(doc_text)

    # Спец-обрізання для TLL: відкинути все після "Overwegende"
    if doc_type.upper() == "TLL":
        m = re.search(r"(?i)\bOverwegende\b", text)
        if m:
            text = text[:m.start()].strip()

    chunks = _chunk(text, MAX_CHARS_PER_CHUNK)
    if not chunks:
        return "Geen tekst aangetroffen."

    # Лаконічна system-роль, щоб не ехо-копіювалась
    system_msg = "Schrijf een korte, professionele samenvatting in het Nederlands."

    target_ctx = int(_effective_ctx)  # на старті — те, що вказано у config.py

    # --- 1) MAP ---
    partials: List[str] = []
    for ch in chunks:
        # будуємо промпт під поточний target_ctx
        prompt = _fit_prompt_to_ctx(system_msg, template, ch, target_ctx)
        try:
            out = _generate(prompt).strip()
        except Exception as e:
            # Якщо збірка реально на 512/1024 — пробуємо авто-фолбек
            msg = str(e)
            if "maximum context length" in msg or "exceeded maximum context length" in msg:
                if "512" in msg:
                    target_ctx = _effective_ctx = 512
                elif "1024" in msg:
                    target_ctx = _effective_ctx = 1024
                else:
                    target_ctx = _effective_ctx = 768
                prompt = _fit_prompt_to_ctx(system_msg, template, ch, target_ctx)
                out = _generate(prompt, max_new=min(140, MAX_NEW_TOKENS)).strip()
            else:
                raise
        partials.append(_clean_echo(out))

    # обрізаємо кількість часткових у фіналі — гарантія, що все влізе
    if len(partials) > AGGREGATE_MAX_PARTIALS:
        partials = partials[:AGGREGATE_MAX_PARTIALS]

    # --- 2) REDUCE (ієрархічно) ---
    while len(partials) > 1:
        grouped: List[str] = []
        for i in range(0, len(partials), AGGREGATE_GROUP_SIZE):
            grouped.append(_reduce_group(partials[i : i + AGGREGATE_GROUP_SIZE], system_msg, target_ctx))
        partials = grouped

    return partials[0] if partials else ""
