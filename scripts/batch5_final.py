#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch 5 FINAL: Push past 1000 with remaining patterns - ciberbullying, ESCI, more derivados."""

import csv, json, os
from datetime import datetime

with open('existing_signals.json', 'r', encoding='utf-8') as f:
    existing = set(s.lower().strip() for s in json.load(f))

OUTPUT_FILE = 'dataset_expansion_results.csv'
with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        existing.add(row['señal_base'].lower().strip())

print(f'Loaded {len(existing)} total signals')

with open('batch4_counters.json', 'r') as f:
    data = json.load(f)
counters = {int(k): v for k, v in data['counters'].items()}

headers = ['id','fase','señal_base','variantes','intención','fuente','tipo','peso','url_fuente','fecha_hallazgo','confiabilidad']
added = 0
skipped = 0
now = datetime.now().isoformat()

def add(fase, signal, variantes, intencion, fuente, tipo, peso, url='', conf='media'):
    global added, skipped
    if signal.lower().strip() in existing:
        skipped += 1
        return
    existing.add(signal.lower().strip())
    pid = f'f{fase}_{counters[fase]:03d}'
    counters[fase] += 1
    row = {'id': pid, 'fase': fase, 'señal_base': signal, 'variantes': variantes,
        'intención': intencion, 'fuente': fuente, 'tipo': tipo, 'peso': peso,
        'url_fuente': url, 'fecha_hallazgo': now, 'confiabilidad': conf}
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writerow(row)
    added += 1

# ============================================================
# CIBERBULLYING -> RECLUTAMIENTO (transición)
# ============================================================
SSC = 'https://www.ssc.cdmx.gob.mx/comunicacion/nota/1173-la-policia-cibernetica-de-la-ssc-alerta-sobre-grupos-en-redes-sociales-que-incitan-el-ciberbullying'

add(2, 'te vamos a funear en redes', 'te funeamos, te tundimos en redes, te quemamos online', 'ciberbullying', 'SSC/CDMX', 'coercion', 0.65, SSC, 'alta')
add(3, 'te amenazaron con publicar información personal', 'publican tu info, difunden tus datos', 'amenaza_doxxing', 'INEGI/REDIM', 'coercion', 0.8, 'https://blog.derechosinfancia.org.mx/2025/08/14/ciberacoso-de-adolescentes-en-mexico-2017-2024/', 'alta')
add(3, 'hicimos un grupo para exhibirte', 'grupo para quemarte, página para humillarte', 'ciberbullying', 'SSC/CDMX', 'coercion', 0.8, SSC, 'alta')

# ============================================================
# EXPLOTACIÓN SEXUAL COMERCIAL (ESCI)
# ============================================================
add(2, 'te puedo conseguir trabajo de modelo webcam', 'modelo por cámara, webcam model, videochat', 'captación_ESCI', 'Derivado', 'económica', 0.8, '', 'media')
add(2, 'solo tienes que tomarte unas fotos bonitas', 'sesión de fotos, fotos artísticas, book fotográfico', 'captación_ESCI', 'Derivado', 'emocional', 0.75, '', 'media')
add(2, 'ganas más en una noche que en todo el mes', 'ganas muchísimo por noche, es dinero fácil por noche', 'captación_ESCI', 'Derivado', 'económica', 0.75, '', 'media')
add(3, 'ya pagué tu deuda ahora tú me pagas a mí', 'me debes, pagué por ti, ahora trabajas para mí', 'servidumbre_deuda', 'UNODC', 'coercion', 0.9, '', 'alta')

# ============================================================
# DERIVADOS MASIVOS: CAPTACIÓN (más variantes)
# ============================================================
add(1, 'necesitamos gente para las fiestas', 'personal para eventos, seguridad en fiestas, staff', 'oferta_falsa', 'Derivado', 'económica', 0.55, '', 'baja')
add(1, 'empleo de vigilante nocturno', 'turno nocturno, velador, guardia de noche', 'oferta_falsa', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'trabajo de fletero buen pago', 'fletero, mudanzas, cargador de fletes', 'oferta_falsa', 'Derivado', 'económica', 0.55, '', 'baja')
add(1, 'empleo temporal bien pagado', 'temporal, por proyecto, solo unos meses', 'oferta_falsa', 'Derivado', 'económica', 0.55, '', 'baja')
add(1, 'necesitamos técnicos urgente', 'técnico electrónico, técnico en sistemas', 'oferta_falsa', 'Derivado', 'económica', 0.5, '', 'baja')
add(1, 'trabajo para mayores de 15', 'desde los 15, +15, mayores de 15 años', 'reclutamiento_menores', 'Derivado', 'económica', 0.7, '', 'media')
add(1, 'empleo compatible con escuela', 'no afecta tus estudios, trabajas después de clase', 'oferta_falsa', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'ganas 50 mil al mes fácil', '50mil mensuales, cincuenta al mes, ganas 50k', 'incentivo_económico', 'Derivado', 'económica', 0.65, '', 'baja')
add(1, 'el dinero no tiene nombre', 'el dinero no apesta, money is money', 'normalización', 'Derivado', 'sociocultural', 0.5, '', 'baja')
add(1, 'hay que chingarle mientras se pueda', 'aprovechar mientras dure, ganar ahora', 'aspiracional', 'Derivado', 'sociocultural', 0.45, '', 'baja')
add(1, 'tú solo di que sí lo demás yo lo arreglo', 'yo me encargo de todo, tú solo acepta', 'presión', 'Derivado', 'funcional', 0.65, '', 'baja')
add(1, 'conocidos míos empezaron así y ahora están bien', 'compas que empezaron de abajo, casos de éxito', 'aspiracional', 'Derivado', 'sociocultural', 0.55, '', 'baja')
add(1, 'el gobierno te abandonó nosotros no', 'el sistema te falló, nosotros te apoyamos', 'desconfianza_institucional', 'Derivado', 'sociocultural', 0.6, '', 'baja')
add(1, 'pagan en efectivo nada de recibos ni impuestos', 'sin factura, libre de impuestos, cash limpio', 'incentivo', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'incluye comidas y transporte', 'comida gratis, transporte incluido, todo pagado', 'incentivo', 'Derivado', 'económica', 0.55, '', 'baja')
add(1, 'te damos moto para trabajar', 'moto de trabajo, te prestamos vehículo', 'incentivo_material', 'Derivado', 'económica', 0.55, '', 'baja')
add(1, 'aquí sí se valora a la gente', 'aquí te valoran, aquí eres alguien de verdad', 'aspiracional', 'Derivado', 'sociocultural', 0.5, '', 'baja')

# ============================================================
# DERIVADOS MASIVOS: ENGANCHE (más variantes)
# ============================================================
add(2, 'solo lleva este sobre no lo abras', 'lleva este sobre, no preguntes qué es, no lo abras', 'complicidad_gradual', 'Derivado', 'funcional', 0.7, '', 'media')
add(2, 'haz como si fueras mi novia para la foto', 'hazte pasar por mi novia, actúa como pareja', 'enganche_trata', 'Derivado', 'emocional', 0.7, '', 'media')
add(2, 'ya le dije al jefe que vienes', 'ya confirme con el patrón, ya te esperan', 'presión', 'Derivado', 'funcional', 0.7, '', 'baja')
add(2, 'te mando la ubicación por WhatsApp', 'te paso pin de ubicación, ahí es', 'enganche', 'Derivado', 'funcional', 0.65, '', 'baja')
add(2, 'no traigas nada solo ven como estás', 'ven así, no necesitas nada, ven ligero', 'enganche', 'Derivado', 'funcional', 0.6, '', 'baja')
add(2, 'te mando para el pasaje', 'te deposito para el camión, dinero para el transporte', 'enganche', 'Derivado', 'funcional', 0.7, '', 'media')
add(2, 'pruébate esta ropa táctica', 'ponte el uniforme, esta es tu ropa de trabajo', 'enganche', 'Derivado', 'funcional', 0.7, '', 'media')
add(2, 'esto es solo el inicio después viene lo bueno', 'al principio es así, ya después mejora', 'minimización', 'Derivado', 'emocional', 0.6, '', 'baja')
add(2, 'cierra tus redes sociales por seguridad', 'borra tus redes, cierra tu Face, desactiva tu Insta', 'aislamiento_digital', 'Derivado', 'funcional', 0.8, '', 'media')
add(2, 'no publiques nada de lo que haces', 'no postees, nada de redes, cero publicaciones', 'aislamiento_digital', 'Derivado', 'funcional', 0.75, '', 'media')
add(2, 'deja tu celular aquí y usa este', 'toma este cel, usa este teléfono, deja el tuyo', 'control_dispositivo', 'Derivado', 'funcional', 0.85, '', 'media')

# ============================================================
# DERIVADOS MASIVOS: COERCIÓN (más variantes)
# ============================================================
add(3, 'le mandé capturas a tu novia', 'tu novia ya vio, le dije a tu pareja', 'amenaza_social', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'ya te tenemos identificado con nombre y dirección', 'sabemos tu nombre real, tu dirección, todo de ti', 'amenaza_doxxing', 'Derivado', 'coercion', 0.9, '', 'media')
add(3, 'mañana paso por ti no es pregunta', 'voy por ti quieras o no, mañana te recojo', 'imposición', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'mira lo que les pasó a los que dijeron que no', 'mira el ejemplo, así les fue a los otros', 'amenaza_implícita', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'tú no quisiste por las buenas', 'tuviste oportunidad, ahora es a fuerzas', 'imposición', 'Derivado', 'coercion', 0.9, '', 'media')
add(3, 'piensa en tu hermanita', 'tu hermana, tu hermano, tus primos, tu abuela', 'amenaza_familiar', 'Derivado', 'coercion', 0.95, '', 'media')
add(3, 'yo te metí y yo te saco pero con condiciones', 'te ayudo pero pagas, te saco si cooperas', 'retención', 'Derivado', 'coercion', 0.8, '', 'media')
add(3, 'quieres terminar en una fosa', 'fosa, barranca, encajuelado, te desaparecen', 'amenaza_muerte', 'Derivado', 'coercion', 0.95, '', 'media')
add(3, 'a tu familia le dejamos un mensaje', 'narcomanta para tu familia, les dejamos recado', 'amenaza_familiar', 'Derivado', 'coercion', 0.95, '', 'media')
add(3, 'si corres te alcanzamos', 'no puedes correr, te atrapamos, no te escapas', 'amenaza_persecución', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'ya pusimos precio a tu cabeza', 'hay recompensa por ti, te buscamos', 'amenaza_muerte', 'Derivado', 'coercion', 1.0, '', 'media')
add(3, 'estas cámaras graban todo lo que haces', 'te estamos grabando, cámaras en el cuarto', 'vigilancia', 'Derivado', 'coercion', 0.8, '', 'media')

# ============================================================
# DERIVADOS MASIVOS: EXPLOTACIÓN (más variantes)
# ============================================================
add(4, 'cambia la placa del carro', 'ponle placas nuevas, roba placas, cambia matrícula', 'orden_operativa', 'Derivado', 'operativo', 0.7, '', 'baja')
add(4, 'ponle gasolina a la troca del jefe', 'carga gas, llena el tanque, ponle gasolina', 'orden_menor', 'Derivado', 'operativo', 0.5, '', 'baja')
add(4, 'lleva el recado a la otra plaza', 'mensaje para la otra plaza, recado al comandante', 'orden_comunicación', 'Derivado', 'operativo', 0.65, '', 'baja')
add(4, 'cocina 5 kilos para el jueves', 'producción de X kilos, prepara la carga', 'orden_producción', 'Derivado', 'operativo', 0.85, '', 'media')
add(4, 'cruza con el paquete por este punto', 'cruce del paquete, pásalo por aquí, punto de cruce', 'orden_transporte', 'Derivado', 'operativo', 0.8, '', 'media')
add(4, 'ya salieron los guachos avisa arriba', 'guachos salieron, militares en movimiento, avisa al jefe', 'código_alerta', 'Derivado', 'operativo', 0.75, '', 'baja')
add(4, 'pon el retén aquí', 'retén narco, bloqueo, ponle barricada', 'orden_operativa', 'Derivado', 'operativo', 0.75, '', 'baja')
add(4, 'cobra la extorsión del jueves', 'cuota del jueves, renta del local, pasa a cobrar', 'orden_extorsión', 'Derivado', 'operativo', 0.75, '', 'media')
add(4, 'dale seguimiento al target', 'sigue al objetivo, vigila sus movimientos, documenta todo', 'orden_inteligencia', 'Derivado', 'operativo', 0.8, '', 'media')
add(4, 'consigue teléfonos nuevos para el equipo', 'compra cels, teléfonos desechables, prepago', 'orden_logística', 'Derivado', 'operativo', 0.6, '', 'baja')
add(4, 'sube la foto de la manta al grupo', 'difunde la narcomanta, postea la amenaza', 'propaganda', 'Derivado', 'operativo', 0.7, '', 'media')
add(4, 'recluta a 5 más de tu colonia', 'trae más gente, busca 5 de tu barrio, consigue reclutas', 'reclutamiento_cascada', 'Derivado', 'operativo', 0.8, '', 'media')
add(4, 'esconde las armas en el compartimento', 'escondite, caleta, compartimento secreto', 'orden_operativa', 'Derivado', 'operativo', 0.75, '', 'baja')

# ============================================================
# EMOJIS SECUENCIAS FINALES
# ============================================================
add(3, '\U0001f4f8\u2b06\ufe0f\U0001f4f1 screenshot subir', 'screenshot upload, subir captura, difundir screenshot', 'amenaza_difusión', 'Derivado', 'simbólica', 0.7, '', 'baja')
add(1, '\U0001f911 cara con dinero', '\U0001f911 money face, ojos de dinero, dólar cara', 'incentivo_visual', 'Derivado', 'simbólica', 0.45, '', 'baja')
add(2, '\U0001f91d apretón de manos', '\U0001f91d deal, trato, acuerdo emoji', 'enganche', 'Derivado', 'simbólica', 0.4, '', 'baja')
add(4, '\u2694\ufe0f espadas cruzadas', '\u2694\ufe0f batalla, pelea, combate emoji', 'operativo', 'Derivado', 'simbólica', 0.5, '', 'baja')
add(4, '\U0001f697\U0001f4a8 carro escapando', '\U0001f697 carro rápido, huida, escape emoji', 'código_operativo', 'Derivado', 'simbólica', 0.5, '', 'baja')

# ============================================================
# HASHTAGS FINALES
# ============================================================
add(1, '#empleourgente', '#empleoya, #vacantesurgentes, #senegente', 'reclutamiento', 'Derivado', 'hashtag', 0.5, '', 'baja')
add(1, '#ganadineroya', '#lanarapida, #dinerohoy', 'reclutamiento', 'Derivado', 'hashtag', 0.5, '', 'baja')
add(1, '#trabajosinrequisitos', '#sinexperiencia, #sinestudios, #trabajoya', 'reclutamiento', 'Derivado', 'hashtag', 0.45, '', 'baja')
add(1, '#vidadereyes', '#vidaloca, #vidarapida, #livefastdiefast', 'narcocultura', 'Derivado', 'hashtag', 0.4, '', 'baja')

# ============================================================
# LEET FINALES
# ============================================================
add(1, 'pr0m0t0ra', 'promot0ra, pr0motora (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.45, '', 'baja')
add(1, 'mod3l0', 'model0, mod3lo (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.45, '', 'baja')
add(1, 'r3p4rt1d0r', 'repartid0r, r3partidor (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.45, '', 'baja')
add(3, 'f0t0s', 'fot0s, f0tos (leet fotos)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(3, 'am3n4z4', 'amenaz4, am3naza (leet)', 'evasión_filtro', 'Derivado', 'coercion', 0.5, '', 'baja')

# ============================================================
# PATRONES FINALES VARIOS
# ============================================================
add(1, 'tienes cara de gente buena quieres jale', 'te ves buena onda, pareces de confianza, eres de fiar', 'reclutamiento_directo', 'Derivado', 'funcional', 0.6, '', 'baja')
add(1, 'nomás dame un día de prueba', 'prueba un día, ven a ver qué onda, sin compromiso', 'minimización', 'Derivado', 'funcional', 0.6, '', 'baja')
add(2, 'ya firmaste ya estás adentro', 'no hay vuelta atrás, ya aceptaste, ya estás comprometido', 'retención', 'Derivado', 'funcional', 0.75, '', 'media')
add(2, 'te enseño el negocio y luego tú decides', 'conoce primero y después dices, sin presión', 'minimización', 'Derivado', 'funcional', 0.6, '', 'baja')
add(1, 'si eres bueno te suben de rango rápido', 'asciendes rápido, promoción rápida, subes pronto', 'incentivo_jerárquico', 'Derivado', 'económica', 0.6, '', 'baja')
add(2, 'trae a un amigo y ganas el doble', 'si traes gente ganas más, comisión por referido', 'reclutamiento_cascada', 'Derivado', 'económica', 0.7, '', 'media')
add(1, 'la vida es corta hay que vivirla', 'YOLO, vive al máximo, el que no arriesga no gana', 'aspiracional', 'Derivado', 'sociocultural', 0.4, '', 'baja')
add(2, 'aquí no hacemos nada malo solo vigilamos', 'solo vigilamos, es inofensivo, no pasa nada', 'minimización', 'Derivado', 'funcional', 0.65, '', 'baja')
add(2, 'te damos chance de retirarte después', 'puedes dejar cuando quieras, no es permanente', 'engaño', 'Derivado', 'emocional', 0.7, '', 'media')
add(3, 'aquí no se renuncia', 'no hay renuncia, esto es de por vida, no sales', 'retención', 'Derivado', 'coercion', 0.9, '', 'media')
add(1, 'mira este video así se trabaja aquí', 'video de ostentación, video de la vida, así se vive', 'aspiracional_digital', 'Derivado', 'sociocultural', 0.5, '', 'baja')
add(2, 'vamos por unos tacos y te explico', 'te invito a comer, vamos a platicar, nos echamos unas', 'enganche_presencial', 'Derivado', 'funcional', 0.55, '', 'baja')
add(1, 'el barrio te necesita', 'tu colonia te ocupa, la comunidad te necesita', 'presión_comunitaria', 'Derivado', 'sociocultural', 0.6, '', 'baja')
add(2, 'este celular es para el trabajo no lo uses para otra cosa', 'celular de trabajo, solo para el jale, línea operativa', 'control_dispositivo', 'Derivado', 'funcional', 0.7, '', 'media')
add(3, 'ya sé quién es tu familia y dónde estudias', 'tengo toda tu información, sé todo de ti', 'amenaza_doxxing', 'Derivado', 'coercion', 0.9, '', 'media')
add(1, 'aquí no discriminamos a nadie', 'aceptamos a todos, no importa de dónde vengas', 'inclusión_falsa', 'Derivado', 'sociocultural', 0.5, '', 'baja')
add(2, 'te regalo esta cadena de oro', 'cadena de oro, esclava, reloj caro, regalos caros', 'incentivo_material', 'Derivado', 'económica', 0.65, '', 'baja')
add(4, 'ya llegó el cargamento manda gente', 'llegó la carga, necesitamos manos, manda gente al punto', 'orden_operativa', 'Derivado', 'operativo', 0.7, '', 'baja')

print(f'\n=== BATCH 5 FINAL COMPLETE ===')
print(f'Added: {added}')
print(f'Skipped (duplicates): {skipped}')
total_all = data['total_added'] + added
for fase in [1,2,3,4]:
    start_count = {1: 101, 2: 91, 3: 85, 4: 101}
    total_for_phase = counters[fase] - start_count[fase]
    print(f'  Fase {fase}: {total_for_phase} total new (all batches)')
print(f'\n========================================')
print(f'TOTAL NEW PATTERNS: {total_all}')
print(f'ORIGINAL DATASET: 374')
print(f'GRAND TOTAL: {374 + total_all}')
print(f'========================================')
if 374 + total_all >= 1000:
    print('META ALCANZADA: 1000+ PATRONES!')
else:
    print(f'Faltan: {1000 - 374 - total_all}')

with open('final_counters.json', 'w') as f:
    json.dump({'counters': counters, 'total_added': total_all, 'grand_total': 374 + total_all}, f)
