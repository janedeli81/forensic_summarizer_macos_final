# backend/classifiers.py

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple


def _normalize(s: str) -> str:
    """
    Lowercase + strip accents (justitiële -> justitiele),
    and keep it unicode-safe for both filenames and text.
    """
    s = (s or "").lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def _prep_for_search(s: str) -> str:
    """
    Normalize + make separators consistent so that:
      - "pv_vgl", "pv-vgl", "pv.vgl" become searchable
      - "vord.ibs" becomes "vord ibs"
    """
    s = _normalize(s)
    s = re.sub(r"[_\-.]+", " ", s)     # separators -> spaces
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _token_match(haystack: str, token: str) -> bool:
    """
    Match short abbreviations as standalone tokens:
      pv, vc, vgc, pj, ujd, tll, recl
    """
    token = re.escape(token)
    return re.search(rf"(?<![a-z0-9]){token}(?![a-z0-9])", haystack) is not None


def _match_rules(haystack: str, phrases: List[str], tokens: List[str]) -> Tuple[bool, str]:
    """
    phrases: substring match (good for longer phrases or glued words like "projustitia")
    tokens:  token/boundary match (good for pv/vc/pj/ujd/tll/recl)
    Returns (hit, matched_keyword)
    """
    for p in phrases:
        if p and p in haystack:
            return True, p
    for t in tokens:
        if t and _token_match(haystack, t):
            return True, t
    return False, ""


def classify_document(path: Path, text: str) -> str:
    """
    Classify document by filename (priority) and then by text (fallback).

    Returns one of:
      PJ, VC, PV, RECLASS, UJD, TLL, UNKNOWN
    """

    # --- prepare searchable strings ---
    name_search = _prep_for_search(path.name)
    # take a bit more than before, but still limited for speed
    content_search = _prep_for_search((text or "")[:8000])

    # --- rules based on client's nomenclature (screenshots) ---
    #
    # IMPORTANT: order matters because of overlaps:
    # - "verhoor raadkamer" must become VC, while "verhoor" alone is PV
    # - "pro justitia consult" / "nifp consult" must become VC, while "pro justitia" / "nifp" is PJ
    #
    RULES: List[Tuple[str, Dict[str, List[str]]]] = [
        # TLL / IBS (Indictment in their sheet, detected via IBS/vordering terms)
        (
            "TLL",
            {
                "phrases": [
                    "vordering tot inbewaringstelling",
                    "vordering inbewaringstelling",
                    "inbewaringstelling",
                    "vordering ibs",
                    "vorderingibs",
                    "vord ibs",
                    "vordibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    "vord ibs",
                    # also allow plain "ibs" (filename often contains IBS)
                    "ibs",
                ],
                "tokens": [
                    "tll",
                ],
            },
        ),

        # UJD
        (
            "UJD",
            {
                "phrases": [
                    "justitiele documentatie",
                    "uittreksel",
                    "uittreksel justitiele documentatie",
                ],
                "tokens": ["ujd"],
            },
        ),

        # RECLASS (probation / reclassering)
        (
            "RECLASS",
            {
                "phrases": [
                    "reclasseringsrapport",
                    "reclasseringsadvies",
                    "adviesrapportage toezicht",
                    "voortgangsrapportage",
                    "vroeghulp",
                    "reclassering",
                    "adviesrapportage",
                    "reclasserings",
                    "recl ",   # e.g. "recl. ..."
                    "recl.",
                ],
                "tokens": ["recl"],
            },
        ),

        # VC (psychiatrist consult / voorgeleidingsconsult)
        (
            "VC",
            {
                "phrases": [
                    "voorgeleidingsconsult",
                    "voor geleidingsconsult",
                    "voor geleidings consult",
                    "voor geleidingsconsult",
                    "voor geleidings consult",
                    "voorgeleiding rc",
                    "voor geleiding rc",
                    "voor geleiding rechter commissaris",
                    "voor geleiding rechter-commissaris",
                    "voorgeleiding rechter commissaris",
                    "voorgeleiding rechter-commissaris",
                    "verhoor raadkamer",
                    "stukken rc",
                    "pro justitia consult",
                    "projustitia consult",
                    "projustitiaconsult",
                    "nifp consult",
                    "nifpconsult",
                    # from the sheet (2nd screenshot)
                    "trajectconsult",
                    "traject consult",
                    # generic "voorgeleiding/voor geleiding" as VC per nomenclature
                    "voorgeleiding",
                    "voor geleiding",
                    "voor geleiding",
                ],
                "tokens": ["vc", "vgc"],
            },
        ),

        # PV (proces-verbaal / official report)
        (
            "PV",
            {
                "phrases": [
                    "proces verbaal",
                    "proces-verbaal",
                    "procesverbaal",
                    "pv vgl",
                    "pvvgl",
                    "nazending",
                    # keep "verhoor" for PV, but VC is checked earlier for "verhoor raadkamer"
                    "verhoor",
                ],
                "tokens": ["pv"],
            },
        ),

        # PJ (oude pro-justitia rapportage)
        (
            "PJ",
            {
                "phrases": [
                    "oude pj",
                    "oud pj",
                    "rapport pro justitia",
                    "pro justitia",
                    "projustitia",
                    # NIFP appears in PJ, but VC has priority for "nifp consult"
                    "nifp",
                ],
                "tokens": ["pj"],
            },
        ),
    ]

    # --- classification ---
    # First: filename
    for doc_type, rule in RULES:
        hit, kw = _match_rules(name_search, rule["phrases"], rule["tokens"])
        if hit:
            print(f"🔍 Herkend als {doc_type} via bestandsnaam met keyword: '{kw}'")
            return doc_type

    # Second: content (fallback)
    for doc_type, rule in RULES:
        hit, kw = _match_rules(content_search, rule["phrases"], rule["tokens"])
        if hit:
            print(f"🔍 Herkend als {doc_type} via tekstinhoud met keyword: '{kw}'")
            return doc_type

    print("⚠️ Geen type herkend — UNKNOWN")
    return "UNKNOWN"
