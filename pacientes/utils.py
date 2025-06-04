from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
import os
from datetime import datetime

def generate_ficha_clinica_pdf(paciente, signos_vitales, balances, evoluciones):
    """
    Genera un PDF con la ficha clínica del paciente
    """
    # Crear un buffer para el PDF
    buffer = BytesIO()
    
    # Crear el PDF
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Logo y cabecera
    p.drawString(width/2 - 50, height - 50, "Área Salud")
    p.drawString(width/2 - 80, height - 70, "Carrera Técnico en Enfermería")
    
    # Dibujar un rectángulo para el logo
    p.rect(width - 150, height - 90, 100, 50)
    p.drawString(width - 130, height - 70, "INACAP")
    
    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(width/2 - 60, height - 110, "FICHA CLÍNICA")
    p.setFont("Helvetica", 10)
    p.drawString(width - 80, height - 110, "(anexo 1)")
    p.setFont("Helvetica", 12)
    
    # Información del paciente
    y_position = height - 140
    
    # Tabla para datos del paciente
    data = [
        ["Sala / cama", paciente.sala_cama],
        ["Nombre del paciente", paciente.nombre],
        ["RUT", paciente.rut, "Fecha", datetime.now().strftime("%d/%m/%Y")],
        ["Días de hospitalización", str(paciente.dias_hospitalizacion), "Edad", str(paciente.edad)]
    ]
    
    # Crear tabla
    table = Table(data, colWidths=[120, 180, 80, 120])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 2), (2, 3), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
    ]))
    
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y_position - 75)
    
    # Sección de dispositivos
    y_position -= 100
    p.setFont("Helvetica-Bold", 10)
    p.drawString(width/2 - 50, y_position, "DISPOSITIVOS")
    p.setFont("Helvetica", 10)
    
    # Tabla para dispositivos
    data = [
        ["Vías venosas /calibre/días", ""],
        ["Catéter Urinario /días", ""]
    ]
    
    # Verificar si el paciente tiene dispositivos
    dispositivos_vvp = paciente.dispositivos.filter(categoria='VVP')
    dispositivos_sonda = paciente.dispositivos.filter(categoria='SONDA', tipo_sonda='FOLEY')
    
    # Completar información de vías venosas si existen
    if dispositivos_vvp.exists():
        vias_info = []
        for disp in dispositivos_vvp:
            vias_info.append(f"{disp.get_tipo_display_completo()} ({disp.dias_instalacion} días)")
        data[0][1] = ", ".join(vias_info)
    
    # Completar información de catéter urinario si existe
    if dispositivos_sonda.exists():
        sonda_info = []
        for disp in dispositivos_sonda:
            sonda_info.append(f"Sonda Foley ({disp.dias_instalacion} días)")
        data[1][1] = ", ".join(sonda_info)
    
    table = Table(data, colWidths=[160, 340])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
    ]))
    
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y_position - 45)
    
    # Sección de signos vitales
    y_position -= 70
    p.setFont("Helvetica-Bold", 10)
    p.drawString(width/2 - 60, y_position, "CURVA DE SIGNOS VITALES")
    p.setFont("Helvetica", 10)
    
    # Obtener horas únicas para las columnas
    horas = ["09:00", "13:00", "17:00", "21:00", "01:00", "07:00"]
    
    # Cabecera de la tabla de signos vitales
    header_row = [""] + horas
    
    data = [header_row]
    
    # Filas para cada tipo de signo vital
    signos_rows = [
        "Presión Art.",
        "F. Cardíaca",
        "Saturación",
        "FiO2",
        "F. Respiratoria",
        "Temperatura",
        "HGT",
        "EVA"
    ]
    
    # Crear un diccionario para fácil acceso a los signos vitales
    signos_por_hora = {}
    for signo in signos_vitales:
        if signo.hora not in signos_por_hora:
            signos_por_hora[signo.hora] = signo
    
    # Crear filas para cada tipo de signo vital
    for signo_tipo in signos_rows:
        row = [signo_tipo]
        
        for hora in horas:
            valor = ""
            if hora in signos_por_hora:
                signo = signos_por_hora[hora]
                if signo_tipo == "Presión Art.":
                    valor = signo.presion_arterial
                elif signo_tipo == "F. Cardíaca":
                    valor = str(signo.frecuencia_cardiaca)
                elif signo_tipo == "Saturación":
                    valor = str(signo.saturacion)
                elif signo_tipo == "FiO2":
                    valor = str(signo.fio2) if signo.fio2 else ""
                elif signo_tipo == "F. Respiratoria":
                    valor = str(signo.frecuencia_respiratoria)
                elif signo_tipo == "Temperatura":
                    valor = str(signo.temperatura)
                elif signo_tipo == "HGT":
                    valor = str(signo.hgt) if signo.hgt else ""
                elif signo_tipo == "EVA":
                    valor = str(signo.eva) if signo.eva else ""
            
            row.append(valor)
        
        data.append(row)
    
    table = Table(data, colWidths=[100] + [65] * len(horas))
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y_position - 180)
    
    # Sección de indicaciones
    y_position -= 200
    p.setFont("Helvetica-Bold", 10)
    p.drawString(width/2 - 40, y_position, "INDICACIONES")
    p.setFont("Helvetica", 10)
    
    # Espacio para indicaciones (rectangular box)
    p.rect(50, y_position - 50, width - 100, 40)
    
    # Obtener la última evolución e indicaciones
    if evoluciones:
        ultima_evolucion = evoluciones.first()
        if ultima_evolucion and ultima_evolucion.indicaciones:
            text = ultima_evolucion.indicaciones
            if len(text) > 150:  # limitar longitud
                text = text[:147] + "..."
            p.drawString(55, y_position - 20, text)
    
    # Sección de balance hídrico
    y_position -= 70
    p.setFont("Helvetica-Bold", 10)
    p.drawString(width/2 - 30, y_position, "BALANCE")
    p.setFont("Helvetica", 10)
    
    # Horarios para el balance hídrico
    horas_balance = ["09:00", "13:00", "17:00", "21:00", "01:00", "06:00"]
    
    # Ingresos
    data = [
        ["Ingresos"] + horas_balance
    ]
    
    # Crear un diccionario para fácil acceso a los balances
    balances_por_hora = {}
    for balance in balances:
        balances_por_hora[balance.hora] = balance
        
    # Filas de ingresos
    ingresos_rows = ["Agua", "Soluciones", "Alimentos"]
    for ingreso_tipo in ingresos_rows:
        row = [ingreso_tipo]
        
        for hora in horas_balance:
            valor = ""
            if hora in balances_por_hora:
                balance = balances_por_hora[hora]
                if ingreso_tipo == "Agua":
                    valor = str(balance.agua)
                elif ingreso_tipo == "Soluciones":
                    valor = str(balance.soluciones)
                elif ingreso_tipo == "Alimentos":
                    valor = str(balance.alimentos)
            
            row.append(valor)
        
        data.append(row)
    
    table = Table(data, colWidths=[100] + [65] * len(horas_balance))
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y_position - 80)
    
    # Egresos
    y_position -= 90
    data = [
        ["Egresos"] + horas_balance
    ]
    
    # Filas de egresos
    egresos_rows = ["Orina", "Deposiciones", "Vómito"]
    for egreso_tipo in egresos_rows:
        row = [egreso_tipo]
        
        for hora in horas_balance:
            valor = ""
            if hora in balances_por_hora:
                balance = balances_por_hora[hora]
                if egreso_tipo == "Orina":
                    valor = str(balance.orina)
                elif egreso_tipo == "Deposiciones":
                    valor = str(balance.deposiciones)
                elif egreso_tipo == "Vómito":
                    valor = str(balance.vomito)
            
            row.append(valor)
        
        data.append(row)
    
    table = Table(data, colWidths=[100] + [65] * len(horas_balance))
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y_position - 80)
    
    # Sección de evoluciones
    y_position -= 100
    p.setFont("Helvetica-Bold", 10)
    p.drawString(width/2 - 40, y_position, "EVOLUCIONES")
    p.setFont("Helvetica", 10)
    
    # Tabla para evoluciones
    data = [["Hora", "Registro", "Responsable"]]
    
    # Agregar evoluciones (máximo 2 para que quepan en la página)
    for i, evolucion in enumerate(evoluciones[:2]):
        data.append([
            evolucion.hora.strftime("%H:%M") if evolucion.hora else "",
            evolucion.registro[:100] + "..." if len(evolucion.registro) > 100 else evolucion.registro,
            evolucion.responsable.get_full_name()
        ])
    
    # Asegurarse de que haya al menos una fila vacía si no hay evoluciones
    if len(data) == 1:
        data.append(["", "", ""])
        data.append(["", "", ""])
    elif len(data) == 2:
        data.append(["", "", ""])
    
    table = Table(data, colWidths=[60, 340, 100])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y_position - 80)
    
    # Pie de página
    p.setFont("Helvetica", 8)
    p.drawString(width/2 - 100, 40, "Enfermería del Niño y Adolescente (INNA01)")
    
    # Guardar el PDF
    p.showPage()
    p.save()
    
    # Mover el cursor al inicio del buffer
    buffer.seek(0)
    
    return buffer 