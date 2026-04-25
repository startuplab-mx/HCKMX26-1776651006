#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch 4: Communication codes, manipulation, catfishing, marketplace, more derivados to reach 1000."""

import csv, json, os
from datetime import datetime

with open('existing_signals.json', 'r', encoding='utf-8') as f:
    existing = set(s.lower().strip() for s in json.load(f))

OUTPUT_FILE = 'dataset_expansion_results.csv'
with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        existing.add(row['señal_base'].lower().strip())

print(f'Loaded {len(existing)} total signals')

with open('batch3_counters.json', 'r') as f:
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
# CÓDIGOS NUMÉRICOS NARCO (Xataka/interceptados)
# ============================================================
XAT = 'https://www.xataka.com.mx/telecomunicaciones/estas-son-las-claves-y-metodos-que-usan-los-narcotraficantes-para-comunicarse'

add(4, 'vamos a la playa', 'vamos a la playa (hacer cita), vernos en la playa', 'código_cita', 'Xataka', 'operativo', 0.7, XAT, 'alta')
add(4, 'hace calor', 'hace calor (cita confirmada)', 'código_confirmación', 'Xataka', 'operativo', 0.65, XAT, 'alta')
add(4, 'la cerveza está fría', 'cerveza fría (en camino), ya salió la cerveza', 'código_tránsito', 'Xataka', 'operativo', 0.7, XAT, 'alta')
add(4, 'estoy con mi esposa', 'con mi esposa (regresando), ya estoy con la mujer', 'código_retorno', 'Xataka', 'operativo', 0.65, XAT, 'alta')
add(4, 'tengo diarrea', 'diarrea (verificación en curso)', 'código_verificación', 'Xataka', 'operativo', 0.65, XAT, 'alta')
add(4, 'Mercedes', 'Mercedes (transacción completada)', 'código_completado', 'Xataka', 'operativo', 0.65, XAT, 'alta')
add(4, 'hamburguesa', 'hamburguesa (artículo no encontrado)', 'código_faltante', 'Xataka', 'operativo', 0.6, XAT, 'alta')
add(4, 'me gusta tu hermana', 'tu hermana (problema encontrado)', 'código_problema', 'Xataka', 'operativo', 0.65, XAT, 'alta')
add(4, 'vamos al cine', 'cine (nos siguen con dinero), al cine', 'código_seguimiento', 'Xataka', 'operativo', 0.7, XAT, 'alta')
add(4, 'soda e hielo', 'soda (metanfetamina), hielo (cristal)', 'código_droga', 'Infobae/DEA', 'operativo', 0.75, 'https://www.infobae.com/mexico/2024/05/08/estas-son-las-aplicaciones-que-usan-el-cartel-de-sinaloa-y-los-chapitos-para-comunicarse-sin-dejar-rastro/', 'alta')
add(4, '100 200 500 (cantidades codificadas)', '100=100mil, 200=200mil, números para cantidades', 'código_cantidad', 'DEA/Xataka', 'operativo', 0.7, XAT, 'alta')
add(4, 'color del día lunes rojo martes amarillo', 'código de colores por día, rojo lunes, azul viernes', 'código_temporal', 'Xataka', 'operativo', 0.65, XAT, 'alta')

# ============================================================
# CATFISHING / PERFIL FALSO
# ============================================================
WLS = 'https://www.welivesecurity.com/es/estafas-enganos/catfishing-5-senales-estafa/'

add(2, 'acabo de crear mi perfil agrégame', 'perfil nuevo, recién me hice cuenta, soy nuevo aquí', 'catfishing', 'WeLiveSecurity', 'funcional', 0.6, WLS, 'media')
add(2, 'nunca puedo hacer videollamada', 'mi cámara no sirve, no tengo datos para video, después hacemos video', 'catfishing', 'WeLiveSecurity', 'funcional', 0.65, WLS, 'media')
add(2, 'te cuento un secreto personal mío', 'te voy a contar algo íntimo, solo tú sabes esto', 'manipulación', 'WeLiveSecurity', 'emocional', 0.7, WLS, 'media')
add(2, 'siento que ya te conozco de toda la vida', 'hay una conexión especial, es como si nos conociéramos', 'manipulación_emocional', 'WeLiveSecurity', 'emocional', 0.6, WLS, 'media')

# ============================================================
# MARKETPLACE/FACEBOOK EXPLOTACIÓN
# ============================================================
UNIV_MK = 'https://www.eluniversal.com.mx/nacion/marketplace-fraude-y-comercio-ilegal-en-la-red-de-facebook/'
PUB = 'https://www.publimetro.com.mx/nacional/2025/03/18/cuidado-6-de-cada-10-empleos-en-redes-son-falsos-estafas-y-trampas-del-crimen/'

add(1, '6 de cada 10 empleos en redes son falsos', 'empleo falso Facebook, mayoría de ofertas son estafa', 'estadística', 'Publimetro', 'económica', 0.7, PUB, 'alta')
add(1, 'se solicita personal por inbox', 'manda inbox, interesados al inbox, DM para más info', 'reclutamiento_digital', 'Derivado', 'funcional', 0.65, '', 'baja')

# ============================================================
# MANIPULACIÓN PSICOLÓGICA (frases documentadas)
# ============================================================
MANIP = 'https://lamenteesmaravillosa.com/las-frases-mas-comunes-de-los-manipuladores/'

add(3, 'eso nunca sucedió te lo estás inventando', 'no pasó eso, estás loca/loco, te lo imaginas', 'gaslighting', 'La Mente es Maravillosa', 'emocional', 0.75, MANIP, 'alta')
add(3, 'si me quisieras de verdad lo harías', 'hazlo por mí, si me amas demuéstralo, lo haces o no me quieres', 'chantaje_emocional', 'La Mente es Maravillosa', 'emocional', 0.8, MANIP, 'alta')
add(3, 'nadie más te va a querer como yo', 'soy el único que te quiere, sin mí no eres nadie', 'dependencia', 'La Mente es Maravillosa', 'emocional', 0.8, MANIP, 'alta')
add(3, 'la culpa es tuya por hacerme enojar', 'tú me provocas, es tu culpa, mira lo que me haces hacer', 'culpabilización', 'La Mente es Maravillosa', 'emocional', 0.75, MANIP, 'alta')
add(3, 'estás exagerando no es para tanto', 'exageras, no es grave, estás siendo dramático/a', 'minimización', 'La Mente es Maravillosa', 'emocional', 0.7, MANIP, 'alta')

# ============================================================
# APPS DE COMUNICACIÓN NARCO
# ============================================================
INF_APPS = 'https://www.infobae.com/mexico/2024/05/08/estas-son-las-aplicaciones-que-usan-el-cartel-de-sinaloa-y-los-chapitos-para-comunicarse-sin-dejar-rastro/'

add(2, 'descarga esta app que se borran los mensajes', 'app de mensajes que desaparecen, mensajes temporales, app efímera', 'migración_plataforma', 'Infobae', 'funcional', 0.7, INF_APPS, 'alta')
add(2, 'usa Wickr Me para hablar', 'Wickr, Threema, app cifrada narco', 'migración_plataforma', 'Infobae/DEA', 'funcional', 0.7, INF_APPS, 'alta')

# ============================================================
# RECLUTAMIENTO REDIM (estados/edad específica)
# ============================================================
REDIM = 'https://blog.derechosinfancia.org.mx/2025/09/30/reclutamiento-y-utilizacion-de-ninas-ninos-y-adolescentes-por-agrupaciones-delictivas-en-mexico-2010-2023/'
QP = 'https://quinto-poder.mx/tendencias/2025/03/30/mapa-estados-donde-carteles-reclutan-a-menores-de-edad-50634.html'

add(1, 'reclutan niños desde los 9 años', 'desde los 9, desde chamaquitos, desde primaria', 'reclutamiento_edad_temprana', 'REDIM', 'sociocultural', 0.8, REDIM, 'alta')
add(1, 'niños de 6 a 12 años como mensajeros', 'mensajero de 6 años, niño mandadero, chamaquito lleva recados', 'reclutamiento_menores', 'REDIM', 'sociocultural', 0.8, REDIM, 'alta')

# ============================================================
# DERIVADOS MASIVOS: FASE 1 - CAPTACIÓN
# ============================================================
# Ofertas laborales variantes
add(1, 'trabajo de mesero bien pagado', 'mesero, cantinero, garrotero', 'oferta_falsa', 'Derivado', 'económica', 0.55, '', 'baja')
add(1, 'empleo en bodega o almacén', 'almacenista, bodeguero, cargador de bodega', 'oferta_falsa', 'Derivado', 'económica', 0.55, '', 'baja')
add(1, 'trabajo de repartidor buen sueldo', 'repartidor, delivery, moto repartidor', 'oferta_falsa', 'Derivado', 'económica', 0.55, '', 'baja')
add(1, 'promotora o edecán eventos VIP', 'edecán, promotora, modelo eventos', 'oferta_falsa_trata', 'Derivado', 'económica', 0.7, '', 'media')
add(1, 'trabajo medio tiempo para estudiantes', 'empleo para estudiantes, horario flexible, compatible con escuela', 'oferta_falsa', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'gana desde tu celular sin salir de casa', 'trabaja desde casa, empleo remoto, gana con tu teléfono', 'oferta_falsa', 'Derivado', 'económica', 0.55, '', 'baja')
add(1, 'necesitamos gente en tu zona', 'hay vacantes en tu colonia, tu barrio necesita personal', 'reclutamiento_local', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'pago diario en efectivo', 'cobras diario, pago en cash, lana al día', 'incentivo', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'no pido experiencia ni estudios', 'sin experiencia, sin estudios, sin requisitos', 'oferta_falsa', 'Derivado', 'económica', 0.6, '', 'baja')

# Narcocultura adicional
add(1, 'la maña te da lo que el gobierno no', 'el cartel ayuda más que el gobierno, aquí sí hay apoyo', 'desconfianza_institucional', 'Derivado', 'sociocultural', 0.6, '', 'baja')
add(1, 'en la calle se aprende más que en la escuela', 'la calle enseña, la escuela no sirve, la vida es la maestra', 'desvalorización_educación', 'Derivado', 'sociocultural', 0.55, '', 'baja')
add(1, 'mi jefe tiene una troca del año', 'troca nueva, carro de lujo, mira cómo anda el patrón', 'aspiracional', 'Derivado', 'sociocultural', 0.5, '', 'baja')
add(1, 'aquí tu familia nunca más pasa hambre', 'tu mamá ya no sufre, tus hermanos ya comen, ayuda a tu familia', 'incentivo_familiar', 'Derivado', 'económica', 0.7, '', 'media')
add(1, 'te damos celular nuevo y datos ilimitados', 'cel nuevo, datos, plan ilimitado, iPhone', 'incentivo_material', 'Derivado', 'económica', 0.6, '', 'baja')

# ============================================================
# DERIVADOS MASIVOS: FASE 2 - ENGANCHE
# ============================================================
add(2, 'bájate esta app para ganar dinero', 'app para ganar, descarga y gana, app de comisiones', 'phishing', 'Derivado', 'funcional', 0.6, '', 'baja')
add(2, 'manda tu INE para darte de alta', 'foto de tu INE, necesito tu CURP, manda identificación', 'perfilamiento', 'Derivado', 'funcional', 0.7, '', 'media')
add(2, 'te hago una cuenta bancaria a mi nombre', 'cuenta prestanombres, tu cuenta pero yo la manejo', 'control_financiero', 'Derivado', 'funcional', 0.75, '', 'media')
add(2, 'te muestro cómo funciona en persona', 'te explico en vivo, nos vemos y te enseño', 'escalamiento_presencial', 'Derivado', 'funcional', 0.7, '', 'media')
add(2, 'dame acceso a tu cuenta de Instagram', 'dame tu contraseña, comparte tu acceso, préstame tu cuenta', 'control_digital', 'Derivado', 'funcional', 0.75, '', 'media')
add(2, 'te presto dinero pero me lo pagas después', 'te adelanto lana, te doy un préstamo, después arreglamos', 'enganche_deuda', 'Derivado', 'económica', 0.75, '', 'media')
add(2, 'mañana empiezas es urgente', 'es para hoy, necesitamos ya, no hay tiempo que perder', 'urgencia', 'Derivado', 'funcional', 0.65, '', 'baja')
add(2, 'solo necesito que guardes esto en tu casa', 'guárdame un paquete, ten esto unos días, cuida esta caja', 'complicidad_gradual', 'Derivado', 'funcional', 0.75, '', 'media')
add(2, 'te invito a una fiesta exclusiva', 'fiesta VIP, reunión privada, evento exclusivo', 'enganche_social', 'Derivado', 'funcional', 0.6, '', 'baja')
add(2, 'te presento gente importante', 'conoces personas de poder, gente conectada', 'enganche_social', 'Derivado', 'funcional', 0.6, '', 'baja')
add(2, 'ya deposité un adelanto a tu cuenta', 'ya te mandé dinero, checa tu cuenta, ya está el depósito', 'enganche_deuda', 'Derivado', 'económica', 0.75, '', 'media')
add(2, 'no le cuentes a tu familia hasta que estés bien', 'después les dices, cuando tengas dinero ya les cuentas', 'aislamiento', 'Derivado', 'emocional', 0.7, '', 'baja')
add(2, 'confía en mí yo pasé por lo mismo', 'yo también estuve así, te entiendo, pasé lo que tú', 'empatía_falsa', 'Derivado', 'emocional', 0.65, '', 'baja')

# ============================================================
# DERIVADOS MASIVOS: FASE 3 - COERCIÓN
# ============================================================
add(3, 'ya eres cómplice si hablas te hundes', 'eres cómplice, si dices algo tú también caes', 'retención_legal', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'tenemos videos de lo que hiciste', 'te grabamos, hay evidencia, todo está documentado', 'chantaje', 'Derivado', 'coercion', 0.9, '', 'media')
add(3, 'ya te reporté como desertora te buscan', 'te reportaron, hay orden, te andan buscando', 'amenaza_persecución', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'a tu mamá le mandé las capturas', 'tu mamá ya sabe, le mandé pruebas', 'amenaza_familiar', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'deposita cada semana o hay consecuencias', 'paga semanal, cuota obligatoria, no faltes al pago', 'extorsión_periódica', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'mandé tu ubicación a mis compas', 'ya saben dónde estás, mandé tu GPS', 'amenaza_ubicación', 'Derivado', 'coercion', 0.9, '', 'media')
add(3, 'crees que puedes esconderte', 'no te puedes esconder, te vamos a encontrar, no hay donde huyas', 'amenaza_persecución', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'haz lo que te digo y no pasa nada', 'obedece y estarás bien, haz caso y no hay bronca', 'imposición', 'Derivado', 'coercion', 0.75, '', 'media')
add(3, 'por las buenas o por las malas', 'tú decides, cooperas o te va mal', 'ultimátum', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'a ver si tu familia te busca cuando desaparezcas', 'te desaparecemos, nadie te va a encontrar', 'amenaza_desaparición', 'Derivado', 'coercion', 0.95, '', 'media')

# ============================================================
# DERIVADOS MASIVOS: FASE 4 - EXPLOTACIÓN
# ============================================================
add(4, 'cobra en tal punto a tal hora', 'cobras a las X en el punto Y, recoge la lana ahí', 'orden_directa', 'Derivado', 'operativo', 0.7, '', 'baja')
add(4, 'vigila esta casa y reporta quién entra', 'halconea esta casa, vigila la entrada, quién sale y entra', 'orden_vigilancia', 'Derivado', 'operativo', 0.7, '', 'baja')
add(4, 'lleva este paquete a la dirección', 'entrega el sobre, deja el paquete en tal lugar', 'orden_transporte', 'Derivado', 'operativo', 0.7, '', 'baja')
add(4, 'toma fotos de las placas', 'anota las placas, fotografía los carros, registra vehículos', 'orden_inteligencia', 'Derivado', 'operativo', 0.65, '', 'baja')
add(4, 'avisa cuando pase la patrulla', 'pasa la tira, avisa del retén, alerta de policía', 'orden_vigilancia', 'Derivado', 'operativo', 0.7, '', 'baja')
add(4, 'cuenta la lana y separa la del patrón', 'cuenta el dinero, la parte del jefe, divide la feria', 'orden_financiera', 'Derivado', 'operativo', 0.65, '', 'baja')
add(4, 'empaca y etiqueta', 'empaqueta la mercancía, etiqueta los paquetes', 'orden_logística', 'Derivado', 'operativo', 0.65, '', 'baja')
add(4, 'limpia la casa', 'limpia la evidencia, no dejes rastro, limpia el lugar', 'orden_encubrimiento', 'Derivado', 'operativo', 0.8, '', 'media')
add(4, 'quema los teléfonos', 'destruye los celulares, tira las SIM, cambia de número', 'evasión', 'Derivado', 'operativo', 0.75, '', 'media')
add(4, 'recoge el fierro', 'agarra el cuerno, recoge las armas, fierro listo', 'orden_armamento', 'Derivado', 'operativo', 0.85, '', 'media')

# ============================================================
# EMOJI SECUENCIAS ADICIONALES
# ============================================================
add(1, '\U0001f4b8\U0001f4b8\U0001f4b8 billetes volando', 'dinero fácil emoji, lluvia de dinero, cash flying', 'incentivo_visual', 'Derivado', 'simbólica', 0.5, '', 'baja')
add(1, '\U0001f3ce\U0001f697 carros de lujo emoji', 'carro emoji, troca emoji, vida de lujo emoji', 'aspiracional', 'Derivado', 'simbólica', 0.45, '', 'baja')
add(4, '\U0001f4e6 paquete emoji', 'caja, paquete, entrega, mercancía emoji', 'código_operativo', 'Derivado', 'simbólica', 0.55, '', 'baja')
add(4, '\U0001f440\U0001f4f1 ojos y teléfono', 'vigila con el cel, reporta por teléfono', 'código_vigilancia', 'Derivado', 'simbólica', 0.55, '', 'baja')
add(3, '\u2620\ufe0f\U0001f52a calavera y cuchillo', 'amenaza de muerte emoji, te mato emoji', 'amenaza_emoji', 'Derivado', 'simbólica', 0.8, '', 'media')
add(3, '\U0001f4f7\u27a1\ufe0f\U0001f310 foto flecha mundo', 'publico tu foto al mundo, difusión global', 'amenaza_difusión', 'Derivado', 'simbólica', 0.75, '', 'media')

# ============================================================
# VARIANTES REGIONALES MEXICANAS
# ============================================================
add(1, 'aquí en el norte hay jale', 'en el norte se gana, ven para el norte, en Sinaloa hay trabajo', 'reclutamiento_regional', 'Derivado', 'económica', 0.55, '', 'baja')
add(1, 'te llevo a Culiacán', 'vente a Culiacán, en Culiacán hay chamba, Culiacán está bien', 'reclutamiento_regional', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'hay trabajo en la frontera', 'chamba en la frontera, empleo fronterizo, en Tijuana hay', 'reclutamiento_regional', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'en Jalisco se gana bien', 'en Jalisco hay jale, ven a Jalisco, GDL tiene chamba', 'reclutamiento_regional', 'Derivado', 'económica', 0.6, '', 'baja')

# ============================================================
# PATRONES ADICIONALES LEET/EVASIÓN
# ============================================================
add(1, 'p1st0la', 'pist0la, p1stola (leet arma)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(1, 'dr0g4', 'drog4, dr0ga, dr0g4 (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(1, 'c4rt3l', 'cart3l, c4rtel (leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.5, '', 'baja')
add(3, 'mu3rt3', 'muert3, mu3rte (leet amenaza)', 'amenaza_evasiva', 'Derivado', 'coercion', 0.6, '', 'baja')
add(1, 'v4c4nt3', 'vacante leet, v4cante, vacan7e', 'evasión_filtro', 'Derivado', 'funcional', 0.45, '', 'baja')
add(1, 'f3r14', 'feri4, f3ria (dinero leet)', 'evasión_filtro', 'Derivado', 'funcional', 0.45, '', 'baja')

# ============================================================
# HASHTAGS ADICIONALES
# ============================================================
add(1, '#dinerorapido', '#dinerorapido, #ganadinerofacil, #dinerofacilya', 'reclutamiento', 'Derivado', 'hashtag', 0.55, '', 'baja')
add(1, '#jalebueno', '#buenjale, #hayjalede, #jalebien', 'reclutamiento', 'Derivado', 'hashtag', 0.5, '', 'baja')
add(1, '#sinescuelatambiensegana', '#escuelanoimporta, #sinestudios', 'desvalorización_educación', 'Derivado', 'hashtag', 0.45, '', 'baja')
add(1, '#mipadrinovip', '#padrinoclub, #quieropadrino', 'aspiracional', 'Derivado', 'hashtag', 0.4, '', 'baja')
add(1, '#cjng2025', '#cjng, #4l2025, #jalisco2025', 'identidad_cartel', 'Derivado', 'hashtag', 0.6, '', 'baja')
add(1, '#chapitos2025', '#chapiza2025, #sinaloa2025, #cdsmx', 'identidad_cartel', 'Derivado', 'hashtag', 0.6, '', 'baja')

# ============================================================
# PATRONES DE VULNERABILIDAD ESPECÍFICA
# ============================================================
add(1, 'si eres migrante te puedo ayudar', 'ayuda para migrantes, trabajo para migrantes', 'captación_migrantes', 'Derivado', 'económica', 0.7, '', 'media')
add(1, 'ayuda para personas deportadas', 'si te deportaron hay trabajo, empleo para deportados', 'captación_migrantes', 'Derivado', 'económica', 0.65, '', 'baja')
add(1, 'si tienes problemas legales yo te ayudo', 'sin antecedentes, aunque tengas problemas, no importa tu situación legal', 'captación_vulnerables', 'Derivado', 'económica', 0.6, '', 'baja')
add(1, 'si te corrieron de tu casa ven conmigo', 'sin casa, te doy techo, si no tienes donde quedarte', 'captación_vulnerables', 'Derivado', 'económica', 0.7, '', 'media')
add(2, 'te doy un lugar donde vivir', 'te doy cuarto, tienes donde quedarte, casa gratis', 'enganche_vivienda', 'Derivado', 'económica', 0.7, '', 'media')

# ============================================================
# SEXTORSIÓN VARIANTES ADICIONALES
# ============================================================
add(3, 'ya hice un perfil falso tuyo con tus fotos', 'perfil fake tuyo, cuenta falsa con tus fotos', 'amenaza_suplantación', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'tus compañeros de escuela van a ver todo', 'lo va a ver toda tu escuela, tus amigos lo van a saber', 'amenaza_social', 'Derivado', 'coercion', 0.9, '', 'media')
add(3, 'ya mandé tu foto a un grupo de tu colonia', 'la mandé a tu barrio, tu colonia ya sabe', 'amenaza_comunitaria', 'Derivado', 'coercion', 0.9, '', 'media')

# ============================================================
# PATRONES DE MANIPULACIÓN TEMPORAL
# ============================================================
add(2, 'es solo por esta vez después no te pido nada', 'solo una vez, no vuelve a pasar, última vez', 'minimización', 'Derivado', 'emocional', 0.7, '', 'media')
add(2, 'si me ayudas hoy mañana te pago el doble', 'hoy me ayudas mañana te compenso, es temporal', 'enganche_temporal', 'Derivado', 'económica', 0.65, '', 'baja')
add(2, 'necesito un favor muy rápido', 'solo toma un minuto, es algo rápido y fácil', 'complicidad_gradual', 'Derivado', 'funcional', 0.6, '', 'baja')

# ============================================================
# CÓDIGOS DE DROGA ADICIONALES
# ============================================================
add(4, 'nieve', 'nieve, blanca, polvo blanco (cocaína)', 'código_droga', 'Derivado', 'operativo', 0.55, '', 'baja')
add(4, 'cristal', 'cristal, vidrio, hielo (metanfetamina)', 'código_droga', 'Derivado', 'operativo', 0.6, '', 'media')
add(4, 'piedra', 'piedra, roca, crack', 'código_droga', 'Derivado', 'operativo', 0.55, '', 'baja')
add(4, 'pase', 'pase, línea, raya (dosis cocaína)', 'código_droga', 'Derivado', 'operativo', 0.5, '', 'baja')
add(4, 'cuerno de chivo', 'cuerno, AK-47, fierro grande', 'código_arma', 'Derivado', 'operativo', 0.65, '', 'media')
add(4, 'corta', 'corta, escuadra, pistola chica', 'código_arma', 'Derivado', 'operativo', 0.6, '', 'media')
add(4, 'lanzagranadas', 'tubo, bazuca, lanza (RPG)', 'código_arma', 'Derivado', 'operativo', 0.65, '', 'media')
add(4, 'monstruo', 'monstruo, tanque, vehículo blindado artesanal', 'código_vehículo', 'Derivado', 'operativo', 0.6, '', 'media')

# ============================================================
# CONTROL DIGITAL ADICIONAL
# ============================================================
add(3, 'préstame tu celular un momento', 'dame tu cel, checo algo en tu teléfono', 'control_dispositivo', 'Derivado', 'coercion', 0.7, '', 'media')
add(3, 'instalé una app de rastreo en tu teléfono', 'te estoy rastreando, GPS en tu cel', 'vigilancia_tech', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'dame tus contraseñas para protegerte', 'dame tu password, necesito acceso a tu cuenta', 'control_digital', 'Derivado', 'coercion', 0.8, '', 'media')

# ============================================================
# PATRONES DE RECLUTAMIENTO EN CENTROS JUVENILES
# ============================================================
add(1, 'te busco a la salida de la escuela', 'te espero a la salida, paso por ti al plantel', 'reclutamiento_escolar', 'Derivado', 'funcional', 0.7, '', 'media')
add(1, 'los miércoles hay reunión para los nuevos', 'reunión de nuevos, junta de interesados, nos vemos el miércoles', 'reclutamiento_organizado', 'Derivado', 'funcional', 0.6, '', 'baja')
add(2, 'ya te tenemos un lugar en el equipo', 'tu lugar está listo, ya tienes puesto, reservamos tu lugar', 'presión', 'Derivado', 'funcional', 0.65, '', 'baja')

# ============================================================
# DERIVADOS FINALES PARA LLEGAR A META
# ============================================================

# Más emojis
add(1, '\U0001f48e diamante emoji', '\U0001f48e joya, gema, riqueza, lujo emoji', 'aspiracional', 'Derivado', 'simbólica', 0.4, '', 'baja')
add(4, '\U0001f4a3 bomba emoji', '\U0001f4a3 explosión, bomba, peligro emoji', 'amenaza', 'Derivado', 'simbólica', 0.6, '', 'baja')
add(4, '\u26d3\ufe0f cadena emoji', '\u26d3\ufe0f cadenas, atrapado, no te sueltan', 'retención', 'Derivado', 'simbólica', 0.55, '', 'baja')

# Más patrones operativos
add(4, 'prende el radio frecuencia 5', 'sintoniza el radio, canal 5, frecuencia de trabajo', 'código_comunicación', 'Derivado', 'operativo', 0.6, '', 'baja')
add(4, 'cambia de SIM cada 3 días', 'rota SIM, cambia de chip, número nuevo', 'evasión', 'Derivado', 'operativo', 0.65, '', 'baja')
add(4, 'usa el carro sin placas', 'sin placas, quita las placas, vehículo limpio', 'evasión', 'Derivado', 'operativo', 0.7, '', 'media')
add(4, 'el pago es en dólares', 'en verde, en billetes verdes, pago en USD', 'operativo', 'Derivado', 'operativo', 0.6, '', 'baja')

# Más captación
add(1, 'aquí respetamos y nos respetan', 'hay respeto mutuo, aquí hay honor, código de honor', 'lealtad', 'Derivado', 'sociocultural', 0.5, '', 'baja')
add(1, 'somos una familia aquí', 'somos familia, hermandad, aquí eres hermano', 'pertenencia', 'Derivado', 'sociocultural', 0.55, '', 'baja')
add(1, 'te damos arma y carro para que defiendas tu zona', 'arma propia, carro propio, tú mandas en tu zona', 'incentivo_material', 'Derivado', 'económica', 0.7, '', 'baja')
add(1, 'con nosotros nadie te molesta', 'protección, nadie te toca, estás protegido', 'incentivo_protección', 'Derivado', 'sociocultural', 0.6, '', 'baja')

# Más enganche
add(2, 'ven al evento todos van a estar', 'van los compas, va mucha gente, no faltes', 'presión_social', 'Derivado', 'emocional', 0.55, '', 'baja')
add(2, 'te enseño a disparar', 'aprendes a usar armas, te entreno, práctica de tiro', 'escalamiento', 'Derivado', 'funcional', 0.75, '', 'media')
add(2, 'primero vas a hacer algo fácil', 'algo sencillo para empezar, trabajo fácil al inicio', 'complicidad_gradual', 'Derivado', 'funcional', 0.7, '', 'media')

# Más coerción
add(3, 'ya le debemos al jefe de plaza', 'deuda con el jefe, el comandante cobra, la plaza quiere su parte', 'presión_deuda', 'Derivado', 'coercion', 0.8, '', 'media')
add(3, 'si te agarran no digas nada', 'si caes calla, no abras la boca, no sueltes nada', 'código_silencio', 'Derivado', 'coercion', 0.85, '', 'media')
add(3, 'el abogado te saca pero cuestas', 'te conseguimos abogado, te sacamos pero pagas', 'retención_deuda', 'Derivado', 'coercion', 0.75, '', 'media')

# Más explotación
add(4, 'abre una cuenta de banco con este nombre', 'cuenta prestanombres, abre cuenta, necesitamos cuentas', 'lavado_dinero', 'Derivado', 'operativo', 0.75, '', 'media')
add(4, 'sube estos videos a TikTok', 'publica esto, sube el video, postea en tu cuenta', 'propaganda', 'Derivado', 'operativo', 0.6, '', 'baja')
add(4, 'maneja esta página de Facebook', 'administra esta página, postea las ofertas, maneja la cuenta', 'reclutamiento_digital', 'Derivado', 'operativo', 0.65, '', 'media')

print(f'\n=== BATCH 4 COMPLETE ===')
print(f'Added: {added}')
print(f'Skipped (duplicates): {skipped}')
total_all = data['total_added'] + added
for fase in [1,2,3,4]:
    start_count = {1: 101, 2: 91, 3: 85, 4: 101}
    total_for_phase = counters[fase] - start_count[fase]
    print(f'  Fase {fase}: {total_for_phase} total new (all batches)')
print(f'Total combined: {374 + total_all}')
print(f'Remaining to 1000: {1000 - 374 - total_all}')

with open('batch4_counters.json', 'w') as f:
    json.dump({'counters': counters, 'added_batch4': added, 'total_added': total_all}, f)
