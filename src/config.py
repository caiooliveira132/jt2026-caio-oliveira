from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Dados: preferência à pasta local `data/` (repo autocontido).
# Fallback: clone irmão `../jovens-talentos-2026-hackathon-data/data`.
_LOCAL_DATA = ROOT / "data"
_SIBLING_DATA = ROOT.parent / "jovens-talentos-2026-hackathon-data" / "data"

DATA_DIR = _LOCAL_DATA if (_LOCAL_DATA / "Details_Itapema.csv").exists() else _SIBLING_DATA

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