"""
Utility functions for URL shortening.
"""
import string
import random


# Base62 characters: 0-9, a-z, A-Z
BASE62_CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE62_LENGTH = len(BASE62_CHARS)


def generate_short_key(length=6):
    """
    Generate a random short key using base62 characters.
    
    Args:
        length: Length of the key to generate (default: 6)
    
    Returns:
        A random string of base62 characters
    """
    return ''.join(random.choice(BASE62_CHARS) for _ in range(length))


def base62_encode(num):
    """
    Encode a number to base62.
    
    Args:
        num: Integer to encode
    
    Returns:
        Base62 encoded string
    """
    if num == 0:
        return BASE62_CHARS[0]
    
    result = []
    while num > 0:
        result.append(BASE62_CHARS[num % BASE62_LENGTH])
        num //= BASE62_LENGTH
    
    return ''.join(reversed(result))


def base62_decode(encoded):
    """
    Decode a base62 string to a number.
    
    Args:
        encoded: Base62 encoded string
    
    Returns:
        Decoded integer
    """
    num = 0
    for char in encoded:
        num = num * BASE62_LENGTH + BASE62_CHARS.index(char)
    return num

