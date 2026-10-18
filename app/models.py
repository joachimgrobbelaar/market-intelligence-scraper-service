from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ScrapeJobRequest(BaseModel):
    target_urls: List[str]
    proxy_tier: str = "rotating_residential"

class ScrapeJobResponse(BaseModel):
    job_id: str
    status: str
    target_count: int

class ScrapedItem(BaseModel):
    url: str
    extracted_price: float
    currency: str
    confidence: float
