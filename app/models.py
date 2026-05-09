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
    prefecture: Optional[str] = None  # extracted/filled by AI or heuristics
    category: Optional[str] = None  # Critical|Warning|Advisory

class TranslatedAlert(Alert):
    """Alert with translations and trust scoring"""
    translated_title_en: Optional[str] = None
    translated_summary_en: Optional[str] = None
    translated_title_zh: Optional[str] = None
    translated_summary_zh: Optional[str] = None
    emergency_actions_en: Optional[str] = None
    emergency_actions_zh: Optional[str] = None
    trust_score: Optional[float] = None  # 0-10 score for Stage 3
    # prefecture/category/hash/ipfs_cid inherited from Alert

class Provenance(BaseModel):
    """Track source information for traceability"""
    source_url: str
    fetch_timestamp: str
    original_hash: str
    ipfs_cid: str