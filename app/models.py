from pydantic import BaseModel
from typing import Optional

class Alert(BaseModel):
    """Raw JMA disaster alert data model."""
    id: str
    title: str
    summary: str
    link: str
    updated: str
    hash: Optional[str] = None  #stage 2
    ipfs_cid: Optional[str] = None #stage 2

class TranslatedAlert(Alert):
    """Alert with translations and trust scoring"""
    translated_title_en: Optional[str] = None
    translated_summary_en: Optional[str] = None
    translated_title_zh: Optional[str] = None
    translated_summary_zh: Optional[str] = None
    emergency_actions_en: Optional[str] = "Stay alert for further updates."
    emergency_actions_zh: Optional[str] = "请保持警惕，等待进一步更新。"
    trust_score: Optional[float] = None  # 0-10 score for Stage 3
    prefecture: Optional[str] = None  # e.g. "Tokyo"
    category: Optional[str] = None  # e.g. "Warning", "Advis
    ipfs_cid: Optional[str] = None

class Provenance(BaseModel):
    """Track source information for traceability"""
    source_url: str
    fetch_timestamp: str
    original_hash: str
    ipfs_cid: str