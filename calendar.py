#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from datetime import date, timedelta
import calendar
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

def easter_sunday(year):
    a=year%19; b=year//100; c=year%100; d=b//4; e=b%4
    f=(b+8)//25; g=(b-f+1)//3; h=(19*a+b-d-g+15)%30
    i=c//4; k=c%4; l=(32+2*e+2*i-h-k)%7; m=(a+11*h+22*l)//451
    month=(h+l-7*m+114)//31; day=((h+l-7*m+114)%31)+1
    return date(year,month,day)

def dutch_holidays(year):
    e=easter_sunday(year)
    return {
        date(year,1,1):"Nieuwjaar",
        e:"1e Paasdag", e+timedelta(days=1):"2e Paasdag",
        date(year,4,27):"Koningsdag",
        e+timedelta(days=39):"Hemelvaart",
        e+timedelta(days=49):"1e Pinksterdag",
        e+timedelta(days=50):"2e Pinksterdag",
        date(year,12,25):"1e Kerstdag",
        date(year,12,26):"2e Kerstdag"
    }

def get_photo(month, photo_num):
    photo_dir = Path("photo")
    filename_base = f"{month}{photo_num}"
    extensions = [".jpg", ".jpeg", ".png"]
    
    for ext in extensions:
        img_path = photo_dir / f"{filename_base}{ext}"
        if img_path.exists():
            # WIDTH is 9.0 to match the updated col_widths below
            return Image(str(img_path), width=10.0*cm, height=12.0*cm)
    
    return Paragraph(f"Photo {filename_base} not found", ParagraphStyle('Missing', alignment=1))

def make_calendar_pdf(year, output_file):
    holidays = dutch_holidays(year)
    doc = SimpleDocTemplate(
        str(output_file), 
        pagesize=landscape(A3),
        rightMargin=0.2*cm, leftMargin=0.2*cm, 
        topMargin=0.5*cm, bottomMargin=0.2*cm
    )
    
    elements = []
    title_style = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=48, alignment=1, textColor=colors.black, spaceAfter=0)
    header_style = ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=18, alignment=1, textColor=colors.black, spaceAfter=0)
    day_style = ParagraphStyle('Day', fontName='Helvetica-Bold', fontSize=12, alignment=0, spaceAfter=0)
    holiday_style = ParagraphStyle('Holiday', fontSize=10, alignment=0, textColor=colors.red, spaceAfter=0)

    months_nl = ["Januari","Februari","Maart","April","Mei","Juni","Juli","Augustus","September","Oktober","November","December"]
    full_weekdays = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]

    for month in range(1, 13):
        # FIXED: 2 columns for photo (9cm + 0cm) + 7 columns for days (4.1cm * 7) = 9 total
        col_widths = [10.0*cm, 0*cm] + [4.1*cm] * 7
        row_heights = [1.0*cm] * 2 + [4.0*cm] * 6
        
        data = []
        
        # ROW 0: Title (Indices 0-8)
        data.append([""] * 2 + [f"{months_nl[month-1]} {year}"] + [""] * 6)

        # ROW 1: Weekdays (Indices 0-8)
        data.append([""] * 2 + [Paragraph(day, header_style) for day in full_weekdays])

        # ROW 2-7: Calendar Days
        weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
        while len(weeks) < 6:
            weeks.append([0] * 7)

        for week_index, week in enumerate(weeks):
            row_cells = [""] * 2 
            
            if week_index == 0: 
                row_cells[0] = get_photo(month, 1)
            elif week_index == 3: 
                row_cells[0] = get_photo(month, 2)
            
            for day_num in week:
                if day_num == 0:
                    row_cells.append("")
                else:
                    curr = date(year, month, day_num)
                    if curr in holidays:
                        text = f"<b>{day_num}</b><br/>{holidays[curr]}"
                        row_cells.append(Paragraph(text, holiday_style))
                    else:
                        row_cells.append(Paragraph(str(day_num), day_style))
            data.append(row_cells)

        t = Table(data, colWidths=col_widths, rowHeights=row_heights)
        
        style_list = [
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            
            # Photo Column Spans: Merge Col 0 and Col 1
            ('SPAN', (0,2), (1,4)), # Photo 1 area
            ('SPAN', (0,5), (1,7)), # Photo 2 area
            
            # Month Title Span: Merge Col 2 through Col 8
            ('SPAN', (2,0), (8,0)),
            
            ('BACKGROUND', (0,0), (1, -1), colors.whitesmoke),
            ('BACKGROUND', (2,0), (8,0), colors.aliceblue),
            ('BACKGROUND', (2,1), (8,1), colors.aliceblue),
            ('BACKGROUND', (7,2), (8,7), colors.whitesmoke),
            ('ALIGN', (2,0), (8,1), 'CENTER'),
        ]
        t.setStyle(TableStyle(style_list))
        
        elements.append(t)
        elements.append(PageBreak())

    doc.build(elements)

if __name__=="__main__":
    os.makedirs("photo", exist_ok=True)
    year=int(sys.argv[1]) if len(sys.argv)>1 else date.today().year
    output=Path(sys.argv[2]) if len(sys.argv)>2 else Path(f"calendar_{year}.pdf")
    make_calendar_pdf(year,output)
    print(f"PDF Generated: {output}")
