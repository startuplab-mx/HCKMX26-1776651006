#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch 3: Training school rules, extortion patterns, corridos, more grooming, operational codes."""

import csv, json, os
from datetime import datetime

with open('existing_signals.json', 'r', encoding='utf-8') as f:
    existing = set(s.lower().strip() for s in json.load(f))

OUTPUT_FILE = 'dataset_expansion_results.csv'
with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        existing.add(row['señal_base'].lower().strip())

print(f'Loaded {len(existing)} total signals')

with open('batch2_counters.json', 'r') as f:
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
# ESCUELA DE SICARIOS CJNG (reglas y lenguaje)
# ============================================================
INF_ESC = 'https://www.infobae.com/mexico/2025/03/19/no-robar-no-drogarse-y-no-pelearse-testimonios-revelan-las-reglas-en-escuela-de-sicarios-del-cjng/'

add(3, 'no robar no drogarse no pelearse', 'reglas del campo, las tres reglas, prohibido robar drogar pelear', 'control_entrenamiento', 'Infobae', 'coercion', 0.8, INF_ESC, 'alta')
add(3, 'la única forma de salir es con los pies por delante', 'sales muerto, la salida es la muerte, no hay salida vivo', 'amenaza_muerte', 'Infobae', 'coercion', 1.0, INF_ESC, 'alta')
add(3, 'no hagas preguntas', 'no preguntes, calla y obedece, no cuestiones', 'control_total', 'Infobae', 'coercion', 0.85, INF_ESC, 'alta')
add(1, 'vacante en rancho o tequilera', 'trabajo en rancho, empresa de tequila, empleo en campo', 'oferta_falsa', 'Infobae', 'económica', 0.7, INF_ESC, 'alta')
add(1, '2000 a 4000 pesos semanales en Facebook', '2mil a 4mil semanal, entre 2 y 4 mil', 'incentivo_económico', 'Infobae', 'económica', 0.75, INF_ESC, 'alta')

# ============================================================
# CORRIDOS Y CANCIONES RECLUTAMIENTO (Politico.mx verified)
# ============================================================
POLIT = 'https://polls.politico.mx/2025/05/14/las-canciones-usadas-por-el-narco-para-reclutar-en-tik-tok/'

add(1, 'El Gallito de Fuerza Regida', 'El 03, El Flaco, Gente del General (canciones CJNG)', 'narcocultura', 'Politico.mx', 'sociocultural', 0.55, POLIT, 'alta')
add(1, 'Fierro por la 300', 'Fierro por la 300, Lenin Ramírez', 'narcocultura', 'Politico.mx', 'sociocultural', 0.5, POLIT, 'alta')
add(1, 'Las cuatro de las cuatro letras', 'canción CJNG, Los Alegres del Barranco', 'narcocultura', 'Politico.mx', 'sociocultural', 0.55, POLIT, 'alta')
add(1, 'Comandante Toro', 'Beto Vega Comandante Toro, corrido CJNG vs Sinaloa', 'narcocultura', 'Politico.mx', 'sociocultural', 0.5, POLIT, 'alta')

# ============================================================
# EXTORSIÓN / COBRO DE PISO (menores involucrados)
# ============================================================
INF_EXT = 'https://www.infobae.com/america/mexico/2021/02/02/al-estilo-del-padrino-pero-con-una-cabeza-de-cerdo-mantas-y-redes-sociales-asi-amenazan-los-narcos-en-mexico/'

add(3, 'te toca pagar tu cuota', 'paga la cuota, es hora de la cuota, ya toca cuota', 'extorsión', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'si no pagas te cerramos el negocio', 'te quemamos, cerramos tu changarro, te levantamos', 'extorsión', 'Infobae', 'coercion', 0.9, INF_EXT, 'alta')
add(3, 'sabemos dónde van tus hijos a la escuela', 'sabemos los horarios de tus hijos, conocemos su escuela', 'amenaza_familiar', 'Infobae', 'coercion', 0.95, INF_EXT, 'alta')
add(4, 'cobra la cuota de tu zona', 've a cobrar el piso, cobra la renta a los locales', 'orden_extorsión', 'Derivado', 'operativo', 0.75, '', 'media')

# ============================================================
# WhatsApp EXTORSIÓN PATTERNS
# ============================================================
ADN = 'https://www.adn40.mx/es-tendencia/extorsion-por-whatsapp-como-son-los-mensajes-que-reciben-las-victimas'

add(2, 'lo siento quién eres te encontré en mi libreta', 'disculpa quién eres, te tengo en mis contactos', 'contacto_inicial_estafa', 'ADN40', 'funcional', 0.6, ADN, 'alta')
add(3, 'te encontraré atente a las consecuencias', 'te voy a encontrar, vigila tu espalda', 'amenaza_WhatsApp', 'ADN40', 'coercion', 0.85, ADN, 'alta')
add(2, 'reunámonos y divirtámonos grupo WhatsApp', 'únete al grupo, ven a divertirte, grupo exclusivo', 'contacto_grupo', 'ADN40', 'funcional', 0.6, ADN, 'alta')

# ============================================================
# GROOMING - INDICADORES (Gobierno Guanajuato + UNAM)
# ============================================================
EFECTO = 'https://efectoprevencion.guanajuato.gob.mx/ninas-ninos-y-adolescentes/ciberacoso-sexual/'
UNAM = 'https://www.gaceta.unam.mx/de-que-se-trata-eso-del-grooming-y-como-cuidamos-a-las-infancias-y-adolescencias/'

add(2, 'soy otro niño como tú', 'también soy menor, tengo tu edad, soy de tu edad', 'suplantación_edad', 'Gobierno Guanajuato', 'emocional', 0.75, EFECTO, 'alta')
add(2, 'te ofrezco ser mi novio/novia', 'quieres ser mi novia, seamos novios, noviazgo virtual', 'enganche_sentimental', 'UNAM', 'emocional', 0.7, UNAM, 'alta')
add(3, 'si no me mandas más fotos le cuento a todos', 'le digo a tu escuela, lo sabe todo mundo', 'amenaza_difusión', 'Gobierno Guanajuato', 'coercion', 0.9, EFECTO, 'alta')
add(2, 'esto es un secreto entre nosotros', 'nadie tiene que saber, es nuestro secreto, privado', 'aislamiento', 'UNAM', 'emocional', 0.8, UNAM, 'alta')

# ============================================================
# PATRONES TRATA (amor/enamoramiento)
# ============================================================
add(2, 'me voy a casar contigo', 'nos casamos, vamos a estar juntos, formamos familia', 'enganche_sentimental', 'Lado B', 'emocional', 0.75, 'https://www.ladobe.com.mx/2019/11/de-amor-mentiras-y-trabajo-los-metodos-de-trata/', 'alta')
add(2, 'te voy a sacar de aquí', 'te saco de tu pueblo, vámonos lejos, nueva vida', 'enganche_sentimental', 'UNODC', 'emocional', 0.75, 'https://www.unodc.org/lpomex/es/articulos/2022/uso-y-abuso-de-la-tecnologa-en-el-enganche-a-vctimas-de-trata-de-personas.html', 'alta')

# ============================================================
# DERIVADOS: AMENAZAS ESCALADAS
# ============================================================
add(3, 'ya no eres civil eres soldado', 'eres sicario ahora, ya perteneces, ya eres de los nuestros', 'imposición_identidad', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'el que se raja no sale vivo', 'rajarse es morirse, no hay marcha atrás', 'amenaza_deserción', 'Derivado', 'coercion', 0.9, '', 'media')
add(3, 'tú ya manchaste las manos', 'ya tienes sangre, ya mataste, ya no hay vuelta', 'retención_culpa', 'Derivado', 'coercion', 0.9, '', 'media')
add(3, 'aquí se obedece o se muere', 'obedeces o te mueres, órdenes son órdenes', 'amenaza_muerte', 'Derivado', 'coercion', 0.95, '', 'media')
add(3, 'ya saben que trabajas con nosotros', 'los rivales ya saben, te tienen fichado', 'amenaza_exposición', 'Derivado', 'coercion', 0.85, '', 'media')

# ============================================================
# DERIVADOS: FASE 1 CAPTACIÓN ADICIONALES
# ============================================================
add(1, 'te presento a mi patrón', 'conoce al jefe, te llevo con el mero mero', 'presentación_jerárquica', 'Derivado', 'funcional', 0.6, '', 'baja')
add(1, 'hay vacantes en mi empresa', 'mi empresa busca gente, donde trabajo hay lugar', 'oferta_falsa', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'no preguntes solo ven', 'no hagas preguntas, solo di que sí, ven y ya', 'presión', 'Derivado', 'funcional', 0.65, '', 'baja')
add(1, 'el patrón paga bien y rápido', 'el jefe paga bien, aquí sí se gana', 'incentivo', 'Derivado', 'económica', 0.65, '', 'baja')
add(1, 'yo empecé de abajo y mira cómo estoy', 'mira mi troca, mira mi vida, así vivo yo', 'aspiracional', 'Derivado', 'sociocultural', 0.6, '', 'baja')
add(1, 'trabaja inteligente no trabaja duro', 'el dinero fácil, no seas burro, trabaja con la cabeza', 'aspiracional', 'Derivado', 'sociocultural', 0.55, '', 'baja')
add(1, 'te pago más que lo que ganas en un mes', 'en un día ganas más, lo que ganas en un mes aquí es un día', 'incentivo_económico', 'Derivado', 'económica', 0.7, '', 'baja')

# ============================================================
# DERIVADOS: FASE 2 ENGANCHE ADICIONALES
# ============================================================
add(2, 'te mando fotos de cómo se vive aquí', 'mira las fotos, así se vive, mira el estilo', 'aspiracional_digital', 'Derivado', 'funcional', 0.55, '', 'baja')
add(2, 'ven a conocer te va a gustar', 'ven a ver cómo está, conoce el lugar', 'enganche', 'Derivado', 'funcional', 0.6, '', 'baja')
add(2, 'solo es de entrada después haces lo que quieras', 'solo al principio es pesado, luego es fácil', 'minimización', 'Derivado', 'emocional', 0.65, '', 'baja')
add(2, 'ya hablé con el jefe y te quiere conocer', 'el patrón quiere verte, el jefe pregunta por ti', 'presión_social', 'Derivado', 'funcional', 0.7, '', 'baja')
add(2, 'mira cuánto gané esta semana', 'screenshot de dinero, foto de billetes, ostentación', 'aspiracional_digital', 'Derivado', 'económica', 0.65, '', 'baja')
add(2, 'te consigo novia aquí hay muchas morras', 'hay morras, te presentamos chavas, aquí hay de todo', 'incentivo_social', 'Derivado', 'emocional', 0.55, '', 'baja')

# ============================================================
# DERIVADOS: FASE 3 COERCIÓN ADICIONALES
# ============================================================
add(3, 'te filmé haciendo eso y tengo el video', 'te grabé, tengo evidencia, video tuyo comprometedor', 'chantaje_video', 'Derivado', 'coercion', 0.9, '', 'media')
add(3, 'ya le debes al patrón', 'tienes deuda con el jefe, el patrón quiere su dinero', 'retención_deuda', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'tu familia no te va a creer', 'nadie te va a creer, quién te va a ayudar', 'aislamiento_psicológico', 'Derivado', 'emocional', 0.8, '', 'media')
add(3, 'ya estás metido demasiado profundo', 'ya estás adentro, ya no hay salida, estás hundido', 'retención', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'si me dejas publico nuestras conversaciones', 'publico los chats, expongo todo, capturas de pantalla', 'amenaza_digital', 'Derivado', 'coercion', 0.85, '', 'media')

# ============================================================
# DERIVADOS: FASE 4 EXPLOTACIÓN ADICIONALES
# ============================================================
add(4, 've al punto y espera instrucciones', 'al punto, espera indicaciones, posiciónate', 'orden_directa', 'Derivado', 'operativo', 0.7, '', 'baja')
add(4, 'mueve el paquete de A a B', 'lleva la carga, transporta el paquete, mueve la mercancía', 'orden_transporte', 'Derivado', 'operativo', 0.75, '', 'baja')
add(4, 'cobra y reporta', 'cobra la cuota y avisa, reporta la lana', 'orden_directa', 'Derivado', 'operativo', 0.7, '', 'baja')
add(4, 'cuida la cocina', 'vigila el lab, cuida la cocina, no dejes entrar a nadie', 'orden_directa', 'Derivado', 'operativo', 0.75, '', 'baja')
add(4, 'entrega el sobre', 'el sobre, la lana, el dinero, entrégaselo al contacto', 'orden_directa', 'Derivado', 'operativo', 0.65, '', 'baja')
add(4, 'hay un encargo', 'encargo del patrón, hay trabajo, hay tarea', 'eufemismo_violencia', 'Derivado', 'operativo', 0.8, '', 'media')
add(4, 'dale piso', 'piso a ese, dale piso, elimínalo', 'orden_violenta', 'Derivado', 'operativo', 0.95, '', 'media')
add(4, 'haz el jale limpio', 'limpio, sin testigos, que no quede nada', 'orden_violenta', 'Derivado', 'operativo', 0.9, '', 'media')
add(4, 'desaparece el cuerpo', 'deshaz del cuerpo, que no lo encuentren, encajuela', 'orden_violenta', 'Derivado', 'operativo', 0.95, '', 'media')

# ============================================================
# EMOJI ADICIONALES (derivados de fuentes)
# ============================================================
add(1, '\U0001f4b0\U0001f4b5 dinero emoji', '\U0001f4b0 bolsa dinero, \U0001f4b5 dólar, money bags', 'incentivo_visual', 'Derivado', 'simbólica', 0.5, '', 'baja')
add(1, '\U0001f52b\U0001f4aa arma y músculo', '\U0001f52b pistola, \U0001f4aa fuerte, poder emoji', 'narcopropaganda', 'Derivado', 'simbólica', 0.55, '', 'baja')
add(1, '\U0001f451 corona', '\U0001f451 king, corona, el patrón, el jefe', 'jerarquía', 'Derivado', 'simbólica', 0.5, '', 'baja')
add(4, '\U0001f4cd ubicación compartida', '\U0001f4cd pin, ubicación, localización compartida', 'operativo_digital', 'Derivado', 'simbólica', 0.6, '', 'baja')

# ============================================================
# VARIANTES LEET ADICIONALES
# ============================================================
add(1, 'gu4rd14', 'guard1a, gu4rdia, guardia (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.45, '', 'baja')
add(1, 'ch0f3r', 'chof3r, ch0fer, chofer (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.45, '', 'baja')
add(3, 'm4tar3', 'mat4re, m4tare (leet amenaza)', 'amenaza_evasiva', 'Derivado', 'coercion', 0.6, '', 'baja')
add(1, '4rm4s', 'arm4s, 4rmas (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.45, '', 'baja')
add(1, 'n4rc0', 'narc0, n4rco (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.45, '', 'baja')

# ============================================================
# HASHTAGS ADICIONALES
# ============================================================
add(1, '#vidabuchona', '#buchona, #estilobuchon, vida buchona TikTok', 'narcocultura', 'Derivado', 'hashtag', 0.5, '', 'baja')
add(1, '#cartellife', '#narcolife, #cartellifestyle, cartel life TikTok', 'narcocultura', 'Derivado', 'hashtag', 0.5, '', 'baja')
add(1, '#corridos2025', '#corridosbelicos, #corridosnuevos', 'narcocultura', 'Derivado', 'hashtag', 0.45, '', 'baja')
add(1, '#chapiza', '#lachapiza, #chapitos, chapiza TikTok', 'identidad_cartel', 'Derivado', 'hashtag', 0.7, '', 'media')
add(1, '#sueldobueno', '#pagasemanal, #ganadinerofacil, #dinerorapido', 'reclutamiento', 'Derivado', 'hashtag', 0.55, '', 'baja')

# ============================================================
# FRASES ASPIRACIONALES DE NARCOCULTURA
# ============================================================
add(1, 'con cara de niño bueno y bolsillos de narco', 'cara de santo bolsillos llenos, parece santo pero gana', 'aspiracional', 'Derivado', 'sociocultural', 0.45, '', 'baja')
add(1, 'primero Dios y luego el patrón', 'Dios y el patrón, la fe y el jefe', 'lealtad', 'Derivado', 'sociocultural', 0.5, '', 'baja')
add(1, 'de la nada a todo en 6 meses', 'en poco tiempo estás arriba, rápido creces', 'aspiracional', 'Derivado', 'sociocultural', 0.5, '', 'baja')
add(1, 'mejor vivir 5 años como rey que 50 como buey', 'vivir rápido morir joven, vida corta pero buena', 'aspiracional', 'Colmex', 'sociocultural', 0.6, '', 'media')

# ============================================================
# MANIPULACIÓN SEXUAL PROGRESIVA
# ============================================================
add(2, 'mándame una foto en traje de baño', 'foto en bikini, foto sin playera, enseña un poco', 'escalamiento_sexual', 'Derivado', 'emocional', 0.75, '', 'media')
add(2, 'solo entre nosotros nadie más lo va a ver', 'es privado, nadie lo ve, solo yo', 'manipulación', 'Derivado', 'emocional', 0.8, '', 'media')
add(3, 'ya vi tu cara en un video que circula', 'tu cara está en un video, circula un video tuyo', 'amenaza_deepfake', 'Derivado', 'coercion', 0.85, '', 'media')
add(2, 'te compro ropa bonita si me mandas fotos', 'te regalo ropa, te compro lo que quieras a cambio', 'transaccional', 'Derivado', 'emocional', 0.75, '', 'media')

# ============================================================
# CÓDIGOS DE COMUNICACIÓN OPERATIVA
# ============================================================
add(4, 'ya cayó el paquete', 'llegó la carga, ya está el envío, la entrega está lista', 'código_operativo', 'Derivado', 'operativo', 0.6, '', 'baja')
add(4, 'la carretera está limpia', 'libre la ruta, no hay retenes, camino libre', 'código_alerta', 'Derivado', 'operativo', 0.65, '', 'baja')
add(4, 'hay retén adelante', 'retén en km X, cuidado hay control, policía adelante', 'código_alerta', 'Derivado', 'operativo', 0.7, '', 'baja')
add(4, 'el contacto está en el punto', 'el compa ya llegó, el enlace está listo', 'código_operativo', 'Derivado', 'operativo', 0.6, '', 'baja')
add(4, 'manda las fotos del objetivo', 'fotos del target, ubicación del objetivo, foto de la persona', 'orden_vigilancia', 'Derivado', 'operativo', 0.8, '', 'media')

# ============================================================
# PATRONES DE RECLUTAMIENTO EN COMUNIDAD
# ============================================================
add(1, 'en este barrio todos saben quién manda', 'aquí manda el cartel, todos saben, el barrio es nuestro', 'territorialidad', 'Derivado', 'sociocultural', 0.6, '', 'baja')
add(1, 'te conviene estar del lado correcto', 'mejor estar con nosotros, te conviene ser aliado', 'presión_comunitaria', 'Derivado', 'sociocultural', 0.7, '', 'media')
add(1, 'el cartel ayuda al pueblo', 'nosotros damos despensas, ayudamos a la gente', 'normalización', 'Derivado', 'sociocultural', 0.6, '', 'baja')
add(1, 'aquí la ley somos nosotros', 'la ley es el cartel, nosotros mandamos, aquí no hay gobierno', 'territorialidad', 'Derivado', 'sociocultural', 0.65, '', 'media')

# ============================================================
# PATRONES DE SEXTORSIÓN FINANCIERA ADICIONALES
# ============================================================
add(3, 'deposita 5000 pesos o publico todo', 'deposita o difundo, manda 5mil o se entera tu familia', 'extorsión_financiera', 'Derivado', 'coercion', 0.9, '', 'media')
add(3, 'ya hicimos un grupo con tus fotos', 'grupo de WhatsApp con tus fotos, creamos un perfil falso tuyo', 'amenaza_digital', 'Derivado', 'coercion', 0.9, '', 'media')
add(3, 'manda el dinero por CoDi o transferencia', 'CoDi, transferencia SPEI, pago inmediato', 'extorsión_financiera', 'Derivado', 'financiero', 0.7, '', 'baja')

# ============================================================
# PATRONES DE IMPERSONACIÓN
# ============================================================
add(2, 'tengo 15 años y estoy en prepa', 'también estoy en la escuela, estoy en secundaria', 'suplantación_edad', 'Derivado', 'emocional', 0.7, '', 'media')
add(2, 'también juego Free Fire qué nivel eres', 'a qué nivel juegas, cuál es tu rango', 'contacto_gaming', 'Derivado', 'funcional', 0.55, '', 'baja')
add(2, 'me gusta tu perfil te puedo seguir', 'me gustó tu foto, qué bonita tu foto, tienes buen perfil', 'contacto_inicial', 'Derivado', 'funcional', 0.55, '', 'baja')

# ============================================================
# LENGUAJE DE NORMALIZACIÓN DE VIOLENCIA
# ============================================================
add(1, 'los corridos cuentan la verdad', 'la música dice la neta, los corridos son la vida real', 'normalización', 'Derivado', 'sociocultural', 0.45, '', 'baja')
add(1, 'así es la vida en el barrio', 'así se vive aquí, es normal, todos lo hacen', 'normalización', 'Derivado', 'sociocultural', 0.5, '', 'baja')
add(1, 'el que no tranza no avanza', 'hay que tranzar, el vivo del muerto, la maña es necesaria', 'normalización', 'Derivado', 'sociocultural', 0.55, '', 'media')

# ============================================================
# TIKTOK LIVE PATTERNS
# ============================================================
add(2, 'entra a mi live te cuento cómo ganar dinero', 'live de oportunidades, en vivo te explico, ven al stream', 'reclutamiento_live', 'Derivado', 'funcional', 0.65, '', 'baja')
add(2, 'manda gifts en el live y te contacto', 'manda regalos, compra coins y te explico', 'monetización_reclutamiento', 'Derivado', 'funcional', 0.55, '', 'baja')

# ============================================================
# INSTAGRAM / FACEBOOK DM PATTERNS
# ============================================================
add(2, 'vi tu historia y me gustó', 'bonita tu historia, vi tu story, me gustó tu reel', 'contacto_inicial', 'Derivado', 'funcional', 0.5, '', 'baja')
add(2, 'te mando un link no le digas a nadie', 'abre este link, entra a este enlace privado', 'phishing', 'Derivado', 'funcional', 0.7, '', 'media')

# ============================================================
# PATRONES DE RECLUTAMIENTO RELIGIOSO/ESPIRITUAL
# ============================================================
add(1, 'la Santa Muerte nos protege', 'Santa Muerte, la niña blanca, la flaquita protege', 'espiritualidad_criminal', 'Derivado', 'sociocultural', 0.55, '', 'media')
add(1, 'San Judas Tadeo patrón de los desesperados', 'San Juditas, el santo de la maña, patrono del narco', 'espiritualidad_criminal', 'Derivado', 'sociocultural', 0.5, '', 'media')
add(1, 'Jesús Malverde protege a los narcos', 'Malverde, santo de los narcos, patrono del crimen', 'espiritualidad_criminal', 'Derivado', 'sociocultural', 0.5, '', 'media')

# ============================================================
# PRESIÓN DE PARES / RECLUTAMIENTO SOCIAL
# ============================================================
add(2, 'no seas maricón entra con nosotros', 'no seas puto, échale huevos, no seas cobarde', 'presión_masculinidad', 'Derivado', 'emocional', 0.7, '', 'media')
add(2, 'ya todos en la colonia están con nosotros', 'todo el barrio trabaja, la colonia entera', 'presión_comunitaria', 'Derivado', 'emocional', 0.65, '', 'baja')
add(2, 'si entras te presentamos al patrón', 'conoces al jefe, te damos rango, subes rápido', 'incentivo_jerárquico', 'Derivado', 'funcional', 0.6, '', 'baja')

# ============================================================
# CÓDIGOS NUMÉRICOS
# ============================================================
add(4, 'código 1 alerta', 'código 1, alerta 1, prioridad 1', 'código_alerta', 'Derivado', 'operativo', 0.6, '', 'baja')
add(4, 'punto caliente', 'zona caliente, zona roja, punto de riesgo', 'código_territorial', 'Derivado', 'operativo', 0.65, '', 'baja')
add(4, 'zona fría', 'zona segura, punto limpio, zona tranquila', 'código_territorial', 'Derivado', 'operativo', 0.6, '', 'baja')

print(f'\n=== BATCH 3 COMPLETE ===')
print(f'Added: {added}')
print(f'Skipped (duplicates): {skipped}')
total_all = 111 + data['added_batch2'] + added
for fase in [1,2,3,4]:
    start_count = {1: 101, 2: 91, 3: 85, 4: 101}
    total_for_phase = counters[fase] - start_count[fase]
    print(f'  Fase {fase}: {total_for_phase} total new (all batches)')
print(f'Total combined: {374 + total_all}')
print(f'Remaining to 1000: {1000 - 374 - total_all}')

with open('batch3_counters.json', 'w') as f:
    json.dump({'counters': counters, 'added_batch3': added, 'total_added': total_all}, f)
