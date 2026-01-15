"""
lien_stage_detector.py
Maps auction listings and portal data to a 0-7 severity scale.
"""

from typing import Dict, Any

# Stage Definitions as per README:
# 0: Normal
# 1: Past due
# 2: Lien warning
# 3: Placeholder sale date assigned
# 4: Legal notice published
# 5: Auction submitted
# 6: Auction scheduled
# 7: Auction live

def determine_lien_stage(listing: Dict[str, Any]) -> int:
    """
    Analyzes listing metadata to determine the current lien stage.
    
    Args:
        listing: Dictionary containing status, tags, and platform-specific metadata.
        
    Returns:
        int: A stage from 0 to 7.
    """
    status = listing.get("status", "").lower()
    tags = [t.lower() for t in listing.get("tags", [])]
    is_published = listing.get("is_published", False)
    
    # Stage 7: Auction Live
    if status == "live" or "active_bidding" in tags:
        return 7
    
    # Stage 6: Auction Scheduled
    if status == "scheduled" or "confirmed_date" in tags:
        return 6
    
    # Stage 5: Auction Submitted (Threshold for Alerting)
    if "submitted" in status or "pending_approval" in tags:
        return 5
    
    # Stage 4: Legal Notice Published
    if "newspaper_published" in tags or listing.get("legal_notice_verified"):
        return 4
    
    # Stage 3: Placeholder sale date assigned
    if listing.get("has_placeholder_date") or "auto_generated_date" in tags:
        return 3
        
    # Stage 2: Lien warning
    if "lien_notice_sent" in tags or "pre_auction" in status:
        return 2
        
    # Stage 1: Past due
    if "delinquent" in status or "overdue" in tags:
        return 1

    # Stage 0: Normal
    return 0
