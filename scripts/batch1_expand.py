#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch 1: Dataset expansion from web research findings."""

import csv, json, os
from datetime import datetime

with open('existing_signals.json', 'r', encoding='utf-8') as f:
    existing = set(s.lower().strip() for s in json.load(f))

print(f'Loaded {len(existing)} existing signals')

OUTPUT_FILE = 'dataset_expansion_results.csv'
headers = ['id','fase','señal_base','variantes','intención','fuente','tipo','peso','url_fuente','fecha_hallazgo','confiabilidad']

with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()

counters = {1: 101, 2: 91, 3: 85, 4: 101}
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
# EMOJIS CARTEL (Colmex/Infobae/Milenio verified)
# ============================================================
INF_EMOJI = 'https://www.infobae.com/mexico/2025/04/20/estos-son-los-emojis-que-ocupa-el-crimen-organizado-para-reclutar-jovenes-en-mexico/'
MIL_EMOJI = 'https://www.milenio.com/policia/narcotrafico/emojis-hashtags-simbologia-del-narco-redes-sociales-y-su-significado'

add(1, '\U0001f977 ninja', '\U0001f977 encapuchado, ninja emoji, sicario emoji', 'identidad_criminal', 'Colmex/Infobae', 'simb\u00f3lica', 0.7, INF_EMOJI, 'alta')
add(1, '\U0001fa96 casco militar', '\U0001fa96 armed, helmet emoji', 'propaganda', 'Colmex/Infobae', 'simb\u00f3lica', 0.65, INF_EMOJI, 'alta')
add(1, '\U0001f608 diablo', '\U0001f479 namahague, demonio emoji, makab\u00e9lico', 'identidad_criminal', 'Colmex/Infobae', 'simb\u00f3lica', 0.6, INF_EMOJI, 'alta')
add(1, '\U0001f9ff ojo turco', '\U0001f9ff ma\u00f1a, ojo de la ma\u00f1a', 'identidad_criminal', 'Colmex/Infobae', 'simb\u00f3lica', 0.6, INF_EMOJI, 'alta')
add(1, '\U0001f196 NG emoji', '4\U0001f196, cuatro letras NG, CJNG emoji', 'identidad_cartel', 'Colmex/Milenio', 'simb\u00f3lica', 0.75, MIL_EMOJI, 'alta')
add(1, '\U0001f3a9 sombrero emoji', '\U0001f920 sombrero Mayo, hat emoji', 'identidad_cartel', 'Colmex/Milenio', 'simb\u00f3lica', 0.65, MIL_EMOJI, 'alta')
add(1, '\U0001f353\U0001f41f fresa y pez', '\U0001f353 El Fresa, \U0001f41f El Pez, Familia Michoacana', 'identidad_cartel', 'Colmex/Milenio', 'simb\u00f3lica', 0.7, MIL_EMOJI, 'alta')

# ============================================================
# HASHTAGS RECLUTAMIENTO (TikTok - Colmex verified)
# ============================================================
INF_BELIC = 'https://www.infobae.com/mexico/2025/04/18/belicones-y-trabajo-para-la-mana-las-frases-en-tiktok-que-usa-el-narco-para-el-reclutamiento-criminal-de-jovenes/'

add(1, '#4letras', '#4l, #cuatroletras', 'identidad_cartel', 'Colmex', 'hashtag', 0.8, INF_BELIC, 'alta')
add(1, '#gentedelmz', '#operativamz, #mayozambada', 'identidad_cartel', 'Colmex', 'hashtag', 0.75, INF_BELIC, 'alta')
add(1, '#trabajoparalamaña', '#maña, trabajo para la maña', 'reclutamiento', 'Colmex', 'hashtag', 0.85, INF_BELIC, 'alta')
add(1, '#belicones', '#frasesbelicas, #makabelico', 'narcocultura', 'Colmex', 'hashtag', 0.6, INF_BELIC, 'alta')
add(1, '#nuevageneracion', '#ng, #señormencho, #ElSeñorDeLosGallos', 'identidad_cartel', 'Colmex/Milenio', 'hashtag', 0.75, MIL_EMOJI, 'alta')

# ============================================================
# FRASES RECLUTAMIENTO DIRECTO
# ============================================================
MIL_REC = 'https://www.milenio.com/policia/reclutamiento-de-menores-en-mexico-asi-operan-los-carteles-en-redes'

add(1, 'a mí me interesa', 'yo quiero jale, me interesa el trabajo, yo le entro', 'auto_reclutamiento', 'Milenio/Colmex', 'sociocultural', 0.75, MIL_REC, 'alta')
add(1, 'la empresa cuida a los suyos', 'aquí cuidamos a la familia, la compañía protege', 'lealtad', 'Infobae/Colmex', 'sociocultural', 0.7, INF_BELIC, 'alta')
add(1, 'se buscan halcones', 'necesitamos halcones, buscamos vigilantes, se necesitan ojos', 'reclutamiento_operativo', 'Colmex/Infobae', 'funcional', 0.85, INF_BELIC, 'alta')
add(1, 'se necesitan cocineros', 'buscamos cocineros, se buscan químicos', 'reclutamiento_operativo', 'Colmex/Infobae', 'funcional', 0.85, INF_BELIC, 'alta')
add(1, 'pagos semanales y protección a toda costa', 'pago semanal con protección, te protegemos y pagamos', 'incentivo', 'Colmex', 'económica', 0.8, INF_BELIC, 'alta')

# ============================================================
# OFERTAS ECONÓMICAS ESPECÍFICAS
# ============================================================
PROC_TIKTOK = 'https://www.proceso.com.mx/nacional/2026/4/17/policia-de-jalisco-evita-reclutamiento-de-dos-menores-contactados-por-crimen-organizado-en-tiktok-372393.html'
INF_OFERTAS = 'https://www.infobae.com/mexico/2024/02/04/las-ofertas-laborales-del-narco-asi-es-como-el-crimen-organizado-recluta-a-jovenes-en-redes/'
PROC_LASTRA = 'https://www.proceso.com.mx/nacional/2025/3/24/teuchitlan-asi-operaba-el-lastra-para-reclutar-personas-para-el-cjng-en-el-rancho-izaguirre-347986.html'

add(1, '15 mil pesos a la semana', '15mil semanales, quince mil por semana', 'incentivo_económico', 'Milenio/Proceso', 'económica', 0.85, MIL_REC, 'alta')
add(1, '20 mil pesos semanales', '20mil semanal, veinte mil a la semana', 'incentivo_económico', 'Proceso', 'económica', 0.85, PROC_TIKTOK, 'alta')
add(1, '18 mil pesos quincenales más comida y hospedaje', '18mil quincenal con hospedaje', 'incentivo_económico', 'Infobae', 'económica', 0.85, INF_OFERTAS, 'alta')
add(1, 'de 4 a 12 mil pesos semanales', '4mil a 12mil semanal', 'incentivo_económico', 'Proceso', 'económica', 0.8, PROC_LASTRA, 'alta')
add(2, 'hospedaje pagos y entrenamiento', 'incluye hospedaje y entrenamiento, te damos casa', 'incentivo', 'Colmex/Infobae', 'económica', 0.75, INF_BELIC, 'alta')

# ============================================================
# OFERTAS LABORALES FALSAS
# ============================================================
MIL_NARCO = 'https://www.milenio.com/policia/narcotrafico/narco-redes-crimen-organizado-recluta-jovenes-mexico'
INF_TACT = 'https://www.infobae.com/mexico/2025/03/01/nuevas-tacticas-del-crimen-organizado-el-reclutamiento-de-menores-a-traves-de-videojuegos-y-redes-sociales-en-mexico/'
INF_FALSAS = 'https://www.infobae.com/mexico/2026/04/19/ofertas-de-trabajo-falsas-en-redes-sociales-una-trampa-que-puede-terminar-en-violacion-o-secuestro/'

add(1, 'trabajo de chofer bien pagado', 'chofer privado, se busca chofer', 'oferta_falsa', 'Milenio/Infobae', 'económica', 0.7, MIL_NARCO, 'media')
add(1, 'seguridad privada sin experiencia', 'guardia de seguridad sin exp', 'oferta_falsa', 'Proceso/Infobae', 'económica', 0.75, PROC_LASTRA, 'alta')
add(1, 'apoyo logístico sin documentos', 'trabajo sin papeles, no necesitas documentos', 'oferta_falsa', 'Infobae', 'económica', 0.7, INF_TACT, 'media')
add(1, 'trabajo en campo agrícola', 'jornalero, trabajo de campo', 'oferta_falsa', 'Infobae', 'económica', 0.6, INF_OFERTAS, 'media')
add(1, 'trabajo en call center', 'empleo call center, operador telefónico', 'oferta_falsa', 'Infobae', 'económica', 0.55, INF_OFERTAS, 'media')
add(1, 'tu currículum está en revisión', 'estamos revisando tu perfil, ya vimos tu solicitud', 'enganche_laboral', 'Infobae', 'funcional', 0.7, INF_FALSAS, 'alta')
add(1, 'altos salarios por tareas simples sin experiencia', 'gana mucho sin experiencia, sueldos altos sin estudios', 'oferta_falsa', 'Infobae', 'económica', 0.65, INF_FALSAS, 'alta')
add(1, 'se solicita personal para despacho jurídico', 'empleo en despacho, trabajo en ventas, agencia de edecanes', 'oferta_falsa', 'Infobae', 'económica', 0.65, INF_FALSAS, 'alta')
add(1, 'trabajo como pintor o albañil', 'pintor, albañil, ayudante de obra', 'oferta_falsa', 'Infobae', 'económica', 0.6, INF_OFERTAS, 'media')

# ============================================================
# GAMING / ROBLOX / FREE FIRE
# ============================================================
MIL_ROBLOX = 'https://www.milenio.com/policia/roblox-crimen-organizado-recluta-difunde-mensajes-en-videojuego'

add(2, 'te regalo skins y loot', 'te doy power-ups, te paso consumibles', 'incentivo_gaming', 'Infobae', 'funcional', 0.7, INF_TACT, 'media')
add(2, 'únete a mi equipo de Roblox', 'entra al team, únete a mi clan', 'contacto_gaming', 'Milenio', 'funcional', 0.65, MIL_ROBLOX, 'alta')
add(2, 'eres muy bueno en el juego te tengo una propuesta', 'juegas muy bien, tienes talento', 'perfilamiento_gaming', 'Infobae/Segob', 'funcional', 0.7, INF_TACT, 'media')
add(2, 'te puedo dar dinero real si juegas conmigo', 'te pago por jugar, te doy lana real', 'incentivo_gaming', 'Segob/Infobae', 'económica', 0.75, INF_TACT, 'media')
add(2, 'escenarios narco en Roblox', 'juegos narco Roblox, partidas conflicto Sinaloa', 'narcopropaganda_gaming', 'Milenio', 'funcional', 0.6, MIL_ROBLOX, 'alta')
add(2, 'pásame tu WhatsApp para hablar fuera del juego', 'dame tu número, hablamos por WhatsApp', 'aislamiento_gaming', 'Segob/Infobae', 'funcional', 0.8, INF_TACT, 'media')
add(2, 'mándame una foto tuya para saber con quién juego', 'foto tuya, cómo eres, mándame selfie', 'perfilamiento_gaming', 'Segob/Infobae', 'funcional', 0.75, INF_TACT, 'media')
add(2, 'te mando diamantes en Free Fire', 'te regalo diamantes, te paso gemas, te compro pase', 'incentivo_gaming', 'Vanguardia', 'funcional', 0.7, 'https://vanguardia.com.mx/noticias/mexico/carteles-usan-videojuegos-como-free-fire-para-reclutar-ninos-y-adolescentes-AD13892561', 'alta')
add(2, 'gallo y pizza en juegos Roblox', 'emojis narco dentro de Roblox, simbolos cartel en juego', 'narcopropaganda_gaming', 'Milenio', 'simbólica', 0.65, MIL_ROBLOX, 'alta')

# ============================================================
# GROOMING DIGITAL (Derecho de la Red verified)
# ============================================================
GROOM = 'https://derechodelared.com/las-frases-mas-comunes-del-grooming/'

add(2, 'nos gustan las mismas cosas vamos a ser buenos amigos', 'tenemos mucho en común, somos iguales', 'confianza', 'Derecho de la Red', 'emocional', 0.65, GROOM, 'alta')
add(2, 'pareces triste cuéntame qué te pasa', 'te noto mal, desahógate conmigo', 'perfilamiento', 'Derecho de la Red', 'emocional', 0.7, GROOM, 'alta')
add(2, 'si te envío una foto mía me envías una tuya', 'intercambiamos fotos, foto por foto', 'perfilamiento', 'Derecho de la Red', 'emocional', 0.75, GROOM, 'alta')
add(2, 'eres el amor de mi vida', 'te amo, sin ti no puedo vivir', 'manipulación_emocional', 'Derecho de la Red', 'emocional', 0.65, GROOM, 'alta')
add(2, 'nunca te pediré algo que no quieras hacer', 'tú decides, yo respeto tus límites', 'manipulación_emocional', 'Derecho de la Red', 'emocional', 0.7, GROOM, 'alta')
add(2, 'diles a tus papás que vas a hacer un trabajo', 'diles que vas con un amigo, inventa algo', 'aislamiento', 'Derecho de la Red', 'emocional', 0.8, GROOM, 'alta')
add(3, 'si no haces lo que digo colgaré tus fotos en la red', 'publico tus fotos, las subo a internet', 'amenaza_digital', 'Derecho de la Red', 'coercion', 0.9, GROOM, 'alta')
add(3, 'en otros países esto es normal', 'todos lo hacen, no tiene nada de malo', 'normalización', 'Derecho de la Red', 'emocional', 0.6, GROOM, 'alta')
add(2, 'cuál es tu película favorita', 'qué música te gusta, cuáles son tus hobbies', 'perfilamiento', 'Derecho de la Red', 'emocional', 0.5, GROOM, 'alta')
add(2, 'tú pones los límites cuando quieras que paremos dímelo', 'tú controlas la situación, tú mandas', 'manipulación_emocional', 'Derecho de la Red', 'emocional', 0.7, GROOM, 'alta')

# ============================================================
# ROLES CARTEL (Infobae hierarchy article)
# ============================================================
INF_HIER = 'https://www.infobae.com/mexico/2025/11/15/desde-el-halcon-hasta-el-patron-asi-funciona-la-estructura-interna-de-los-carteles-mexicanos/'

add(4, 'necesitamos punteros', 'se buscan punteros, vigía armado', 'reclutamiento_operativo', 'Infobae', 'operativo', 0.8, INF_HIER, 'alta')
add(4, 'necesitamos estacas', 'unidad móvil, estaca de sicarios', 'reclutamiento_operativo', 'Infobae', 'operativo', 0.85, INF_HIER, 'alta')
add(4, 'zancudo', 'zancudos, menores sicarios, chamaco armado', 'reclutamiento_menores', 'Infobae', 'operativo', 0.85, INF_HIER, 'alta')
add(4, 'necesitamos droneros', 'operador de drones, piloto de drone', 'reclutamiento_operativo', 'Infobae', 'operativo', 0.75, INF_HIER, 'alta')
add(1, 'pollitos de colores', 'pollito, pollitos, niños halcones', 'reclutamiento_menores', 'Excélsior', 'sociocultural', 0.7, 'https://www.excelsior.com.mx/nacional/narco-recluta-a-ninos-y-los-suma-a-pollitos-de-colores-como-halcones/1718351', 'alta')
add(4, 'necesitamos troqueros', 'troquero, cargador, jalador', 'reclutamiento_operativo', 'Infobae', 'operativo', 0.7, INF_HIER, 'alta')
add(4, 'gente del cerro', 'gente de la sierra, sicarios rurales', 'reclutamiento_operativo', 'Infobae', 'operativo', 0.7, INF_HIER, 'alta')
add(4, 'se buscan escoltas', 'escolta personal, guardaespaldas', 'reclutamiento_operativo', 'Infobae', 'operativo', 0.75, INF_HIER, 'alta')
add(4, 'jefe de plaza', 'comandante de plaza, encargado de zona', 'jerarquía', 'Infobae', 'operativo', 0.7, INF_HIER, 'alta')

# ============================================================
# SEXTORSIÓN
# ============================================================
SEXT = 'https://www.eluniversal.com.mx/nacion/ninas-ninos-y-adolescentes-principales-victimas-de-sextorsion-en-mexico-incrementa-delito-en-56/'
FINCEN = 'https://www.fincen.gov/news/news-releases/fincen-issues-notice-financially-motivated-sextortion'

add(3, 'tengo tus fotos íntimas y las voy a publicar', 'publico tus nudes, mando tus fotos a todos', 'amenaza_sextorsión', 'REDIM/Consejo Ciudadano', 'coercion', 0.95, SEXT, 'alta')
add(3, 'mándame más material o le digo a tus papás', 'le cuento a tu familia, tus papás van a saber', 'amenaza_sextorsión', 'REDIM/Consejo Ciudadano', 'coercion', 0.9, SEXT, 'alta')
add(3, 'mándame dinero o publico todo', 'págame o subo tus fotos, deposita o difundo', 'extorsión_financiera', 'FinCEN/REDIM', 'coercion', 0.95, FINCEN, 'alta')
add(2, 'soy tu amigo virtual confía en mí', 'soy tu amigo en línea, puedes confiar', 'grooming', 'Consejo Ciudadano', 'emocional', 0.65, SEXT, 'media')

# ============================================================
# RANCHO IZAGUIRRE / MECANISMOS ENGANCHE
# ============================================================
add(2, 'te citamos en la central de autobuses', 'nos vemos en la central, pasa a la terminal', 'punto_encuentro', 'Proceso', 'funcional', 0.85, PROC_TIKTOK, 'alta')
add(2, 'te recogemos en un vehículo', 'mandamos carro por ti, va una camioneta', 'punto_encuentro', 'Proceso', 'funcional', 0.85, PROC_TIKTOK, 'alta')
add(3, 'entrega tus pertenencias', 'dame tu celular, deja tus cosas', 'control', 'Proceso', 'coercion', 0.9, PROC_LASTRA, 'alta')
add(3, 'vas a estar incomunicado un mes', 'sin teléfono, sin contacto con nadie', 'aislamiento_forzado', 'Proceso', 'coercion', 0.9, PROC_LASTRA, 'alta')
add(3, 'si te quieres ir te va mal', 'el que se raja le va peor, no hay salida', 'amenaza_deserción', 'Proceso', 'coercion', 0.95, PROC_LASTRA, 'alta')

# ============================================================
# CÓDIGOS DROGA
# ============================================================
UNIV = 'https://www.univision.com/noticias/narcotrafico/el-lenguaje-secreto-que-usan-los-traficantes'

add(4, 'la señora lechuga', 'señora lechuga, la doña verde (marihuana)', 'código_droga', 'Vice/Univision', 'operativo', 0.6, UNIV, 'media')
add(4, 'la muchacha', 'la morra, la nena (metanfetamina)', 'código_droga', 'Vice/Univision', 'operativo', 0.6, UNIV, 'media')
add(4, 'la piñata', 'la piñata, el pollito (metanfetamina)', 'código_droga', 'Vice/Univision', 'operativo', 0.6, UNIV, 'media')
add(4, 'el pescado', 'queso blanco, los tamales (cocaína)', 'código_droga', 'Vice/Univision', 'operativo', 0.6, UNIV, 'media')
add(4, 'el aguacate', 'el chorizo, manteca (heroína)', 'código_droga', 'Vice/Univision', 'operativo', 0.55, UNIV, 'media')
add(4, 'azuquítar', 'cremita, talco, perico (cocaína)', 'código_droga', 'Vice/Univision', 'operativo', 0.6, UNIV, 'media')
add(4, 'special k', 'especial k, ketamina, keta', 'código_droga', 'Univision', 'operativo', 0.55, UNIV, 'media')
add(4, 'grapa', 'grapa (gramo), puntita (dosis), piquito (mínimo)', 'código_cantidad', 'Univision', 'operativo', 0.55, UNIV, 'media')
add(4, 'tachas', 'tachas, chochos, pastillas (éxtasis)', 'código_droga', 'Univision', 'operativo', 0.6, UNIV, 'media')
add(4, 'chemo', 'chemo, cemento, mona', 'código_droga', 'Univision', 'operativo', 0.5, UNIV, 'media')

# ============================================================
# FINANCIEROS SEXTORSIÓN (FinCEN)
# ============================================================
add(3, 'for tutoring (memo engañosa)', 'gift, for school (memo falso en pago)', 'evasión_detección', 'FinCEN', 'financiero', 0.7, FINCEN, 'alta')
add(3, 'pagos rápidos P2P a desconocidos', 'transferencias P2P repetidas a extraños', 'red_flag_financiero', 'FinCEN', 'financiero', 0.7, FINCEN, 'alta')
add(3, 'deepfake amenaza con IA', 'hicimos un video tuyo, foto deepfake, IA generó tu imagen', 'amenaza_IA', 'FinCEN', 'coercion', 0.85, FINCEN, 'alta')

# ============================================================
# PLATAFORMAS CONTACTO
# ============================================================
add(2, 'hablamos por Telegram que es más seguro', 'vamos a Telegram, mejor por app cifrada', 'migración_plataforma', 'Derivado', 'funcional', 0.7, '', 'baja')
add(2, 'te envío mi perfil de Discord', 'agrégame al Discord, entra a mi servidor', 'contacto_gaming', 'Segob', 'funcional', 0.65, INF_TACT, 'media')
add(2, 'sígueme en TikTok te mando DM', 'dame follow, te contacto por DM', 'contacto_digital', 'Colmex', 'funcional', 0.65, INF_BELIC, 'media')

# ============================================================
# MUJERES / ESTUDIANTES
# ============================================================
NMAS = 'https://www.nmas.com.mx/nacional/seguridad/emojis-hashtags-y-canciones-las-estrategias-del-narco-para-reclutar-en-tiktok/'

add(1, 'apoyo para madres solteras', 'ayuda para mamás, programa para madres solteras', 'incentivo_mujeres', 'Colmex/N+', 'económica', 0.7, NMAS, 'alta')
add(1, 'beca o apoyo para estudiantes', 'beca para jóvenes, pagamos tus estudios', 'incentivo_estudiantes', 'Colmex/N+', 'económica', 0.65, NMAS, 'alta')

# ============================================================
# LEET / EVASIÓN DE FILTROS
# ============================================================
add(1, 'tr4b4jo', 'tr4bajo, trab4jo (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(1, 'd1ner0', 'din3ro, diner0 (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(1, 'j4le', 'jal3, j4l3 (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(1, 'r3clut4', 'reclut4, r3clut4 (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(3, 't3 m4to', 'te mat0, t3 mato (leet)', 'amenaza_evasiva', 'Derivado', 'coercion', 0.6, '', 'baja')
add(1, 's1car1o', 'sic4rio, s1cario (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(1, 'h4lcon', 'halc0n, h4lc0n (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')

# ============================================================
# NARCOCULTURA / CORRIDOS
# ============================================================
add(1, 'escucha este corrido tumbado', 'oye este beat, ponle play a este corrido', 'narcocultura', 'Colmex', 'sociocultural', 0.5, INF_BELIC, 'media')
add(1, 'la vida bélica es la buena', 'vivir bélico, ser belicón', 'aspiracional', 'Colmex', 'sociocultural', 0.55, INF_BELIC, 'media')
add(1, 'yo quiero ser sicario', 'quiero ser como ellos, quiero ser del cartel', 'auto_reclutamiento', 'Vanguardia', 'sociocultural', 0.7, 'https://vanguardia.com.mx/noticias/mexico/yo-quiero-ser-sicario-que-es-el-comando-calavera-del-cjng-ligado-a-centros-de-adiestramiento-de-jovenes-HE15447257', 'alta')
add(1, 'Comando Calavera', 'Comando Calavera CJNG, grupo de adiestramiento', 'identidad_cartel', 'Vanguardia', 'sociocultural', 0.75, 'https://vanguardia.com.mx/noticias/mexico/yo-quiero-ser-sicario-que-es-el-comando-calavera-del-cjng-ligado-a-centros-de-adiestramiento-de-jovenes-HE15447257', 'alta')

# ============================================================
# VIOLENCIA NARCO (jerga documentada)
# ============================================================
ANIMAL = 'https://animalpolitico.com/2017/09/tacha-buchon-encobijado-mundo-los-narcos-se-ha-infiltrado-espanol-mexico'

add(4, 'levantón', 'dar un levantón, levantamos a alguien, secuestro narco', 'orden_directa', 'Animal Político', 'operativo', 0.85, ANIMAL, 'alta')
add(4, 'encobijado', 'encobijar, envolver cuerpo, encobijados', 'violencia', 'Animal Político', 'operativo', 0.8, ANIMAL, 'alta')
add(4, 'narcomanta', 'colgar manta, narcomensaje, mensaje narco', 'comunicación_criminal', 'Animal Político', 'operativo', 0.7, ANIMAL, 'alta')
add(4, 'plaza', 'controlar la plaza, defender la plaza, pelear la plaza', 'territorio', 'Animal Político', 'operativo', 0.65, ANIMAL, 'alta')
add(4, 'buchón', 'ser buchón, vida buchona, buchones', 'identidad_criminal', 'Animal Político', 'sociocultural', 0.5, ANIMAL, 'media')

# ============================================================
# TRATA / MIGRACIÓN
# ============================================================
add(1, 'te pasamos al otro lado', 'cruzamos la frontera, te llevamos a USA', 'tráfico_migrantes', 'N+/Colmex', 'económica', 0.7, NMAS, 'alta')

# ============================================================
# PATRONES ADICIONALES DE CAPTACIÓN
# ============================================================
add(1, 'aquí no importa si tienes antecedentes', 'con o sin antecedentes, no pedimos fedepol', 'oferta_falsa', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'sueldo desde el primer día', 'pagas inmediatas, cobras desde hoy', 'incentivo', 'Derivado', 'económica', 0.55, '', 'baja')
add(2, 'no le digas a nadie de este trabajo', 'es confidencial, no cuentes, entre nosotros', 'aislamiento', 'Derivado', 'funcional', 0.7, '', 'baja')
add(2, 'borra los mensajes después de leerlos', 'borra el chat, no dejes rastro, elimina la conversación', 'evasión', 'Derivado', 'funcional', 0.75, '', 'baja')
add(2, 'te vamos a dar un radio', 'comunicación por radio, frecuencia privada', 'reclutamiento_operativo', 'Infobae', 'funcional', 0.7, INF_HIER, 'media')

# ============================================================
# PATRONES CDN / OTROS CARTELES
# ============================================================
add(1, '18 mil pesos quincenales interesados escribir', '18k quincenal, interesados inbox, manden mensaje', 'reclutamiento_explícito', 'Infobae', 'económica', 0.85, INF_OFERTAS, 'alta')
add(1, 'trabajo para el CDN', 'Cártel del Noreste trabajo, CDN recluta', 'identidad_cartel', 'Infobae', 'funcional', 0.8, INF_OFERTAS, 'alta')

# ============================================================
# PATRONES TIJUANA / DESAPARICIONES
# ============================================================
add(2, 'ven a una entrevista de trabajo', 'acude a la entrevista, te esperamos para platicar', 'enganche_laboral', 'El Imparcial', 'funcional', 0.75, 'https://www.elimparcial.com/mexico/2026/04/24/tres-adolescentes-desaparecen-en-tijuana-tras-acudir-a-una-oferta-de-trabajo-lo-que-se-sabe-y-como-evitar-caer-en-enganos/', 'alta')
add(2, 'te trasladamos a otro estado', 'te llevamos a otro lugar, reubicación', 'enganche', 'Infobae', 'funcional', 0.8, INF_FALSAS, 'alta')

print(f'\n=== BATCH 1 COMPLETE ===')
print(f'Added: {added}')
print(f'Skipped (duplicates): {skipped}')
for fase in [1,2,3,4]:
    count = counters[fase] - [101,91,85,101][fase-1]
    print(f'  Fase {fase}: {count} new')
print(f'Total combined: {374 + added}')
print(f'Remaining to 1000: {1000 - 374 - added}')

# Save updated counters
with open('batch1_counters.json', 'w') as f:
    json.dump({'counters': counters, 'added': added}, f)
