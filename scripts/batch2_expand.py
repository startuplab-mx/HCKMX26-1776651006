#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch 2: More patterns from testimonies, AFP glossary, trata, CJNG modalities."""

import csv, json, os
from datetime import datetime

with open('existing_signals.json', 'r', encoding='utf-8') as f:
    existing = set(s.lower().strip() for s in json.load(f))

# Also load batch1 signals
OUTPUT_FILE = 'dataset_expansion_results.csv'
with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        existing.add(row['señal_base'].lower().strip())

print(f'Loaded {len(existing)} total signals (original + batch1)')

with open('batch1_counters.json', 'r') as f:
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
# CJNG 4 MODALIDADES (Infobae verified)
# ============================================================
INF_4MOD = 'https://www.infobae.com/mexico/2025/04/06/estas-son-las-cuatro-modalidades-de-reclutamiento-que-el-cjng-utiliza-para-hacer-crecer-sus-ejercitos/'
INF_EXREC = 'https://www.infobae.com/mexico/2024/11/11/exrecluta-del-cjng-narra-como-se-unio-al-grupo-criminal-de-el-mencho-tras-caer-en-trampa-de-falsa-oferta-laboral/'

add(1, 'voy para sicario de las 4 letras nadie me obliga', 'voy por voluntad propia, yo quiero ser de las 4 letras', 'auto_reclutamiento', 'Infobae', 'sociocultural', 0.85, INF_4MOD, 'alta')
add(3, 'tú vas para la escuela de sicarios', 'vas a la escuela, te vamos a entrenar, escuela del CJNG', 'reclutamiento_forzado', 'Infobae', 'coercion', 0.95, INF_4MOD, 'alta')
add(3, 'voy a levantarte a ti y a toda tu familia la voy a matar', 'levanto a tu familia, mato a los tuyos, tu familia paga', 'amenaza_familiar', 'Infobae', 'coercion', 1.0, INF_4MOD, 'alta')

# CJNG testimonio ex-recluta
add(1, 'vacante de guardia de seguridad 3000 semanales', 'guardia seguridad 3mil, puesto de seguridad semanal', 'oferta_falsa', 'Infobae', 'económica', 0.8, INF_EXREC, 'alta')
add(2, 'Uber pagado para el traslado a la entrevista', 'te mandamos Uber, transporte gratis a entrevista', 'enganche_laboral', 'Infobae', 'funcional', 0.75, INF_EXREC, 'alta')
add(2, 'breve entrenamiento de tres días', 'entrenamiento corto, solo 3 días de capacitación', 'enganche_laboral', 'Infobae', 'funcional', 0.75, INF_EXREC, 'alta')
add(3, 'aquí vienes a ser sicario', 'aquí eres sicario, tu trabajo es matar', 'imposición', 'Infobae', 'coercion', 0.95, INF_EXREC, 'alta')
add(3, 'aquí ya no eres tú eres tu alias', 'ya no eres Luis eres Tocino, tu nuevo nombre es', 'control_identidad', 'Infobae', 'coercion', 0.85, INF_EXREC, 'alta')
add(3, 'tienes que pedir autorización para todo', 'permiso para todo, pedir permiso hasta para tomar agua', 'control_total', 'Infobae', 'coercion', 0.9, INF_EXREC, 'alta')
add(4, 'código 14 pecho tierra código 15 posición de tiro', 'código militar, códigos operativos, código de entrenamiento', 'instrucción_militar', 'Infobae', 'operativo', 0.8, INF_EXREC, 'alta')
add(3, 'cuidar a la gente y proteger al pueblo', 'proteger al pueblo, cuidar la gente, defender la comunidad', 'eufemismo', 'Infobae', 'emocional', 0.7, INF_EXREC, 'alta')

# ============================================================
# AFP GLOSSARY - PREDATOR CODES (verified)
# ============================================================
AFP = 'https://www.afp.gov.au/news-centre/media-release/afp-releases-glossary-terms-used-some-sex-predators-groom-children'

add(2, 'CD9 o Code 9', 'CD9, Code 9 (padres cerca)', 'código_seguridad', 'AFP', 'funcional', 0.65, AFP, 'alta')
add(2, 'GNOC', 'GNOC (get naked on camera), desnúdate en cámara', 'explotación', 'AFP', 'funcional', 0.85, AFP, 'alta')
add(2, 'LMIRL', 'LMIRL (let us meet in real life), nos vemos en persona', 'escalamiento', 'AFP', 'funcional', 0.8, AFP, 'alta')
add(2, 'NP4NP', 'NP4NP (nude pic for nude pic), foto por foto desnudo', 'explotación', 'AFP', 'funcional', 0.85, AFP, 'alta')
add(2, 'P911 o PIR', 'P911, PIR (parent in room), POS (parent over shoulder)', 'código_seguridad', 'AFP', 'funcional', 0.6, AFP, 'alta')
add(2, 'TDTM', 'TDTM (talk dirty to me), habla sucio', 'escalamiento', 'AFP', 'funcional', 0.75, AFP, 'alta')
add(2, '1174', '1174 (nude club), club de desnudos', 'código_numerico', 'AFP', 'funcional', 0.7, AFP, 'alta')
add(2, '143', '143 (I love you), te quiero en código', 'manipulación_emocional', 'AFP', 'funcional', 0.5, AFP, 'alta')
add(2, 'sneaky link', 'sneaky link (encuentro sexual secreto)', 'escalamiento', 'AFP', 'funcional', 0.7, AFP, 'alta')
add(2, 'catch a case', 'catch a case (dispuesto a ser arrestado por sexo ilegal)', 'predatorio', 'AFP', 'funcional', 0.8, AFP, 'alta')
add(2, '\U0001f351 emoji durazno', '\U0001f351 peach, emoji sexual', 'código_emoji_predador', 'AFP', 'simbólica', 0.6, AFP, 'alta')
add(2, '\U0001f924 emoji cara babeando', '\U0001f924 drooling face, deseo sexual', 'código_emoji_predador', 'AFP', 'simbólica', 0.6, AFP, 'alta')
add(2, '\U0001f35c emoji fideos', '\U0001f35c ramen bowl, noodles (nude pictures)', 'código_emoji_predador', 'AFP', 'simbólica', 0.7, AFP, 'alta')
add(2, '\U0001f33d emoji maíz', '\U0001f33d corn emoji (bypass de restricciones)', 'evasión_filtro', 'AFP', 'simbólica', 0.55, AFP, 'alta')

# ============================================================
# TRATA DE PERSONAS (Consejo Ciudadano / UNODC)
# ============================================================
CC_TRATA = 'https://consejociudadanomx.org/contenido/detectamos-nuevos-medios-de-captacion-en-trata-de-personas'
UNODC = 'https://www.unodc.org/lpomex/es/articulos/2022/uso-y-abuso-de-la-tecnologa-en-el-enganche-a-vctimas-de-trata-de-personas.html'
LADOB = 'https://www.ladobe.com.mx/2019/11/de-amor-mentiras-y-trabajo-los-metodos-de-trata/'

add(2, 'se fue con el novio', 'se la llevó el novio, se fue con su pareja', 'normalización_trata', 'Consejo Ciudadano', 'emocional', 0.7, CC_TRATA, 'alta')
add(2, 'ven conmigo te voy a cuidar', 'yo te cuido, te protejo, estás segura conmigo', 'enganche_sentimental', 'UNODC', 'emocional', 0.75, UNODC, 'alta')
add(2, 'te ofrezco trabajo de modelo', 'trabajo de modelo, edecán, imagen', 'oferta_falsa_trata', 'Consejo Ciudadano', 'económica', 0.75, CC_TRATA, 'alta')
add(2, 'vámonos a vivir juntos', 'nos vamos a otro estado, empecemos una vida', 'aislamiento_trata', 'Lado B', 'emocional', 0.8, LADOB, 'alta')
add(3, 'ya no puedes hablar con tu familia', 'corta con tu familia, no hables con ellos, no los necesitas', 'aislamiento_forzado', 'UNODC', 'coercion', 0.9, UNODC, 'alta')

# ============================================================
# TESTIMONIOS MENORES RECLUTADOS
# ============================================================
UNIV_TEST = 'https://www.univision.com/noticias/narcotrafico/testimonios-de-ninos-reclutados-por-el-narco-en-mexico'
INF_MAUR = 'https://www.infobae.com/mexico/2023/11/26/era-como-matar-animales-el-crudo-testimonio-de-mauricio-un-menor-reclutado-por-el-cartel-del-noroeste/'
HORA_AMIG = 'https://horacero.com.mx/nacional/mate-a-mi-mejor-amigo-por-lealtad-al-cartel-testimonio-del-reclutamiento-infantil-en-el-narco'

add(1, 'mis tíos me daban dinero carros joyas', 'me regalaban cosas, me daban ropa cara, me daban lana', 'incentivo_familiar', 'Univision', 'económica', 0.8, UNIV_TEST, 'alta')
add(1, 'a los 14 años entré al cartel', 'entré chamaco, desde los 14, empecé de morro', 'auto_reclutamiento', 'Univision', 'sociocultural', 0.75, UNIV_TEST, 'alta')
add(3, 'era como matar animales', 'matar era normal, como matar un pollo, no sentía nada', 'desensibilización', 'Infobae', 'coercion', 0.9, INF_MAUR, 'alta')
add(3, 'maté a mi mejor amigo por lealtad al cartel', 'matar por lealtad, prueba de lealtad, demostrar que eres fiel', 'prueba_lealtad', 'Hora Cero', 'coercion', 0.95, HORA_AMIG, 'alta')

# ============================================================
# REGALOS/DULCES COMO CAPTACIÓN INICIAL
# ============================================================
INF_NAV = 'https://www.infobae.com/mexico/2025/12/25/juguetes-dulces-y-reclutamiento-de-menores-el-trasfondo-de-la-navidad-para-el-crimen-organizado-en-mexico/'

add(1, 'te regalamos juguetes y dulces', 'regalos navideños, dulces del cartel, juguetes gratis', 'captación_inicial', 'Infobae', 'sociocultural', 0.65, INF_NAV, 'alta')
add(1, 'el reclutamiento empieza con la normalización', 'normalizar al grupo, el cartel es parte del barrio', 'normalización', 'Infobae', 'sociocultural', 0.6, INF_NAV, 'alta')
add(2, 'primero vigilar después entregar mensajes', 'empieza con halconeo, luego llevas recados, paso a paso', 'escalamiento_gradual', 'Infobae', 'funcional', 0.75, INF_NAV, 'alta')

# ============================================================
# CONTROL COERCITIVO DIGITAL
# ============================================================
ESAF = 'https://www.esafety.gov.au/key-topics/domestic-family-violence/coercive-control'

add(3, 'te estoy rastreando por el celular', 'te tengo ubicado, sé dónde estás, GPS activado', 'vigilancia', 'eSafety', 'coercion', 0.85, ESAF, 'media')
add(3, 'te controlo el dinero', 'yo manejo tu dinero, no puedes gastar sin mi permiso', 'control_financiero', 'eSafety', 'coercion', 0.8, ESAF, 'media')
add(3, 'voy a compartir tus fotos privadas', 'comparto tu pack, difundo tus íntimas', 'amenaza_digital', 'eSafety', 'coercion', 0.9, ESAF, 'media')
add(3, 'te estoy vigilando las redes', 'reviso tu Face, veo tu WhatsApp, monitoreo tus redes', 'vigilancia_digital', 'eSafety', 'coercion', 0.75, ESAF, 'media')

# ============================================================
# NARCOMENUDEO - JERGA CALLEJERA
# ============================================================
VICE = 'https://www.vice.com/es/article/narcos-mexicanos-bautizan-droga-despistar-policia/'

add(4, 'pusher', 'push, dealer, el que vende', 'rol_narcomenudeo', 'Vice', 'operativo', 0.55, VICE, 'media')
add(4, 'efectivo', 'parna, de confianza, el que vende bien', 'rol_narcomenudeo', 'Vice', 'operativo', 0.5, VICE, 'media')
add(4, 'cacique', 'jefe de punto, el que manda el punto', 'rol_narcomenudeo', 'Vice', 'operativo', 0.55, VICE, 'media')
add(4, 'blanca blanquiñosa fifí', 'blanca, fifí, clorofila (cocaína)', 'código_droga', 'Vice', 'operativo', 0.55, VICE, 'media')

# ============================================================
# RECLUTAMIENTO VÍA FACEBOOK/GRUPOS CERRADOS
# ============================================================
MIL_CJNG = 'https://www.milenio.com/policia/cjng-asi-reclutan-personas-en-redes-sociales-con-ofertas-laborales'
SOP = 'https://www.sopitas.com/teuchitlan-reclutamiento-cjng-redes-sociales/'

add(1, '12 mil pesos a la semana en redes sociales', '12k semanal, doce mil por semana', 'incentivo_económico', 'Sopitas', 'económica', 0.8, SOP, 'alta')
add(1, 'vacante de asistente de oficina', 'ayudante de oficina, asistente administrativo falso', 'oferta_falsa', 'Infobae', 'económica', 0.65, INF_4MOD, 'alta')
add(1, 'vacante de ayudante de limpieza', 'personal de limpieza, intendencia falsa', 'oferta_falsa', 'Infobae', 'económica', 0.6, INF_4MOD, 'alta')
add(2, 'entrevista de trabajo con examen médico', 'evaluación médica falsa, examen para contratación', 'enganche_laboral', 'Infobae', 'funcional', 0.7, INF_4MOD, 'alta')
add(2, 'transferimos a Zacatecas para entrenamiento', 'te mandamos a Zacatecas, viajas a otro estado para capacitación', 'traslado', 'Milenio', 'funcional', 0.8, MIL_CJNG, 'alta')

# ============================================================
# SINALOA CARTEL PROPAGANDA DIGITAL
# ============================================================
INF_SIN = 'https://www.infobae.com/mexico/2025/09/09/propaganda-digital-y-reclutamiento-forzado-el-nuevo-rostro-del-cartel-de-sinaloa-a-un-ano-de-su-guerra-interna/'

add(1, 'la Chapiza recluta', 'únete a la Chapiza, Chapitos reclutan, trabaja con los Chapitos', 'identidad_cartel', 'Infobae', 'sociocultural', 0.75, INF_SIN, 'alta')
add(1, 'propaganda narco en TikTok armas y dinero', 'videos con armas, fajos de billetes, camionetas blindadas', 'narcopropaganda', 'Infobae', 'sociocultural', 0.65, INF_SIN, 'alta')

# ============================================================
# LEET + VARIANTES ORTOGRÁFICAS ADICIONALES
# ============================================================
add(1, 'c0cin3r0', 'coc1nero, c0cinero (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(1, 'h4lc0ne0', 'halcon30, h4lconeo (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(1, 'm4t4r', 'mat4r, m4tar (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(3, 'te v0y a ub1car', 't3 ubico, te v0y a encontrar (leet)', 'amenaza_evasiva', 'Derivado', 'coercion', 0.6, '', 'baja')
add(1, 'pl4z4', 'plaz4, pl4za (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.45, '', 'baja')

# ============================================================
# PATRONES DERIVADOS ADICIONALES
# ============================================================

# Incentivos materiales
add(1, 'te damos camioneta y arma', 'troca nueva, camioneta blindada, pistola propia', 'incentivo_material', 'Derivado', 'económica', 0.7, '', 'baja')
add(1, 'ropa táctica y botas', 'uniforme táctico, te vestimos, equipo completo', 'incentivo_material', 'Proceso', 'económica', 0.65, 'https://www.proceso.com.mx/nacional/2025/3/24/teuchitlan-asi-operaba-el-lastra-para-reclutar-personas-para-el-cjng-en-el-rancho-izaguirre-347986.html', 'alta')

# Amenazas a familia
add(3, 'sabemos dónde vive tu familia', 'tenemos ubicada a tu familia, sabemos de tu mamá', 'amenaza_familiar', 'Derivado', 'coercion', 0.95, '', 'media')
add(3, 'le va a pasar algo a tu mamá', 'tu mamá paga, tu jefa va a sufrir', 'amenaza_familiar', 'Derivado', 'coercion', 0.95, '', 'media')
add(3, 'si hablas con la policía te matamos', 'no vayas con los puercos, nada de policía, cuidado con los federales', 'amenaza_silencio', 'Derivado', 'coercion', 0.95, '', 'media')

# Desensibilización progresiva
add(3, 'es normal ya te acostumbras', 'te vas acostumbrando, con el tiempo se hace fácil', 'desensibilización', 'Derivado', 'emocional', 0.7, '', 'baja')
add(3, 'aquí o te chingas o te chingan', 'es matar o morir, kill or be killed', 'amenaza_existencial', 'Derivado', 'coercion', 0.85, '', 'media')

# Control operativo
add(4, 'quédate en tu punto', 'no te muevas del punto, vigila tu zona', 'orden_directa', 'Derivado', 'operativo', 0.7, '', 'baja')
add(4, 'reporta cada hora', 'manda reporte, informa cada hora, checa y reporta', 'orden_directa', 'Derivado', 'operativo', 0.65, '', 'baja')
add(4, 'ya viene la marina', 'vienen los guachos, viene el ejército, alerta militar', 'código_alerta', 'Derivado', 'operativo', 0.7, '', 'baja')
add(4, 'hay paquete en la bodega', 'recoge el paquete, hay carga, ya está el pedido', 'código_operativo', 'Derivado', 'operativo', 0.65, '', 'baja')

# Perfilamiento de víctimas
add(2, 'cuántos años tienes', 'qué edad tienes, eres mayor de edad, eres menor', 'perfilamiento', 'Derivado', 'funcional', 0.6, '', 'baja')
add(2, 'vives solo o con tus papás', 'con quién vives, tienes familia, están tus papás', 'perfilamiento', 'Derivado', 'funcional', 0.65, '', 'baja')
add(2, 'en qué zona vives', 'de dónde eres, qué colonia, cuál es tu barrio', 'perfilamiento', 'Derivado', 'funcional', 0.6, '', 'baja')
add(2, 'tienes broncas con alguien', 'tienes pedos, te llevas mal con alguien, tienes enemigos', 'perfilamiento', 'Derivado', 'funcional', 0.6, '', 'baja')

# Aislamiento digital
add(2, 'usa esta app es más privada', 'bájate esta app, esta es más segura, Telegram o Signal', 'migración_plataforma', 'Derivado', 'funcional', 0.7, '', 'baja')
add(2, 'no uses tu nombre real', 'pon un alias, usa nombre falso, crea cuenta nueva', 'anonimización', 'Derivado', 'funcional', 0.65, '', 'baja')

# Narcocultura adicional
add(1, 'la buena vida buchona', 'vida buchona, lifestyle buchón, así se vive', 'aspiracional', 'Animal Político', 'sociocultural', 0.5, 'https://animalpolitico.com/2017/09/tacha-buchon-encobijado-mundo-los-narcos-se-ha-infiltrado-espanol-mexico', 'media')
add(1, 'Fuerza Regida Peso Pluma vida narco', 'corridos de Fuerza Regida, música de Peso Pluma, rolas bélicas', 'narcocultura', 'Colmex', 'sociocultural', 0.45, '', 'media')

# Migración/cruce frontera
add(1, 'te ayudamos a cruzar te damos trabajo del otro lado', 'cruzas y trabajas, empleo en USA, te sacamos de México', 'incentivo_migración', 'Derivado', 'económica', 0.7, '', 'baja')

# Manipulación emocional adicional
add(2, 'yo soy el único que te entiende', 'nadie te comprende como yo, solo yo te apoyo', 'manipulación_emocional', 'Derivado', 'emocional', 0.7, '', 'baja')
add(2, 'tus papás no te quieren', 'tu familia no te valora, ellos no te apoyan', 'aislamiento_emocional', 'Derivado', 'emocional', 0.75, '', 'baja')
add(2, 'aquí eres alguien aquí te respetan', 'aquí vales, te damos respeto, aquí eres importante', 'aspiracional', 'Derivado', 'emocional', 0.7, '', 'baja')
add(2, 'yo te voy a dar lo que tu familia no te da', 'te doy lo que tus papás no, yo sí te apoyo', 'manipulación_emocional', 'Derivado', 'emocional', 0.75, '', 'baja')

# Free Fire / gaming específico
add(2, 'hagamos ranked juntos en Free Fire', 'ranked, partida ranked, subimos de nivel juntos', 'contacto_gaming', 'Derivado', 'funcional', 0.55, '', 'baja')
add(2, 'te paso mi ID de Free Fire', 'agrégame en el juego, mi usuario es, add me', 'contacto_gaming', 'Derivado', 'funcional', 0.5, '', 'baja')
add(2, 'te compro el pase de batalla', 'pase gratis, te lo regalo, yo te compro el pass', 'incentivo_gaming', 'Derivado', 'funcional', 0.6, '', 'baja')

# Señales de videollamada/streaming
add(2, 'prende tu cámara quiero verte', 'enciende la cam, ponle cámara, video call', 'escalamiento', 'Derivado', 'funcional', 0.7, '', 'baja')
add(2, 'hazme un stream privado', 'stream solo para mí, transmite en privado', 'escalamiento', 'Derivado', 'funcional', 0.75, '', 'baja')

# Códigos de pago/transferencia
add(4, 'manda por Oxxo', 'depósito Oxxo, envía por Spin, transferencia BBVA', 'transferencia_código', 'Derivado', 'operativo', 0.55, '', 'baja')
add(4, 'manda cripto', 'paga en bitcoin, manda USDT, billetera crypto', 'transferencia_código', 'Derivado', 'operativo', 0.55, '', 'baja')

# Amenazas de retención
add(3, 'ya no puedes irte debes dinero', 'nos debes, tienes deuda, pagas primero', 'retención_deuda', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'si te vas te buscamos', 'no te puedes esconder, te encontramos donde sea', 'amenaza_deserción', 'Derivado', 'coercion', 0.9, '', 'media')

# Patrones de normalización
add(1, 'aquí todos trabajan desde chavos', 'todos empezaron jóvenes, de morros empiezan', 'normalización', 'Derivado', 'sociocultural', 0.55, '', 'baja')
add(1, 'el gobierno no te va a ayudar', 'el gobierno vale, nadie te ayuda, aquí sí hay apoyo', 'desconfianza_institucional', 'Derivado', 'sociocultural', 0.6, '', 'baja')

# Presión de grupo / pertenencia
add(2, 'todos tus compas ya están aquí', 'tus amigos ya entraron, todos están trabajando', 'presión_social', 'Derivado', 'emocional', 0.7, '', 'baja')
add(2, 'qué no tienes huevos', 'eres gallina, no te atrevas, no seas rajón', 'presión_masculinidad', 'Derivado', 'emocional', 0.65, '', 'baja')

# Códigos operativos adicionales
add(4, 'la gente ya subió', 'la gente está lista, ya están los compas, ya subieron', 'código_operativo', 'Derivado', 'operativo', 0.6, '', 'baja')
add(4, 'llévate el plomo', 'carga la mercancía, agarra el fierro, lleva el equipo', 'orden_directa', 'Derivado', 'operativo', 0.75, '', 'baja')

# WhatsApp/Telegram grupos de reclutamiento
add(2, 'te agrego al grupo de WhatsApp', 'te meto al grupo, entra al grupo, link del grupo', 'contacto_grupo', 'Derivado', 'funcional', 0.65, '', 'baja')
add(2, 'manda ubicación para recogerte', 'comparte tu ubicación, pasa tu ubis, manda pin', 'enganche', 'Derivado', 'funcional', 0.8, '', 'media')

# Emisión de identidad falsa (documentos)
add(4, 'te hacemos credencial falsa', 'INE falsa, credencial de la empresa, identificación', 'operativo', 'Derivado', 'operativo', 0.6, '', 'baja')

print(f'\n=== BATCH 2 COMPLETE ===')
print(f'Added: {added}')
print(f'Skipped (duplicates): {skipped}')
for fase in [1,2,3,4]:
    start_count = {1: 101, 2: 91, 3: 85, 4: 101}
    total_for_phase = counters[fase] - start_count[fase]
    print(f'  Fase {fase}: {total_for_phase} total new (across all batches)')
print(f'Total combined: {374 + 111 + added}')
print(f'Remaining to 1000: {1000 - 374 - 111 - added}')

with open('batch2_counters.json', 'w') as f:
    json.dump({'counters': counters, 'added_batch2': added, 'total_added': 111 + added}, f)
