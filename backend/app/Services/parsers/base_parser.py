# app/Services/parsers/base_parser.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pdfplumber
from shapely.geometry import Polygon as ShapelyPolygon

class BaseParser(ABC):
    def __init__(self, outputs_dir: Path):
        self.outputs_dir = outputs_dir

    @abstractmethod
    def parse(self, pdf_path: Path, order_code: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_client_code(self) -> str:
        pass
