import re
from typing import List, Set, Tuple


class TextProcessor:
    def __init__(self):
        self.months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

    def format_date(self, text: str) -> str:
        """
        Handles various date formats found in medical records:
        - Full dates: DD MMM YYYY (e.g., 26 May 1959)
        - Month-year: MMM YYYY (e.g., Oct 1999)
        - Year only: YYYY (e.g., 1975)
        """
        # Pattern for full dates (day + month + year)
        full_date = r"(\d{1,2})\s*(" + "|".join(self.months) + r")\s*(\d{4})"

        # Pattern for month-year only
        month_year = r"\b(" + "|".join(self.months) + r")\s*(\d{4})\b"

        def format_full_date(match):
            day, month, year = match.groups()
            return f"{day.zfill(2)} {month} {year}"

        def format_month_year(match):
            month, year = match.groups()
            return f"{month} {year}"

        # Apply patterns in order: full dates, then month-year
        text = re.sub(full_date, format_full_date, text)
        text = re.sub(month_year, format_month_year, text)

        return text

    def remove_read_codes(self, text: str) -> str:
        """
        Removes medical read codes from text, handling various OCR artifacts.

        Handles these code formats:
        - Standard format: (A55.)
        - Without parentheses: XE0r9
        - With Yen symbol: ¥3306
        - With dots: 7F19.
        - Multiple closing parentheses: X407Z))
        """
        # Normalize any Yen symbols to Y
        text = text.replace("¥", "Y")

        # Patterns to remove, in order of specificity
        patterns = [
            r"\s*\([A-Z0-9._]+\)+\s*$",  # (XE123), (X407Z))
            r"\s+[A-Z][A-Z0-9._]+\)+\s*$",  # X407Z))
            r"\s+[A-Z][A-Z0-9._]+\s*$",  # M1612
            r"\s+[0-9][A-Z0-9]+\.[0-9]*\s*$",  # 7F19.
            r"\s*[.()]+\s*$",  # Cleanup trailing dots/parentheses
        ]

        # Apply each pattern in sequence
        for pattern in patterns:
            text = re.sub(pattern, "", text)

        return text.strip()

    def clean_description(self, text: str) -> str:
        """
        Cleans OCR artifacts while preserving important text structure.
        """
        # Fix common OCR date formatting issues
        months = "(?:Oct|Dec|Feb|Jan|Mar|Apr|May|Jun|Jul|Aug|Sep|Nov)"
        text = re.sub(rf"(\d+)({months})", r"\1 \2", text)

        # Remove various OCR artifacts while preserving structure
        replacements = [
            (r"[_~]", ""),  # Remove underscores and tildes
            (r"\[(?:Dj|D|X|Xj)\]", ""),  # Remove [D], [Dj], [X], [Xj]
            (r"={1,2}\[(?:Xj|X)\]", ""),  # Remove =[X], =[Xj]
            (r"(?:—|-)+\s*", ""),  # Remove em dashes and hyphens
            (r"=+\s*", ""),  # Remove equals signs
            (r"NOS\s*\(", "NOS "),  # Handle "NOS(" properly
            (r"\s+", " "),  # Normalize spaces
        ]

        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)

        return text.strip()

    def _extract_date_and_description(self, entry: str) -> Tuple[str, str]:
        """Helper function to parse entry into date and description components."""
        parts = entry.split()

        # Full date (DD MMM YYYY)
        if len(parts) >= 3 and parts[1] in self.months:
            return " ".join(parts[:3]), " ".join(parts[3:])

        # Month Year only
        elif len(parts) >= 2 and parts[0] in self.months:
            return " ".join(parts[:2]), " ".join(parts[2:])

        # Year only
        elif parts and parts[0].isdigit() and len(parts[0]) == 4:
            return parts[0], " ".join(parts[1:])

        return "", ""  # Return empty strings instead of None due to typing issue

    def process_text(self, text: str) -> str:
        """
        Main processing function that handles OCR output formatting.
        Ensures proper handling of dates, descriptions, and removal of read codes.
        """
        # Initial cleanup of zero-width spaces
        text = text.replace("\u200b", " ")

        # Split into lines and process each line
        lines = text.split("\n")
        formatted_entries = []

        for line in lines:
            if not line.strip():
                continue

            # Clean up the line and format dates
            line = self.clean_description(line)
            line = self.format_date(line)
            line = self.remove_read_codes(line)

            if line.strip():
                formatted_entries.append(line)

        # Handle duplicates by date and description
        seen_entries: Set[str] = set()
        filtered_entries = []

        for entry in formatted_entries:
            date, description = self._extract_date_and_description(entry)
            if date is None:
                filtered_entries.append(entry)
                continue

            entry_key = f"{date}|{description}"
            if entry_key not in seen_entries:
                seen_entries.add(entry_key)
                filtered_entries.append(entry)

        return "\n".join(filtered_entries)
