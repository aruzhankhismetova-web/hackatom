"""TilTekser — контроль качества казахской и узбекской локализации."""

__version__ = "1.0.0"
__product__ = "TilTekser"

from qazaq_loc_qa.models import Bundle, Finding, Segment

__all__ = ["Bundle", "Finding", "Segment", "__version__"]
