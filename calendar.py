#!/usr/bin/env python3
from pathlib import Path
from datetime import date, timedelta
import calendar
import sys
from odf.opendocument import OpenDocumentSpreadsheet
from odf import table
from odf.text import P
from odf.style import Style, TextProperties, TableCellProperties, ParagraphProperties, PageLayout, PageLayoutProperties , TableColumnProperties
from odf.table import TableRow, TableCell, TABLENS

MONTHS = ["januari","februari","maart","april","mei","juni","juli","augustus","september","oktober","november","december"]
WEEKDAYS = ["ma","di","wo","do","vr","za","zo"]

def easter_sunday(year):
    a=year%19; b=year//100; c=year%100; d=b//4; e=b%4
    f=(b+8)//25; g=(b-f+1)//3; h=(19*a+b-d-g+15)%30
    i=c//4; k=c%4; l=(32+2*e+2*i-h-k)%7; m=(a+11*h+22*l)//451
    month=(h+l-7*m+114)//31; day=((h+l-7*m+114)%31)+1
    return date(year,month,day)

def dutch_holidays(year):
    e=easter_sunday(year)
    return {
        date(year,1,1):"Nieuwjaarsdag",
        e:"Pasen (1e Paasdag)", e+timedelta(days=1):"Pasen (2e Paasdag)",
        date(year,4,27):"Koningsdag",
        e+timedelta(days=39):"Hemelvaart",
        e+timedelta(days=49):"Pinksteren (1e Pinksterdag)",
        e+timedelta(days=50):"Pinksteren (2e Pinksterdag)",
        date(year,12,25):"Kerstmis (1e Kerstdag)",
        date(year,12,26):"Kerstmis (2e Kerstdag)"
    }

def merged(row, value, span, stylename):
    c=TableCell(stylename=stylename)
    c.setAttrNS(TABLENS, "number-columns-spanned", str(span))
    if value:
        for line in str(value).split("\n"):
            c.addElement(P(text=line))
    row.addElement(c)
    for _ in range(span-1):
        row.addElement(table.CoveredTableCell())
    return c

def cell(row, value="", stylename=None):
    c=TableCell(stylename=stylename)
    if value != "":
        c.addElement(P(text=str(value)))
    row.addElement(c)
    return c

def make_calendar(year, output_file):
    holidays=dutch_holidays(year)
    doc=OpenDocumentSpreadsheet()

    # A3 landscape: 420 x 297 mm, with small printable margins.
    pl=PageLayout(name="A3Landscape")
    pl.addElement(PageLayoutProperties(pagewidth="16.54in", pageheight="11.69in",
                                       printorientation="landscape",
                                       margintop="0.18in", marginbottom="0.18in",
                                       marginleft="0.18in", marginright="0.18in"))
    doc.automaticstyles.addElement(pl)

    def addstyle(name, bg=None, size="11pt", bold=False, align="left", border=True):
        s=Style(name=name,family="table-cell")
        s.addElement(TextProperties(fontsize=size,fontweight="bold" if bold else "normal"))
        s.addElement(ParagraphProperties(textalign=align,verticalalign="middle"))
        s.addElement(TableCellProperties(
            backgroundcolor=bg if bg else "#FFFFFF",
            padding="0.07in",
            border="0.02in solid #777777" if border else "none"))
        doc.automaticstyles.addElement(s)
        return s

    title=addstyle("Title", "#D9EAF7","20pt",True,"center")
    header=addstyle("Header","#D9EAF7","12pt",True,"center")
    day=addstyle("Day","#FFFFFF","13pt",False,"left")
    weekend=addstyle("Weekend","#F2F2F2","13pt",False,"left")
    holiday=addstyle("Holiday","#FFF2CC","11pt",True,"left")
    blank=addstyle("Blank","#FFFFFF","10pt",False,"center")
    photo=addstyle("Photo","#E8E8E8","12pt",True,"center")

    # Holiday overview
    hs=table.Table(name="Feestdagen")
    r=TableRow(); cell(r,f"Nederlandse feestdagen {year}","Title"); hs.addElement(r)
    r=TableRow(); cell(r,"Datum","Header"); cell(r,"Feestdag","Header"); hs.addElement(r)
    for d,n in sorted(holidays.items()):
        r=TableRow(); cell(r,d.strftime("%d-%m-%Y"),"Day"); cell(r,n,"Holiday"); hs.addElement(r)
    doc.spreadsheet.addElement(hs)

    for month in range(1,13):
        s=table.Table(name=MONTHS[month-1].capitalize())

        # 2 columns for portrait photos + 7 calendar columns.
        widths=["2.05in","2.05in"]+["1.07in"]*7
        for i,w in enumerate(widths):
            cs=Style(name=f"C{month}_{i}",family="table-column")
            cs.addElement(TableColumnProperties(columnwidth=w))
            doc.automaticstyles.addElement(cs)
            s.addElement(table.TableColumn(stylename=cs))

        # Month/year merged across all seven calendar columns.
        r=TableRow(); merged(r,"",2,"Blank"); merged(r,f"{MONTHS[month-1].capitalize()} {year}",7,"Title"); s.addElement(r)
        r=TableRow(); merged(r,"",2,"Blank")
        for wd in WEEKDAYS: cell(r,wd,"Header")
        s.addElement(r)

        # Two portrait photo slots on the left.
        for n in (1,2):
            r=TableRow(); merged(r,f"FOTO {n}\n(portrait)",2,"Photo")
            for _ in range(7): cell(r,"","Blank")
            s.addElement(r)
            for _ in range(2):
                r=TableRow(); merged(r,"",2,"Photo")
                for _ in range(7): cell(r,"","Blank")
                s.addElement(r)

        # Calendar occupies the right side, with large rows for handwritten notes.
        weeks=calendar.Calendar(firstweekday=0).monthdayscalendar(year,month)
        while len(weeks)<6: weeks.append([0]*7)
        for week in weeks:
            r=TableRow(); merged(r,"",2,"Blank")
            for wd,n in enumerate(week):
                if not n: cell(r,"","Day"); continue
                d=date(year,month,n)
                if d in holidays:
                    c=TableCell(stylename="Holiday")
                    c.addElement(P(text=str(n)))
                    c.addElement(P(text=holidays[d]))
                    r.addElement(c)
                elif wd>=5: cell(r,n,"Weekend")
                else: cell(r,n,"Day")
            s.addElement(r)

        r=TableRow(); merged(r,"Foto's / notities",2,"Blank"); merged(r,"Geel = Nederlandse feestdag",7,"Holiday"); s.addElement(r)
        doc.spreadsheet.addElement(s)

    doc.save(str(output_file))

if __name__=="__main__":
    year=int(sys.argv[1]) if len(sys.argv)>1 else date.today().year
    output=Path(sys.argv[2]) if len(sys.argv)>2 else Path(f"calendar365_{year}.ods")
    make_calendar(year,output)
    print(f"Gemaakt: {output}")
