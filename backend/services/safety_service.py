import logging

logger = logging.getLogger(__name__)

# List of forbidden keywords for content safety
# In a real app, this would be a more comprehensive list or an external API
BLOCKLIST = {
    "porn", "hentai", "xxx", "explicit", "nsfw", "adult", 
    "erotica", "gore", "sexual", "nude"
}

def is_safe(text: str) -> bool:
    """
    Checks if the given text contains any blocklisted keywords.
    """
    if not text:
        return True
    
    text_lower = text.lower()
    for word in BLOCKLIST:
        if word in text_lower:
            return False
    return True

def filter_media_items(items: list) -> list:
    """
    Filters a list of media items, removing those that are not safe.
    Expected items to have 'title' and 'description' attributes.
    """
    safe_items = []
    for item in items:
        title = getattr(item, 'title', '')
        description = getattr(item, 'description', '')
        
        if is_safe(title) and is_safe(description):
            safe_items.append(item)
        else:
            logger.warning(f"Filtered unsafe content: {title}")
            
    return safe_items
