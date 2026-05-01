from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / 'project_progress.svg'
PNG = ROOT / 'project_progress.png'
PDF = ROOT / 'project_progress.pdf'

if not SVG.exists():
    print('SVG not found at', SVG)
    sys.exit(2)

try:
    import cairosvg
    cairosvg.svg2png(url=str(SVG), write_to=str(PNG), output_width=1000, output_height=620)
    print('Wrote PNG:', PNG)
except Exception as e:
    print('Failed to render PNG:', e)
    sys.exit(3)

# create a simple PDF embedding the PNG
try:
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    c = canvas.Canvas(str(PDF), pagesize=(1000, 620))
    img = ImageReader(str(PNG))
    c.drawImage(img, 0, 0, width=1000, height=620)
    c.showPage()
    c.save()
    print('Wrote PDF:', PDF)
except Exception as e:
    print('Failed to create PDF:', e)
    sys.exit(4)

print('Done')
