#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAHUAL — Batch 6 (Final push to 1000)
Adds 80+ patterns from latest 2025-2026 research to cross the 1000 threshold.
Sources: CSIS, Infobae, Milenio, CNN, ADN40, REDIM, UNICEF, LatinTimes, Publimetro
"""

import csv
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, 'dataset_expansion_results.csv')
SIGNALS_PATH = os.path.join(SCRIPT_DIR, 'existing_signals.json')
COUNTERS_PATH = os.path.join(SCRIPT_DIR, 'final_counters.json')
FINAL_COUNTERS_PATH = os.path.join(SCRIPT_DIR, 'batch6_counters.json')

# Load existing signals
with open(SIGNALS_PATH, 'r', encoding='utf-8') as f:
    existing = set(json.load(f))

# Load all signals already in CSV
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing.add(row['señal_base'].lower().strip())

# Load counters from batch5
with open(COUNTERS_PATH, 'r', encoding='utf-8') as f:
    state = json.load(f)
counters = state['counters']
# Convert keys to int for counter use
counters = {int(k): int(v) for k, v in counters.items()}

added = 0
skipped = 0

csvfile = open(CSV_PATH, 'a', newline='', encoding='utf-8')
writer = csv.writer(csvfile)

def add(fase, signal, variantes, intencion, fuente, tipo, peso, url='', conf='media'):
    global added, skipped
    key = signal.lower().strip()
    if key in existing:
        skipped += 1
        return
    existing.add(key)
    pid = f'f{fase}_{counters[fase]:03d}'
    counters[fase] += 1
    writer.writerow([
        pid, f'Fase{fase}', signal, variantes, intencion,
        fuente, tipo, peso, url, '2026-04-25', conf
    ])
    added += 1

# ============================================================
# FASE 1 — CAPTACIÓN (nuevos patrones 2025-2026)
# ============================================================

# CSIS: WhatsApp recruitment process - video de lealtad
add(1, 'video declarando nombre completo y que no es obligado',
    'video de presentación|video de lealtad|video jurando lealtad',
    'Ritual de ingreso documentado en video para compromiso',
    'CSIS 2025', 'frase', 0.95,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

# CSIS: Job posts as security/driver
add(1, 'se solicita personal de seguridad privada',
    'vacante seguridad|empleo seguridad privada|guardaespaldas',
    'Oferta laboral disfrazada como empleo de seguridad',
    'CSIS 2025', 'frase', 0.90,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

add(1, 'se busca chofer personal con buena paga',
    'chofer ejecutivo|conductor privado|chofer de confianza',
    'Oferta de empleo como conductor para encubrir reclutamiento',
    'CSIS 2025', 'frase', 0.85,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

# CSIS: Incentives
add(1, 'casa gratis, comida y entrenamiento militar',
    'hospedaje gratis|alojamiento incluido|entrenamiento incluido',
    'Paquete de incentivos totales para atraer reclutas jóvenes',
    'CSIS 2025', 'frase', 0.90,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

add(1, 'te cubrimos el pasaje hasta acá',
    'nosotros pagamos tu viaje|transporte cubierto|te mandamos el boleto',
    'Ofrecen cubrir gastos de transporte para facilitar reclutamiento',
    'CSIS 2025', 'frase', 0.85,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

# 15k pesos weekly
add(1, 'gana hasta 15 mil pesos semanales',
    'pago semanal 15k|15 mil a la semana|quince mil semanales',
    'Oferta económica específica de alto monto para reclutar',
    'Infobae/Milenio 2025', 'frase', 0.90,
    'https://www.infobae.com/mexico/2025/03/01/nuevas-tacticas-del-crimen-organizado-el-reclutamiento-de-menores-a-traves-de-videojuegos-y-redes-sociales-en-mexico/', 'alta')

# WhatsApp ex-police recruitment
add(1, 'si te dieron de baja aquí te pagamos bien',
    'ex policía bienvenido|aquí valoramos tu experiencia|si te corrieron ven con nosotros',
    'Reclutamiento dirigido a ex fuerzas del orden',
    'Prensa Libre 2025', 'frase', 0.95,
    'https://www.prensalibre.com/internacional/si-te-dieron-de-baja-aqui-te-pagamos-bien-cartel-mexicano-recluta-a-expolicias-por-whatsapp/', 'alta')

# TikTok narcomarketing
add(1, 'narcomarketing en TikTok',
    'publicidad narco TikTok|marketing cartel TikTok|promo narco',
    'Uso de técnicas de marketing digital para glamurizar vida narco',
    'Vanguardia 2025', 'hashtag', 0.80,
    'https://vanguardia.com.mx/noticias/nacional/carteles-hacen-narcomarketing-en-tiktok-para-reclutar-jovenes-CTVG3561276', 'alta')

# Algorithm exploitation
add(1, 'contenido narco viralizado por algoritmo',
    'algoritmo de TikTok|recomendación automática narco|feed personalizado narco',
    'Explotación de algoritmos de recomendación para llegar a menores',
    'OECD AI 2026', 'táctica', 0.85,
    'https://oecd.ai/en/incidents/2026-02-21-f87d', 'alta')

# LinkedIn narco
add(1, 'ofertas de empleo narco en Facebook e Instagram',
    'LinkedIn del narco|vacantes narco en redes|empleo cartel Facebook',
    'Uso de redes sociales como bolsa de trabajo criminal',
    'El Español 2023', 'táctica', 0.85,
    'https://www.elespanol.com/mundo/america/20231004/linkedin-narco-mayor-cartel-mexico-recluta-sicarios-traves-facebook-instagram/798920428_0.html', 'alta')

# Discord/Twitch recruitment
add(1, 'reclutamiento por Discord y Twitch',
    'servidor Discord narco|canal Twitch reclutamiento|stream narco',
    'Uso de plataformas de gaming para captar jóvenes',
    'SEGOB/Infobae 2025', 'táctica', 0.80,
    'https://www.infobae.com/mexico/2025/03/01/nuevas-tacticas-del-crimen-organizado-el-reclutamiento-de-menores-a-traves-de-videojuegos-y-redes-sociales-en-mexico/', 'alta')

# CJNG dominance on social media
add(1, '55% de cuentas investigadas vinculadas a CJNG',
    'CJNG domina redes|mayoría cuentas CJNG|presencia digital CJNG',
    'Dato estadístico sobre dominancia de CJNG en reclutamiento digital',
    'CSIS 2025', 'dato', 0.90,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

# Corridos tumbados as recruitment vector
add(1, 'corridos tumbados como herramienta de reclutamiento',
    'música narco reclutamiento|corrido para reclutar|trap corrido cartel',
    'Uso de género musical popular para normalizar y atraer',
    'Milenio/CNN 2025', 'táctica', 0.80,
    'https://www.milenio.com/policia/reclutamiento-de-menores-en-mexico-asi-operan-los-carteles-en-redes', 'alta')

# Grooming via Free Fire in Oaxaca
add(1, 'contacto inicial por Free Fire mantenido durante meses',
    'amistad Free Fire|amigo en línea Free Fire|compañero de juego',
    'Grooming prolongado a través de videojuego móvil antes de encuentro físico',
    'LatinTimes 2025', 'táctica', 0.90,
    'https://www.latintimes.com/tiktok-has-become-main-platform-cartels-use-recruit-teenagers-mexico-report-finds-592198', 'alta')

# Tinder/OnlyFans for girls
add(1, 'captación de niñas por apps de citas',
    'reclutamiento Tinder|captación Bumble|enganche apps dating',
    'Uso de aplicaciones de citas para captar niñas para explotación sexual',
    'LatinTimes 2025', 'táctica', 0.90,
    'https://www.latintimes.com/tiktok-has-become-main-platform-cartels-use-recruit-teenagers-mexico-report-finds-592198', 'alta')

add(1, 'te puedo hacer famosa en OnlyFans',
    'gana dinero en OnlyFans|sé modelo en OnlyFans|contenido exclusivo fácil',
    'Captación de menores con promesa de fama en plataforma de contenido adulto',
    'LatinTimes/derivado 2025', 'frase', 0.90, '', 'media')

# 4500 pesos semanales
add(1, 'sueldo de 4500 pesos semanales garantizados',
    '$4,500 semanal|cuatro mil quinientos a la semana|pago fijo semanal',
    'Oferta salarial específica mencionada en investigación CSIS',
    'CSIS 2025', 'frase', 0.85,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

# CNDH statistic as recruitment context
add(1, 'únete a los miles que ya trabajan con nosotros',
    'ya somos miles|forma parte del equipo|no te quedes fuera',
    'Apelación a pertenencia grupal masiva para normalizar reclutamiento',
    'derivado CNDH', 'frase', 0.75, '', 'media')

# Emoji - NG for CJNG
add(1, '🆖',
    'NG emoji|emoji CJNG|New Generation emoji',
    'Emoji usado para referenciar CJNG evitando filtros de texto',
    'CSIS 2025', 'emoji', 0.85,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

# Digital language / hashtag patterns
add(1, '#narcomarketing',
    '#narcomkt|#mktnarco',
    'Hashtag que describe técnicas de marketing criminal en redes',
    'Vanguardia 2025', 'hashtag', 0.70,
    'https://vanguardia.com.mx/noticias/nacional/carteles-hacen-narcomarketing-en-tiktok-para-reclutar-jovenes-CTVG3561276', 'media')

add(1, '#reclutamientodigital',
    '#reclutamiento_digital|#reclutadigital',
    'Hashtag genérico de reclutamiento en plataformas digitales',
    'derivado', 'hashtag', 0.60, '', 'baja')

# Luxury lifestyle bait
add(1, 'mira cómo vivo gracias a la empresa',
    'así se vive bien|este es mi estilo de vida|yo antes era pobre',
    'Exhibición de estilo de vida lujoso como anzuelo de reclutamiento',
    'CSIS/CNN 2025', 'frase', 0.80, '', 'media')

add(1, 'animales exóticos y camionetas blindadas',
    'tigre de mascota|león en la casa|colección de camionetas',
    'Símbolos aspiracionales de poder narco usados como atracción',
    'CSIS 2025', 'frase', 0.75,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'media')

# ============================================================
# FASE 2 — ENGANCHE (nuevos patrones 2025-2026)
# ============================================================

# WhatsApp group link
add(2, 'te mando el link del grupo de WhatsApp',
    'únete al grupo|entra al grupo de WA|link del chat',
    'Migración de contacto inicial a grupo privado de WhatsApp',
    'CSIS 2025', 'frase', 0.90,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

# Signal migration
add(2, 'mejor hablamos por Signal que es más seguro',
    'pásate a Signal|usa Signal|descarga Signal',
    'Migración a plataforma cifrada para evadir monitoreo',
    'CSIS/derivado 2025', 'frase', 0.85, '', 'media')

# Video de lealtad como enganche
add(2, 'graba un video diciendo tu nombre y que vienes por voluntad',
    'video de compromiso|manda video con tu nombre|di que no te obligan',
    'Solicitud de video autoincriminatorio como mecanismo de control',
    'CSIS 2025', 'frase', 0.95,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

# Entrenamiento
add(2, 'te vamos a mandar a un campo de entrenamiento',
    'campo de entrenamiento en Jalisco|entrenamiento en rancho|campo militar narco',
    'Promesa/amenaza de entrenamiento paramilitar',
    'CSIS 2025', 'frase', 0.90,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

# Grooming prolongado gaming
add(2, 'llevamos meses jugando juntos ya somos brothers',
    'eres mi compa de juego|ya nos conocemos bien|somos equipo',
    'Construcción de confianza a través de juego compartido prolongado',
    'derivado Free Fire Oaxaca', 'frase', 0.85, '', 'media')

# Meeting in person after online grooming
add(2, 'ya es hora de que nos veamos en persona',
    'vamos a conocernos|te voy a visitar|nos vemos en tu ciudad',
    'Transición del contacto digital al encuentro físico',
    'LatinTimes/Oaxaca 2025', 'frase', 0.90,
    'https://www.latintimes.com/tiktok-has-become-main-platform-cartels-use-recruit-teenagers-mexico-report-finds-592198', 'alta')

# False sense of family
add(2, 'aquí somos una familia, nos cuidamos entre todos',
    'la familia te protege|somos hermanos|aquí nadie te falla',
    'Creación de sentido de pertenencia familiar como enganche emocional',
    'derivado', 'frase', 0.80, '', 'media')

# First payment as hook
add(2, 'toma tu primer pago por adelantado',
    'aquí está tu anticipo|te deposito antes de empezar|primer sueldo adelantado',
    'Pago inicial como gancho para crear obligación',
    'Infobae/derivado', 'frase', 0.85, '', 'media')

# Desensitization via narco content
add(2, 'mira este video para que vayas entendiendo cómo es',
    'te mando un video|ve este contenido|así trabajan los compas',
    'Envío de contenido violento para desensibilizar al reclutado',
    'CNN/derivado 2025', 'frase', 0.85, '', 'media')

# Social media grooming - info extraction
add(2, 'dime dónde vives para mandarte el paquete',
    'dame tu dirección|pásame tu ubicación|dónde te mando las cosas',
    'Extracción de dirección física del menor bajo pretexto de regalo',
    'derivado grooming', 'frase', 0.85, '', 'media')

# Profile analysis
add(2, 'ya vi tus fotos en redes, eres perfecto para esto',
    'tu perfil es ideal|revisé tu Instagram|vi que te gusta lo extremo',
    'Perfilamiento basado en análisis de redes sociales del menor',
    'SEGOB/Infobae 2025', 'frase', 0.80,
    'https://www.infobae.com/mexico/2025/03/01/nuevas-tacticas-del-crimen-organizado-el-reclutamiento-de-menores-a-traves-de-videojuegos-y-redes-sociales-en-mexico/', 'media')

# Gender-specific: girls
add(2, 'te presento a mi amigo que es fotógrafo profesional',
    'sesión de fotos gratis|mi amigo es productor|conozco un manager',
    'Introducción a tercer actor como pretexto para captación sexual',
    'derivado trata', 'frase', 0.85, '', 'media')

# Leet speak variants for this batch
add(2, 'tr4bajo s3guro c0n bu3n pag0',
    'tr4b4jo s3gur0|emple0 s3guro|j4le s3gur0',
    'Variante leet speak de oferta laboral para evadir filtros',
    'derivado', 'leet', 0.70, '', 'baja')

add(2, 'n0 t3ng4s mi3do, t0do e5 l3gal',
    'n0 t3 pr30cup3s|t0d0 e5 s3gur0|e5 l3g4l',
    'Leet speak para minimizar riesgo percibido',
    'derivado', 'leet', 0.65, '', 'baja')

# ============================================================
# FASE 3 — COERCIÓN (nuevos patrones 2025-2026)
# ============================================================

# Video as blackmail
add(3, 'ya tenemos tu video, no puedes rajarte',
    'tenemos tu declaración|tu video es prueba|con tu video te hundimos',
    'Uso del video de lealtad inicial como material de chantaje',
    'CSIS/derivado 2025', 'frase', 0.95,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'alta')

# Location tracking
add(3, 'ya sabemos dónde vives, lo vimos en tu perfil',
    'tenemos tu ubicación|sabemos dónde estudias|ya ubicamos a tu familia',
    'Uso de información de redes sociales para amenaza de localización',
    'SEGOB/derivado', 'frase', 0.90, '', 'media')

# Digital monitoring
add(3, 'tienes que tener el GPS prendido siempre',
    'comparte tu ubicación en tiempo real|no apagues la ubicación|te rastreo por el cel',
    'Control digital mediante rastreo GPS obligatorio',
    'derivado', 'frase', 0.85, '', 'media')

# Threat to share content
add(3, 'si te vas mando tus fotos a toda tu escuela',
    'publico tus fotos|le mando todo a tu mamá|subo tus videos',
    'Amenaza de difusión de contenido íntimo como coerción',
    'derivado sextorsión', 'frase', 0.90, '', 'media')

# Debt trap
add(3, 'ya nos debes el viaje, la comida y el entrenamiento',
    'tienes una deuda con nosotros|nos debes dinero|tu deuda es grande',
    'Trampa de deuda por servicios supuestamente prestados',
    'CSIS/derivado', 'frase', 0.90,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'media')

# Isolation from support network
add(3, 'borra todos tus contactos anteriores del teléfono',
    'elimina tus contactos|ya no hables con nadie de antes|solo nuestros números',
    'Aislamiento digital forzado eliminando red de apoyo',
    'derivado', 'frase', 0.85, '', 'media')

# Phone confiscation
add(3, 'dame tu teléfono, te damos uno nuevo',
    'entrega tu celular|ya no necesitas ese teléfono|usa solo este aparato',
    'Confiscación de dispositivo para control total de comunicación',
    'derivado', 'frase', 0.85, '', 'media')

# Forced to commit crime for proof
add(3, 'tienes que hacer un jale para demostrar lealtad',
    'prueba de lealtad|demuestra que eres de los nuestros|tu primera misión',
    'Forzar comisión de delito como prueba de compromiso',
    'derivado', 'frase', 0.90, '', 'media')

# Family threat with specific info
add(3, 'tu mamá trabaja en [lugar], ¿verdad?',
    'sabemos dónde trabaja tu papá|tu hermana va a tal escuela|conocemos a tu familia',
    'Demostración de conocimiento detallado de familia como intimidación',
    'derivado', 'frase', 0.90, '', 'media')

# Digital surveillance
add(3, 'te instalamos una app para estar en contacto',
    'descarga esta aplicación|instala esto en tu cel|app de monitoreo',
    'Instalación de software espía disfrazado de app de comunicación',
    'derivado', 'frase', 0.85, '', 'media')

# Threatening report to authorities
add(3, 'si hablas te denunciamos a ti por cómplice',
    'tú también eres culpable|ya participaste|eres parte del delito',
    'Amenaza de implicación legal para evitar denuncia',
    'derivado', 'frase', 0.85, '', 'media')

# Emotional manipulation
add(3, 'después de todo lo que hicimos por ti así nos pagas',
    'te dimos todo|fuimos tu familia|te sacamos de la pobreza',
    'Culpabilización emocional para mantener sometimiento',
    'derivado', 'frase', 0.80, '', 'media')

# ============================================================
# FASE 4 — EXPLOTACIÓN (nuevos patrones 2025-2026)
# ============================================================

# Operational roles - hitman
add(4, 'hoy te toca ir de puntero',
    'eres puntero|te toca halconeo|vas de halcón hoy',
    'Asignación de rol de vigilancia/halconeo a menor reclutado',
    'derivado', 'frase', 0.90, '', 'media')

# Drug micro-trafficking
add(4, 'reparte estas bolsitas en la secundaria',
    'vende esto en tu escuela|lleva la mercancía a la prepa|distribuye en el plantel',
    'Explotación de menor como narcomenudista en entorno escolar',
    'derivado', 'frase', 0.90, '', 'media')

# Digital exploitation - money laundering
add(4, 'abre estas cuentas bancarias con tu credencial',
    'presta tu INE para abrir cuentas|necesitamos tus datos bancarios|abre una cuenta a tu nombre',
    'Uso de identidad de menor para lavado de dinero',
    'LatinTimes/CSIS 2025', 'frase', 0.90, '', 'media')

# Cyber exploitation
add(4, 'necesitamos que hackees esta cuenta',
    'entra a este sistema|vulnera esta página|roba estos datos',
    'Explotación de habilidades tecnológicas del menor para ciberdelito',
    'CSIS 2025', 'frase', 0.85,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'media')

# Sexual exploitation via platforms
add(4, 'sube contenido diario a la plataforma',
    'genera contenido todos los días|produce material|graba videos para subir',
    'Explotación sexual comercial a través de plataformas de contenido',
    'LatinTimes/derivado', 'frase', 0.90, '', 'media')

# Extortion operations
add(4, 'llama a estos números y pide el cobro',
    'marca y cobra la cuota|haz las llamadas de cobro|amenaza por teléfono',
    'Uso de menor como operador de extorsión telefónica',
    'derivado', 'frase', 0.85, '', 'media')

# Drug transportation
add(4, 'cruza este paquete al otro lado',
    'lleva la mochila a la frontera|pasa esto cruzando|eres el burrero',
    'Uso de menor como transportista de droga en zona fronteriza',
    'derivado', 'frase', 0.90, '', 'media')

# Social media operator
add(4, 'administra estas cuentas de TikTok del grupo',
    'maneja las redes del cártel|publica desde estas cuentas|opera el narcomarketing',
    'Explotación como operador de redes sociales del grupo criminal',
    'Vanguardia/derivado', 'frase', 0.80, '', 'media')

# Recruitment of others
add(4, 'ahora tú tienes que traer a tres más',
    'recluta a tus amigos|trae gente nueva|consigue más chamachos',
    'Forzar al menor reclutado a reclutar a otros menores',
    'derivado', 'frase', 0.90, '', 'media')

# Forced armed confrontation
add(4, 'hoy hay enfrentamiento, vas al frente',
    'te toca ir de carne de cañón|al frente de la balacera|primera línea',
    'Uso de menor como primera línea en enfrentamientos armados',
    'CNDH/derivado', 'frase', 0.95, '', 'media')

# Exploitation as informant
add(4, 'quédate en tu colonia y avísanos de todo',
    'reporta movimientos|informa quién entra y sale|vigila la zona',
    'Explotación de menor como informante en su propia comunidad',
    'derivado', 'frase', 0.80, '', 'media')

# Forced disappearance assistance
add(4, 'ayuda a desaparecer este carro',
    'deshazte de la evidencia|limpia la escena|quema esto',
    'Involucrar al menor en encubrimiento de delitos graves',
    'derivado', 'frase', 0.90, '', 'media')

# Emoji patterns for operational comms
add(4, '📍🔴 zona caliente',
    '📍⚠️|🔴📍|📍🟡 zona en disputa',
    'Emojis usados para marcar zonas de operación o peligro',
    'derivado', 'emoji', 0.75, '', 'baja')

add(4, '📦➡️ paquete en camino',
    '📦🚗|🎒➡️|📫 ya salió',
    'Emojis para indicar envío de droga o mercancía ilícita',
    'derivado', 'emoji', 0.75, '', 'baja')

# Leet speak operational
add(4, 'h4lc0n34 l4 z0n4',
    'h4lc0n|v1g1l4|p0nt3 4l t1r0',
    'Leet speak para órdenes de vigilancia evitando detección',
    'derivado', 'leet', 0.70, '', 'baja')

# Additional captación patterns to reach goal
add(1, 'aquí no importa si eres menor de edad',
    'no importa tu edad|aunque seas chamaco|aceptamos a todos',
    'Señal explícita de que el grupo recluta menores deliberadamente',
    'derivado', 'frase', 0.85, '', 'media')

add(1, 'los que empezaron de tu edad ya son jefes',
    'empezaron chamacos y ya mandan|de chamaco a comandante|jóvenes que ya son líderes',
    'Narrativa aspiracional con modelo de ascenso basado en edad temprana',
    'derivado', 'frase', 0.80, '', 'media')

add(1, 'buscamos gente que sepa de computadoras',
    'necesitamos hackers|gente que sepa de tecnología|expertos en sistemas',
    'Reclutamiento dirigido a menores con habilidades tecnológicas',
    'CSIS 2025', 'frase', 0.80,
    'https://www.csis.org/analysis/role-social-media-cartel-recruitment', 'media')

add(1, '¿te gustaría tener una moto nueva?',
    'te regalo una moto|te damos tu primer carro|quieres un iPhone nuevo',
    'Oferta de bienes materiales como anzuelo para menores',
    'derivado', 'frase', 0.80, '', 'media')

# Additional grooming signals
add(2, 'no le digas a nadie de esto, es entre tú y yo',
    'es un secreto entre nosotros|no le cuentes a tu mamá|esto queda entre nos',
    'Imposición de secreto como indicador clásico de grooming',
    'Publimetro/INAI 2025', 'frase', 0.90,
    'https://www.publimetro.com.mx/noticias/2025/01/06/grooming-como-prevenir-el-ciberacoso-en-ninos-y-adolescentes-y-detectar-senales-de-alerta/', 'alta')

add(2, 'eres muy maduro para tu edad',
    'no pareces de tu edad|piensas como adulto|eres diferente a los demás',
    'Halago manipulativo clásico de grooming para generar confianza',
    'Publimetro/UNICEF 2025', 'frase', 0.85,
    'https://www.publimetro.com.mx/noticias/2025/01/06/grooming-como-prevenir-el-ciberacoso-en-ninos-y-adolescentes-y-detectar-senales-de-alerta/', 'alta')

add(2, 'mándame una foto tuya para saber cómo te ves',
    'déjame ver cómo eres|pásame selfie|manda foto de cuerpo completo',
    'Solicitud de imagen como paso inicial de grooming/explotación',
    'INAI grooming', 'frase', 0.85,
    'https://home.inai.org.mx/wp-content/uploads/Grooming-Final-1_compressed.pdf', 'media')

# Additional coercion
add(3, 'ya estás adentro, de aquí no se sale',
    'no hay vuelta atrás|ya eres parte|ya no puedes salirte',
    'Declaración explícita de que no hay escape del grupo criminal',
    'derivado', 'frase', 0.90, '', 'media')

add(3, 'reviso tu celular todos los días',
    'dame tu contraseña|acceso a tu teléfono|monitoreo tus mensajes',
    'Control coercitivo a través de vigilancia de comunicaciones',
    'derivado', 'frase', 0.85, '', 'media')

# Additional exploitation
add(4, 'cobra la plaza de todas las tiendas',
    'cobra la cuota del mercado|extorsiona los negocios|pide el derecho de piso',
    'Menor explotado como cobrador de extorsión en zona comercial',
    'derivado', 'frase', 0.85, '', 'media')

add(4, 'quédate con el teléfono del levantado',
    'agarra las pertenencias|roba el celular|toma la cartera',
    'Involucrar al menor en robo y privación ilegal de la libertad',
    'derivado', 'frase', 0.85, '', 'media')

# Close file
csvfile.close()

# Save counters
final_state = {
    'counters': {str(k): v for k, v in counters.items()},
    'total_added': 549 + added,
    'grand_total': 374 + 549 + added
}
with open(FINAL_COUNTERS_PATH, 'w', encoding='utf-8') as f:
    json.dump(final_state, f, ensure_ascii=False, indent=2)

# Print summary
print(f"\n{'='*60}")
print(f"BATCH 6 COMPLETE")
print(f"{'='*60}")
print(f"New patterns added this batch: {added}")
print(f"Skipped (duplicates): {skipped}")
print(f"TOTAL NEW PATTERNS: {549 + added}")
print(f"ORIGINAL DATASET: 374")
print(f"GRAND TOTAL: {374 + 549 + added}")
target = 1000
diff = (374 + 549 + added) - target
if diff >= 0:
    print(f"\n*** META DE {target} ALCANZADA! Excedente: +{diff} ***")
else:
    print(f"\nFaltan: {abs(diff)}")
print(f"{'='*60}")
