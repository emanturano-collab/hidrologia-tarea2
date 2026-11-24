from pathlib import Path
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'pdf'/'T2_202602_G00_presentacion.pdf'
slides=[
('Tarea 2 de Hidrología','Diseño hidrológico — Punto 2\nDWD 00020 · Abtsgmünd–Untergröningen'),
('Pregunta y datos','¿Qué lluvia debe soportar la obra?\nSerie DWD de 10 minutos, 2005–2025\n20 años hidrológicos válidos\nMicrocuenca: 0.123154 km²'),
('Extremos e IDF','GEV-MLE como referencia\nGumbel, GEV y Log-Pearson III\nT = 2, 5, 10, 25, 50 y 100 años\nBootstrap: retornos altos muy inciertos'),
('Comparación externa','KOSTRA-DWD-2020, celda 186/142, EPSG:3035\nLa razón local/KOSTRA cambia con duración y retorno\nNo se interpreta como sesgo puro: mezcla escalas y periodos'),
('Alcantarilla 2.4A','C = 0.33239 · tc Kirpich = 4.226 min\nQp(T=25) = 3.56 m³/s\nDiámetro adoptado = 1.50 m\nRiesgo efectivo anual = 0.9482 %\nRiesgo a 30 años = 24.86 %'),
('Tanque 2.4B','Piscina nivelada: dS/dt = I − O(h)\nOrificio: 0.30 m · Cd = 0.65\nCaso crítico: 60 min, pico final\nVolumen requerido = 1014.75 m³\nVolumen útil = 1056 m³'),
('Limitaciones y decisiones','Outlet sintético derivado del DEM\nWorldCover original y checksum incluidos\nEl método racional no se extrapola a cuencas grandes\nLa cola GEV y la cobertura dominan la incertidumbre'),
('Cierre oral','Explicar: datos → código → figura → decisión\nDefender GEV-MLE, T=25, C y tc\nReconocer incertidumbre y supuestos\nResponder qué cambiaría con clima o urbanización')]
c=canvas.Canvas(str(OUT),pagesize=landscape(A4)); w,h=landscape(A4)
for title,body in slides:
    c.setFillColor(colors.HexColor('#17365D')); c.rect(0,h-75,w,75,fill=1,stroke=0)
    c.setFillColor(colors.white); c.setFont('Helvetica-Bold',24); c.drawString(45,h-50,title)
    c.setFillColor(colors.HexColor('#222222')); c.setFont('Helvetica',18)
    y=h-140
    for line in body.split('\n'):
        c.drawString(60,y,line); y-=34
    c.setFont('Helvetica',9); c.setFillColor(colors.HexColor('#666666')); c.drawRightString(w-35,25,f'Borrador de presentación · {slides.index((title,body))+1}/{len(slides)}')
    c.showPage()
c.save(); print(OUT)
