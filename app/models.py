"""
Data models for HealthLabelCheck
Defines the structure for regulation records and related data
"""

from dataclasses import dataclass, asdict
from typing import Optional
import json


@dataclass
class RegulationRecord:
    """
    Represents a single FSSAI labelling regulation requirement
    """
    regulation_no: str
    requirement: str
    applies_to: str
    details: str
    exemption: str
    source_doc: str
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self):
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data):
        """Create RegulationRecord from dictionary"""
        return cls(
            regulation_no=data.get('regulation_no', ''),
            requirement=data.get('requirement', ''),
            applies_to=data.get('applies_to', ''),
            details=data.get('details', ''),
            exemption=data.get('exemption', ''),
            source_doc=data.get('source_doc', '')
        )
    
    def is_mandatory_for_all(self):
        """Check if this regulation applies to all packaged foods"""
        return 'all packaged foods' in self.applies_to.lower()
    
    def has_exemption(self):
        """Check if this regulation has any exemptions"""
        return self.exemption.lower() != 'none'


@dataclass
class LabelCheckResult:
    """
    Represents the result of checking a label against requirements
    """
    regulation_no: str
    requirement: str
    present: bool
    status: str  # 'compliant', 'missing', 'not_applicable'
    notes: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class FontSizeRequirement:
    """
    Represents font size requirements based on panel area
    """
    min_area_cm2: float
    max_area_cm2: float
    min_letter_height_mm: float
    
    def applies_to_area(self, area_cm2: float) -> bool:
        """Check if this requirement applies to given area"""
        return self.min_area_cm2 <= area_cm2 < self.max_area_cm2


# Font size table from FSSAI Regulation 6.1
FONT_SIZE_TABLE = [
    FontSizeRequirement(0, 40, 1.0),
    FontSizeRequirement(40, 170, 1.5),
    FontSizeRequirement(170, 650, 2.0),
    FontSizeRequirement(650, float('inf'), 3.0)
]


def get_min_font_size(panel_area_cm2: float) -> float:
    """
    Get minimum font size for given principal display panel area
    
    Args:
        panel_area_cm2: Area of principal display panel in cm²
    
    Returns:
        Minimum letter height in mm
    """
    for requirement in FONT_SIZE_TABLE:
        if requirement.applies_to_area(panel_area_cm2):
            return requirement.min_letter_height_mm
    
    # Default to largest size if somehow not found
    return 3.0


if __name__ == "__main__":
    # Test the models
    print("=== Testing models.py ===\n")
    
    # Test RegulationRecord
    record = RegulationRecord(
        regulation_no="5.1",
        requirement="Name of Food",
        applies_to="All packaged foods",
        details="The name shall be prescribed or common name",
        exemption="None",
        source_doc="FSSAI 2020"
    )
    
    print("RegulationRecord:")
    print(record)
    print(f"\nMandatory for all: {record.is_mandatory_for_all()}")
    print(f"Has exemption: {record.has_exemption()}")
    
    # Test font size calculation
    print("\n=== Font Size Tests ===")
    test_areas = [30, 100, 200, 700]
    for area in test_areas:
        min_size = get_min_font_size(area)
        print(f"Panel area {area} cm² → Minimum font: {min_size} mm")
    
    # Test LabelCheckResult
    print("\n=== Label Check Result ===")
    result = LabelCheckResult(
        regulation_no="5.1",
        requirement="Name of Food",
        present=True,
        status="compliant",
        notes="Name clearly visible"
    )
    print(result.to_dict())
