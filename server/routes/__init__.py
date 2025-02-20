from .config import bp as config_bp
from .users import bp as users_bp
from .emails import bp as emails_bp
from .search import bp as search_bp
from .groups import bp as groups_bp

__all__ = [
    'config_bp',
    'users_bp',
    'emails_bp',
    'search_bp',
    'groups_bp'
]