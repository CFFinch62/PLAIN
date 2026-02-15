"""
Warning and error reporting system for the converter.

Provides structured warnings for conversion issues, unsupported features,
and lossy conversions.
"""

from enum import Enum
from dataclasses import dataclass, field


class WarningCategory(Enum):
    """Categories of conversion warnings."""
    UNSUPPORTED_FEATURE = "unsupported_feature"
    LOSSY_CONVERSION = "lossy_conversion"
    TYPE_INFERENCE = "type_inference"
    NAMING_CONFLICT = "naming_conflict"
    SHADOWED_VARIABLE = "shadowed_variable"
    MANUAL_FIX_NEEDED = "manual_fix_needed"
    COMMENT_LOST = "comment_lost"
    IMPORT_NEEDED = "import_needed"
    STYLE = "style"


@dataclass
class ConversionWarning:
    """A single conversion warning."""
    category: WarningCategory
    message: str
    line: int | None = None
    source_code: str | None = None
    suggestion: str | None = None

    def __str__(self) -> str:
        parts = []
        if self.line is not None:
            parts.append(f"Line {self.line}")
        parts.append(f"[{self.category.value}]")
        parts.append(self.message)
        if self.suggestion:
            parts.append(f"(Suggestion: {self.suggestion})")
        return " ".join(parts)


@dataclass
class ConversionResult:
    """Result of a code conversion operation."""
    code: str
    warnings: list[ConversionWarning] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Whether the conversion completed without errors."""
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        """Whether the conversion produced any warnings."""
        return len(self.warnings) > 0

    def add_warning(self, category: WarningCategory, message: str,
                    line: int | None = None, source_code: str | None = None,
                    suggestion: str | None = None) -> None:
        """Add a warning to the result."""
        self.warnings.append(ConversionWarning(
            category=category,
            message=message,
            line=line,
            source_code=source_code,
            suggestion=suggestion,
        ))

    def add_error(self, message: str) -> None:
        """Add an error to the result."""
        self.errors.append(message)

    def increment_stat(self, key: str, amount: int = 1) -> None:
        """Increment a conversion statistic."""
        self.stats[key] = self.stats.get(key, 0) + amount


class UnsupportedFeatureError(Exception):
    """Raised in strict mode when an unsupported feature is encountered."""

    def __init__(self, feature: str, line: int | None = None,
                 suggestion: str | None = None):
        self.feature = feature
        self.line = line
        self.suggestion = suggestion
        msg = f"Unsupported feature: {feature}"
        if line is not None:
            msg = f"Line {line}: {msg}"
        if suggestion:
            msg += f" (Suggestion: {suggestion})"
        super().__init__(msg)

