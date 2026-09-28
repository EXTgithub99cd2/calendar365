#!/usr/bin/env python3
"""
Maak een Nederlandse maandkalender als .ods-bestand.

Gebruik:
    python maak_nederlandse_maandkalender.py 2026
    python maak_nederlandse_maandkalender.py 2027 mijn_kalender.ods

De kalender gebruikt maandag als eerste dag van de week en vermeldt
Nederlandse feestdagen. De kalender bevat 12 maandbladen plus een blad
"Feestdagen".
"""

from pathlib import Path
from datetime import date, timedelta
import calendar
import sys

from odf.opendocument import OpenDocumentSpreadsheet
from odf import table, text, style
from odf.text import P
from odf.table import TableRow, TableCell
from odf.style import Style, TextProperties, TableCellProperties, ParagraphProperties


MONTHS = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december"
]
WEEKDAYS = ["ma", "di", "wo", "do", "vr", "za", "zo"]


def easter_sunday(year):
    """Meeus/Jones/Butcher-algoritme voor Paaszondag."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451
    month = (h + l - 7*m + 114) // 31
    day = ((h + l - 7*m + 114) % 31) + 1
    return date(year, month, day)


def dutch_holidays(year):
    """Geeft de belangrijkste Nederlandse feestdagen voor het kalenderjaar."""
    easter = easter_sunday(year)
    return {
        date(year, 1, 1): "Nieuwjaarsdag",
        easter: "Pasen (1e Paasdag)",
        easter + timedelta(days=1): "Pasen (2e Paasdag)",
        date(year, 4, 27): "Koningsdag",
        easter + timedelta(days=39): "Hemelvaart",
        easter + timedelta(days=49): "Pinksteren (1e Pinksterdag)",
        easter + timedelta(days=50): "Pinksteren (2e Pinksterdag)",
        date(year, 12, 25): "Kerstmis (1e Kerstdag)",
        date(year, 12, 26): "Kerstmis (2e Kerstdag)",
    }


def add_cell(row, value="", cell_style=None):
    cell = TableCell(stylename=cell_style) if cell_style else TableCell()
    cell.addElement(P(text=str(value)))
    row.addElement(cell)
    return cell


def make_calendar(year, output_file):
    holidays = dutch_holidays(year)

    doc = OpenDocumentSpreadsheet()

    # ---- Stijlen ----
    title_style = Style(name="CalendarTitle", family="table-cell")
    title_style.addElement(TextProperties(fontsize="16pt", fontweight="bold"))
    title_style.addElement(ParagraphProperties(textalign="center"))
    doc.automaticstyles.addElement(title_style)

    header_style = Style(name="WeekHeader", family="table-cell")
    header_style.addElement(TextProperties(fontweight="bold"))
    header_style.addElement(ParagraphProperties(textalign="center"))
    header_style.addElement(TableCellProperties(backgroundcolor="#D9EAF7"))
    doc.automaticstyles.addElement(header_style)

    day_style = Style(name="DayCell", family="table-cell")
    day_style.addElement(ParagraphProperties(verticalalign="top"))
    day_style.addElement(TableCellProperties(padding="0.08in"))
    doc.automaticstyles.addElement(day_style)

    holiday_style = Style(name="HolidayCell", family="table-cell")
    holiday_style.addElement(TextProperties(fontweight="bold"))
    holiday_style.addElement(ParagraphProperties(verticalalign="top"))
    holiday_style.addElement(TableCellProperties(backgroundcolor="#FFF2CC", padding="0.08in"))
    doc.automaticstyles.addElement(holiday_style)

    weekend_style = Style(name="WeekendCell", family="table-cell")
    weekend_style.addElement(ParagraphProperties(verticalalign="top"))
    weekend_style.addElement(TableCellProperties(backgroundcolor="#F2F2F2", padding="0.08in"))
    doc.automaticstyles.addElement(weekend_style)

    # ---- Feestdagenblad ----
    ht = table.Table(name="Feestdagen")
    hr = TableRow()
    add_cell(hr, f"Nederlandse feestdagen {year}", title_style)
    ht.addElement(hr)

    hr = TableRow()
    add_cell(hr, "Datum", header_style)
    add_cell(hr, "Feestdag", header_style)
    ht.addElement(hr)

    for d, name in sorted(holidays.items()):
        hr = TableRow()
        add_cell(hr, d.strftime("%d-%m-%Y"), day_style)
        add_cell(hr, name, holiday_style)
        ht.addElement(hr)

    # Extra uitleg
    hr = TableRow()
    add_cell(hr, "")
    add_cell(hr, "Weekindeling: maandag t/m zondag. Jaar gegenereerd door het script.", day_style)
    ht.addElement(hr)

    doc.spreadsheet.addElement(ht)

    # ---- 12 maandbladen ----
    for month in range(1, 13):
        sheet = table.Table(name=MONTHS[month - 1].capitalize())

        # Titel
        row = TableRow()
        add_cell(row, f"{MONTHS[month - 1].capitalize()} {year}", title_style)
        for _ in range(6):
            add_cell(row, "", title_style)
        sheet.addElement(row)

        # Weekdagen
        row = TableRow()
        for wd in WEEKDAYS:
            add_cell(row, wd, header_style)
        sheet.addElement(row)

        # Python's calendar: Monday=0, Sunday=6
        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdayscalendar(year, month)

        # Altijd minimaal 6 kalenderregels voor een vaste lay-out
        while len(weeks) < 6:
            weeks.append([0] * 7)

        for week in weeks:
            row = TableRow()
            for weekday, day in enumerate(week):
                if day == 0:
                    add_cell(row, "", day_style)
                    continue

                d = date(year, month, day)
                if d in holidays:
                    cell = TableCell(stylename=holiday_style)
                    cell.addElement(P(text=str(day)))
                    cell.addElement(P(text=holidays[d]))
                    row.addElement(cell)
                elif weekday >= 5:
                    cell = TableCell(stylename=weekend_style)
                    cell.addElement(P(text=str(day)))
                    row.addElement(cell)
                else:
                    cell = TableCell(stylename=day_style)
                    cell.addElement(P(text=str(day)))
                    row.addElement(cell)
            sheet.addElement(row)

        # Korte legenda
        row = TableRow()
        add_cell(row, "")
        add_cell(row, "Geel = Nederlandse feestdag", holiday_style)
        for _ in range(5):
            add_cell(row, "")
        sheet.addElement(row)

        doc.spreadsheet.addElement(sheet)

    doc.save(str(output_file))


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else date.today().year
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(f"Nederlandse_maandkalender_{year}.ods")
    make_calendar(year, output)
    print(f"Gemaakt: {output}")
