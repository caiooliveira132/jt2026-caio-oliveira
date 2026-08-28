from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT.parent / "jovens-talentos-2026-hackathon-data" / "data"

RAW_FILES = {
    "details": DATA_DIR / "Details_Itapema.csv",
    "hosts": DATA_DIR / "Hosts_ids_Itapema.csv",
    "mesh": DATA_DIR / "Mesh_Ids_Data_Itapema.csv",
    "price": DATA_DIR / "Price_AV_Itapema.csv",
    "vivareal": DATA_DIR / "VivaReal_Itapema.csv",
}

OUTPUT_DIR = ROOT / "output"
AI_LOG_DIR = ROOT / "ai-log"

for _d in (OUTPUT_DIR, AI_LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)