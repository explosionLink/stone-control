# app/Services/pdf_processing_service.py

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from .parsers.veneta_cucine_parser import VenetaCucineParser
from .parsers.base_parser import BaseParser

class PDFProcessingService:
    def __init__(self, imports_dir: str = "imports", outputs_dir: str = "outputs"):
        # Se i path sono relativi, li rendiamo assoluti rispetto alla root del backend
        base_path = Path(__file__).parent.parent.parent
        self.imports_dir = base_path / imports_dir if not Path(imports_dir).is_absolute() else Path(imports_dir)
        self.outputs_dir = base_path / outputs_dir if not Path(outputs_dir).is_absolute() else Path(outputs_dir)
        self.imports_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        # Registry of parsers by client code
        self._parsers: Dict[str, BaseParser] = {
            "VENETA_CUCINE": VenetaCucineParser(self.outputs_dir)
        }

    def process_pdf(self, pdf_path: Path, order_code: str, client_code: str = "VENETA_CUCINE") -> List[Dict[str, Any]]:
        parser = self._parsers.get(client_code)
        if not parser:
            raise ValueError(f"No parser found for client code: {client_code}")

        return parser.parse(pdf_path, order_code)
