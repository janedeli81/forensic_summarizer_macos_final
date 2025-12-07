# classifiers.py

from pathlib import Path

def classify_document(path: Path, text: str) -> str:
    """
    Класифікує документ за ключовими словами в назві файлу (пріоритетно) та у тексті.
    Повертає один з: PJ, VC, PV, RECLASS, UJD, TLL, UNKNOWN.
    """

    name = path.name.lower()
    content = (text[:3000] or "").lower()

    # ✅ Мапінг ключових слів до типів
    KEYWORD_TO_TYPE = {
        # RECLASS
        "reclassering": "RECLASS", "reclasseringsrapport": "RECLASS",
        "reclasseringsadvies": "RECLASS", "adviesrapportage toezicht": "RECLASS",
        "vroeghulp": "RECLASS", "trajectconsult": "RECLASS",

        # VC
        "vc": "VC", "voorgeleidingsconsult": "VC", "voorgeleiding rc": "VC",
        "voorgeleiding rechter-commissaris": "VC", "verhoor raadkamer": "VC",

        # TLL
        "tll": "TLL", "vordering ibs": "TLL", "vord.ibs": "TLL",
        "vordering tot inbewaringstelling": "TLL",

        # UJD
        "ujd": "UJD", "justitiele documentatie": "UJD", "uittreksel": "UJD",

        # PV
        "pv": "PV", "proces-verbaal": "PV", "proces verbaal": "PV",
        "pv vgl": "PV", "voorgeleiding": "PV", "verhoor": "PV",

        # PJ
        "pj": "PJ", "pro justitia": "PJ", "rapport pro justitia": "PJ",
        "nifp": "PJ", "nifp consult": "PJ",
    }

    # ✅ Пріоритет типів (що важливіше)
    PRIORITY = ["RECLASS", "VC", "TLL", "UJD", "PV", "PJ"]

    # 🔍 Перевірка: спочатку у назві файлу
    for doc_type in PRIORITY:
        for keyword, mapped_type in KEYWORD_TO_TYPE.items():
            if mapped_type == doc_type and keyword in name:
                print(f"🔍 Herkend als {doc_type} via bestandsnaam met keyword: '{keyword}'")
                return doc_type

    # 🔍 Далі — у тексті
    for doc_type in PRIORITY:
        for keyword, mapped_type in KEYWORD_TO_TYPE.items():
            if mapped_type == doc_type and keyword in content:
                print(f"🔍 Herkend als {doc_type} via tekstinhoud met keyword: '{keyword}'")
                return doc_type

    print("⚠️ Geen type herkend — UNKNOWN")
    return "UNKNOWN"
