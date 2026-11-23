from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Image, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'datos' / 'punto2' / 'Abtsgmuend_Untergroeningen'
OUT = ROOT / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
PDF = OUT / 'informe_tarea2_preview.pdf'

pdfmetrics.registerFont(TTFont('Arial', r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\Windows\Fonts\arialbd.ttf'))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyES', parent=styles['BodyText'], fontName='Arial', fontSize=9.2, leading=12, spaceAfter=4))
styles.add(ParagraphStyle(name='H1ES', parent=styles['Heading1'], fontName='Arial-Bold', fontSize=14, leading=17, spaceBefore=9, spaceAfter=5, textColor=colors.HexColor('#17365D')))
styles.add(ParagraphStyle(name='H2ES', parent=styles['Heading2'], fontName='Arial-Bold', fontSize=11, leading=13, spaceBefore=7, spaceAfter=3, textColor=colors.HexColor('#28527A')))
styles.add(ParagraphStyle(name='TitleES', parent=styles['Title'], fontName='Arial-Bold', fontSize=18, leading=22, alignment=TA_CENTER, textColor=colors.HexColor('#17365D')))
styles.add(ParagraphStyle(name='SmallES', parent=styles['BodyText'], fontName='Arial', fontSize=8, leading=10, textColor=colors.HexColor('#555555')))

def P(text, style='BodyES'): return Paragraph(text, styles[style])
def table(data, widths=None):
    t=Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#D9EAF7')),('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#17365D')),('FONTNAME',(0,0),(-1,0),'Arial-Bold'),('FONTNAME',(0,1),(-1,-1),'Arial'),('FONTSIZE',(0,0),(-1,-1),8),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#9EADBA')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F6F9FB')]),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]))
    return t

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont('Arial',8); canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(2*cm,1.2*cm,'Tarea 2 de Hidrología | Informe de trabajo')
    canvas.drawRightString(A4[0]-2*cm,1.2*cm,f'Página {doc.page}')
    canvas.restoreState()

story=[]
story += [Spacer(1,1.6*cm), Spacer(1,2.5*cm), P('UNIVERSIDAD NACIONAL DE COLOMBIA', 'TitleES'), Spacer(1,1.15*cm), P('Tarea 2 de Hidrología:<br/>Evapotranspiración y diseño hidrológico', 'TitleES'), Spacer(1,1.15*cm), P('<b>Andrés Francisco Idrobo Hidrobo — ID. 1089568711</b><br/>Facultad de Minas — Ingeniería Civil', 'BodyES'), Spacer(1,0.45*cm), P('<b>Enmaly Aleli Manturano Grajeda — ID. 125817023</b><br/>Facultad de Minas — Ingeniería Geológica', 'BodyES'), Spacer(1,0.45*cm), P('<b>Jeyson Cristian Javier Irpanoca — ID. 125496042</b><br/>Facultad de Minas — Ingeniería Geológica', 'BodyES'), Spacer(1,1.1*cm), P('Asignatura: Hidrología<br/>Docente: Carlos David Hoyos<br/><br/>Fecha de entrega: 24 de noviembre de 2026', 'BodyES'), PageBreak()]
story += [P('Resumen', 'H1ES'), P('Este informe presenta el análisis del punto 2 para la estación pluviométrica DWD 00020, Abtsgmünd–Untergröningen (Alemania). Se utilizaron datos de precipitación cada 10 minutos, un modelo digital de elevación SRTM, ESA WorldCover 2021 y KOSTRA-DWD-2020. Se documentan el control de calidad, el análisis de extremos, las curvas IDF, el diseño preliminar de una alcantarilla y un tanque de detención, la incertidumbre Monte Carlo y la bonificación Peaks Over Threshold. El outlet empleado es sintético y se deriva del MDE; esta limitación y el riesgo residual se declaran explícitamente.')]
story += [P('1. Espacio reservado para el punto 1', 'H1ES'), P('<b>Esta sección debe ser completada por los integrantes responsables del punto 1.</b> Debe incorporarse aquí el análisis de la cuenca de la Tarea 1, incluyendo delimitación, precipitación, caudales, temperatura, climatología, tendencias, metodología, resultados y conclusiones.'), P('Como referencia de los datos del grupo, la Tarea 1 trabajó con la cuenca PE_200907 (Racarumi, Chancay–Lambayeque), ubicada aproximadamente en −6.633° y −79.317°, con área de 2363.302 km². Los productos originales se conservan en PUNTO_1/datos/punto1/.'), Spacer(1,1.2*cm), table([['Elemento pendiente','Contenido que debe incorporarse'],['Cuenca y delimitación','Mapa, coordenadas, área y método'],['Datos','Precipitación, caudal, temperatura y periodos'],['Resultados','Climatología, tendencias y conclusiones']], [5*cm,10*cm])]
story += [P('2. Punto 2: análisis hidrológico independiente', 'H1ES'), P('El punto 2 es independiente del punto 1. Se seleccionó la estación DWD 00020 porque dispone de precipitación subdiaria y metadatos geográficos suficientes.'), P('2.1 Datos y control de calidad','H2ES'), P('La serie tiene resolución de 10 minutos entre 2004 y 2025. Se conservaron los datos originales, metadatos y códigos de calidad. Los valores inválidos se transformaron en ausentes y no se imputaron sin decisión metodológica explícita. La microcuenca derivada del MDE tiene área 0.123154 km², longitud de cauce principal 382.69 m y pendiente 0.1254 m/m.'), Image(str(BASE/'control_2_1'/'mapa_revision_visual.png'), width=15*cm, height=10.8*cm)]
story += [P('2.2 Extremos y distribuciones','H2ES'), P('Se construyeron máximos anuales hidrológicos para duraciones de 10 minutos a 24 horas. Se compararon Gumbel, GEV y Log-Pearson III mediante momentos, L-momentos y máxima verosimilitud. Las pruebas KS y Cramér–von Mises, junto con los gráficos de probabilidad, condujeron a seleccionar GEV por máxima verosimilitud como modelo de referencia. El bootstrap muestra incertidumbre creciente para duraciones largas y retornos altos.'), Image(str(BASE/'extremos_2_2'/'graficas_probabilidad_2_2.png'), width=12.8*cm, height=14.6*cm)]
story += [P('2.3 Curvas IDF y comparación externa','H2ES'), P('La IDF local se construyó con GEV-MLE. Las intensidades aumentan al disminuir la duración y al aumentar el periodo de retorno. La comparación con KOSTRA evidencia mayor severidad local en varios escenarios de retorno alto. El máximo de 1 hora de 2021 fue 48.27 mm, con periodo de retorno aproximado de 17.4 años.'), Image(str(BASE/'idf_2_3'/'idf_gev_mle.png'), width=13.5*cm, height=8.2*cm)]
story += [P('2.4 Diseño de obras','H2ES'), P('El outlet adoptado es 48.9181944° N, 9.9123611° E. Coincide con el extremo aguas abajo del cauce derivado del MDE y queda dentro del polígono. OpenStreetMap no confirmó una coincidencia exacta; por ello se declara como outlet sintético.'), P('Alcantarilla: diámetro 1.50 m, pendiente 0.010 m/m, Manning n=0.013, capacidad 7.08 m³/s y caudal de diseño mediano 3.57 m³/s. El factor de seguridad es 1.98. Monte Carlo: falla anual 0.82 % y riesgo acumulado a 30 años 21.9 %.'), P('Tanque: planta 24 × 22 m, profundidad útil 2.0 m, borde libre 0.5 m, volumen útil 1056 m³. El escenario crítico requiere 1019.15 m³ y alcanza 1.93 m de profundidad, por lo que queda un margen de 36.85 m³.'), Image(str(BASE/'control_2_1'/'mapa_revision_visual_detalle.png'), width=13.5*cm, height=9.3*cm)]
story += [P('2.5 Bonificación POT','H2ES'), P('Se aplicó Peaks Over Threshold a acumulados horarios derivados de la serie de 10 minutos. Con umbral P95 de 0.530 mm/h y declustering de 24 horas se obtuvieron 1523 picos y 71.22 eventos/año. La GPD produjo 56.35 mm para 1 hora y T=100 años. La sensibilidad P90–P98 varió entre 52.87 y 61.10 mm; la GEV-MLE entrega 93.36 mm para el mismo escenario. POT se reporta como análisis complementario y no sustituye la IDF principal.'), table([['T (años)','POT-P90 (mm)','POT-P95 (mm)','POT-P98 (mm)','GEV-MLE (mm)'],['2','18.02','18.08','18.29','18.45'],['10','29.04','29.76','30.88','38.81'],['25','37.18','38.67','40.79','55.55'],['100','52.87','56.35','61.10','93.36']], [2.2*cm]*5)]
story += [P('3. Discusión, limitaciones y conclusiones','H1ES'), P('La recomendación depende de la IDF GEV-MLE, del outlet sintético, del coeficiente C=0.334, del tiempo de concentración y de los supuestos de Manning y tránsito. La mayor incertidumbre aparece en la extrapolación de retornos largos y en la representación espacial del outlet. El riesgo efectivo de 21.9 % a 30 años debe guiar una eventual medida adicional de seguridad.'), P('Conclusiones','H2ES'), P('La estación DWD 00020 permite un análisis subdiario reproducible. La GEV-MLE se seleccionó como distribución de referencia y la comparación KOSTRA evidenció mayor severidad local en la cola. El diseño preliminar consta de una alcantarilla de 1.50 m y un tanque de 1056 m³, con riesgo residual explícito. La bonificación POT confirma la sensibilidad del análisis de extremos, pero no reemplaza la IDF principal.'), P('Reproducibilidad y uso de IA','H2ES'), P('Los datos procesados, scripts y resultados se encuentran en PUNTO_2/datos/punto2, PUNTO_2/codigo/punto2 y PUNTO_2/productos/punto2. La auditoría previa obtuvo 10/10 controles OK. La IA se utilizó para organizar código, revisar consistencia, generar mapas estáticos y redactar borradores; las decisiones metodológicas y la responsabilidad académica corresponden al grupo.'), P('Referencias','H2ES'), P('Chow, V. T., Maidment, D. R., & Mays, L. W. (1988). <i>Applied hydrology</i>. McGraw–Hill.<br/>Deutscher Wetterdienst. (2026). <i>Datos históricos de precipitación de la estación 00020</i>.<br/>European Space Agency. (2021). <i>ESA WorldCover 10 m 2021</i>.<br/>OpenStreetMap contributors. (2026). <i>OpenStreetMap</i>.<br/>SRTM. (2013). <i>Shuttle Radar Topography Mission global digital elevation model</i>. NASA.')]

doc=SimpleDocTemplate(str(PDF), pagesize=A4, rightMargin=2.15*cm,leftMargin=2.15*cm,topMargin=1.8*cm,bottomMargin=1.8*cm,title='Informe Tarea 2')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(PDF)
