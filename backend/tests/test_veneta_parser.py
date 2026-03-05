
import pytest
from pathlib import Path
from app.Services.parsers.veneta_cucine_parser import VenetaCucineParser

def test_extract_metadata_standard():
    parser = VenetaCucineParser(Path("/tmp"))
    text = "Ordine 3CAD 306230147 ... Top Caranto Ker in Massa Sp.20 ... 2155 x 20 x 638"
    meta = parser.extract_metadata(text)
    assert meta["order_code"] == "306230147"
    assert meta["width_mm"] == 2155.0
    assert meta["height_mm"] == 638.0
    assert meta["thickness_mm"] == 20.0
    assert "Caranto Ker" in meta["material"]
    assert meta["is_sottotop"] is False

def test_extract_metadata_sottotop():
    parser = VenetaCucineParser(Path("/tmp"))
    text = "SOTTO TOP VEDI DIMA ... Ordine 3CAD 12345 ... 1000 x 20 x 600"
    meta = parser.extract_metadata(text)
    assert meta["is_sottotop"] is True

def test_generate_template_holes():
    parser = VenetaCucineParser(Path("/tmp"))
    main_holes = [
        {"x_mm": 100, "y_mm": 100, "width_mm": 500, "height_mm": 400, "type": "foro_lavello"}
    ]
    template_holes = parser.generate_template_holes(main_holes)
    assert len(template_holes) == 4
    for h in template_holes:
        assert h["diameter_mm"] == 12.0
        assert h["type"] == "bussola"
