"""One-shot script: add self-feed audit patterns to the 4 phase JSONs.

These patterns close gaps surfaced by the TRACK 1 self-feeding dataset
audit on Apr 25 2026, validated against POST /analyze (use_llm=false)
on the public endpoint. Every phrase in this file was tested and
returned risk_level=SEGURO — i.e. these are confirmed FALSE NEGATIVES
that the heuristic missed.

Sources cited per pattern (Mexican press 2024-2026): Infobae, Tercera Vía,
Proceso, El Universal, Excélsior, Telediario, La Jornada / LJA, Lisa News,
Adn40, Colmex study on TikTok narco-recruitment.

Run once. Idempotent (skips patterns already present by exact match).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KW = ROOT / "backend" / "classifier" / "keywords"

# (pattern_lower_no_diacritics, weight, category, explanation, source_origin)
# Sources are short-domain identifiers used in _source_origin.

# ============ PHASE 1 — Captación / Ofertas / Glorificación ============
PHASE1_NEW = [
    ("trabajo para la mana", 0.9, "cartel_jerga", "consigna TikTok narco para reclutar (Infobae 2025-04-18)", "infobae.com"),
    ("hay jale para la mana", 0.9, "cartel_jerga", "consigna jerga: maña=cartel, jale=trabajo criminal", "infobae.com"),
    ("se solicita gente para las 4 letras", 0.95, "cartel_jerga", "4 letras = CJNG, llamado directo a reclutamiento", "proceso.com.mx"),
    ("se recluta gente para las 4letras", 0.95, "cartel_jerga", "4letras = CJNG, llamado directo (Proceso 2025-04-22)", "proceso.com.mx"),
    ("manden mensaje si quieren superarse", 0.65, "oferta_vaga", "frase reclutamiento TikTok narco (Proceso 2025-04-22)", "proceso.com.mx"),
    ("buena paga semanal hospedaje y comida", 0.85, "oferta_economica", "paquete típico oferta narco", "proceso.com.mx"),
    ("vacaciones equipo tactico calzado y ropa", 0.9, "cartel_oferta", "menciona equipo táctico = oferta sicariato", "proceso.com.mx"),
    ("quien se anima al jale", 0.7, "oferta_vaga", "convocatoria al jale (jerga MX)", "infobae.com"),
    ("la empresa cuida a los suyos", 0.85, "cartel_jerga", "consigna captación: empresa=cartel", "infobae.com"),
    ("la firma cuida a los suyos", 0.85, "cartel_jerga", "consigna captación: firma=cartel", "infobae.com"),
    ("aqui se gana bien y rapido", 0.65, "oferta_vaga", "anzuelo dinero rápido", "lisanews.org"),
    ("entrenamiento pagado garantizado", 0.6, "oferta_vaga", "promesa típica reclutamiento narco", "terceravia.mx"),
    ("te doy 6 mil a la semana", 0.85, "oferta_economica", "oferta semanal jóvenes (Proceso 2026-04-17)", "proceso.com.mx"),
    ("te pago 8 mil semanal sin experiencia", 0.9, "oferta_economica", "oferta sin experiencia, alta señal", "proceso.com.mx"),
    ("ofrezco 20 mil pesos a la semana", 0.9, "oferta_economica", "monto reportado en operativos Jalisco 2026", "proceso.com.mx"),
    ("te ofrezco 5 mil semanal", 0.85, "oferta_economica", "oferta semanal explícita", "proceso.com.mx"),
    ("paga semanal asegurado", 0.55, "oferta_economica", "patrón anuncio dinero rápido", "lisanews.org"),
    ("paga diaria al cierre del turno", 0.55, "oferta_economica", "patrón paga diaria sospechoso", "lisanews.org"),
    ("solo para puros belicones", 0.7, "narcocultura", "belicones = jerga narcocultura", "infobae.com"),
    ("puros plebes belicos", 0.7, "narcocultura", "plebes belicos = identidad narcocultura juvenil", "infobae.com"),
    ("plebes con actitud", 0.55, "narcocultura", "registro narco juvenil", "infobae.com"),
    ("aqui no se anda jugando plebe", 0.65, "narcocultura", "registro narco intimidación inicial", "infobae.com"),
    ("ondeado y al tiro", 0.7, "narcocultura", "jerga de disposición violenta", "infobae.com"),
    ("se buscan plebes con huevos", 0.7, "narcocultura", "convocatoria masculinidad violenta", "infobae.com"),
    ("aqui se trabaja para el senor", 0.85, "cartel_jerga", "el señor = capo (Mencho/Chapo)", "infobae.com"),
    ("trabajamos para el senor de los gallos", 0.95, "cartel_jerga", "senor de los gallos = Mencho (CJNG)", "proceso.com.mx"),
    ("trabajo para el m", 0.85, "cartel_jerga", "M = Mayo Zambada/CDS reference", "infobae.com"),
    ("te quieres unir a la mana", 0.95, "cartel_jerga", "mana=cartel, invitación directa", "infobae.com"),
    ("entrale a la mana", 0.95, "cartel_jerga", "imperativo unión cartel", "infobae.com"),
    ("le entras o no le entras al jale", 0.9, "cartel_jerga", "presión binaria al jale (criminal)", "infobae.com"),
    ("se solicitan vigilantes 24 horas", 0.65, "fronts_falsos", "vigilante 24h = front halcón", "infobae.com"),
    ("se buscan cocineros para rancho", 0.85, "cartel_jerga", "cocinero = operador laboratorio droga", "infobae.com"),
    ("cocineros para laboratorio", 0.95, "cartel_jerga", "laboratorio droga = operativa narco", "infobae.com"),
    ("se buscan halconeros", 0.95, "cartel_jerga", "halconero = vigilante cartel", "infobae.com"),
    ("se solicitan punteros", 0.9, "cartel_jerga", "puntero = vigilante cartel", "infobae.com"),
    ("buscamos morros sin vicios", 0.7, "perfilamiento", "perfilamiento menores sin antecedentes", "lja.mx"),
    ("morros que no le saquen", 0.75, "narcocultura", "perfil joven dispuesto a violencia", "lja.mx"),
    ("plebe que no raje", 0.75, "narcocultura", "rajar = soplar; perfil leal narco", "infobae.com"),
    ("checa mi bio para info del jale", 0.85, "red_social_bio", "redirigir a bio de cuenta reclutadora", "terceravia.mx"),
    ("dm para entrarle", 0.85, "red_social_dm", "anzuelo dm para reclutar", "terceravia.mx"),
    ("escribeme al privado de tiktok", 0.8, "red_social_dm", "cambio a canal privado TikTok", "terceravia.mx"),
    ("info por inbox", 0.55, "red_social_dm", "anzuelo info por inbox", "terceravia.mx"),
    ("dejen su numero les marco", 0.65, "red_social_dm", "exige PII para contactar", "lisanews.org"),
    ("modelos webcam bien pagado", 0.85, "fronts_falsos", "front trata digital", "eluniversal.com.mx"),
    ("se buscan edecanes para evento privado", 0.85, "fronts_falsos", "edecán evento privado = front trata", "eluniversal.com.mx"),
    ("damas de compania bien pagado", 0.95, "fronts_falsos", "explotación sexual vía oferta", "eluniversal.com.mx"),
    ("acompanantes vip a domicilio", 0.9, "fronts_falsos", "explotación sexual a domicilio", "eluniversal.com.mx"),
    ("masajistas sin experiencia", 0.75, "fronts_falsos", "front comun explotación sexual", "eluniversal.com.mx"),
    ("modelos para contenido adulto", 0.9, "fronts_falsos", "captación CSAM/porn sin consentimiento", "eluniversal.com.mx"),
    ("chicas para fiestas privadas", 0.9, "fronts_falsos", "front trata fiestas privadas", "eluniversal.com.mx"),
    ("trae tu acta de nacimiento y vente", 0.7, "fronts_falsos", "documentos para captación menor", "eluniversal.com.mx"),
]

# ============ PHASE 2 — Enganche / Aislamiento / PII ============
PHASE2_NEW = [
    ("dame tus datos y te resuelvo", 0.7, "perfilamiento", "anzuelo PII a cambio de promesa", "lisanews.org"),
    ("mandame foto de tu credencial", 0.9, "perfilamiento", "exige documento oficial", "eluniversal.com.mx"),
    ("mandame foto de tu ine", 0.9, "perfilamiento", "exige INE = robo identidad/explotación", "eluniversal.com.mx"),
    ("foto de tu identificacion porfa", 0.85, "perfilamiento", "exige identificación", "eluniversal.com.mx"),
    ("dime tu curp", 0.85, "perfilamiento", "exige CURP = robo identidad", "eluniversal.com.mx"),
    ("a que prepa vas", 0.75, "perfilamiento", "mapeo escuela menor", "lja.mx"),
    ("en que secu vas", 0.75, "perfilamiento", "mapeo escuela secundaria", "lja.mx"),
    ("en que turno entras a la escuela", 0.8, "perfilamiento", "patrones horarios menor", "lja.mx"),
    ("a que hora sales de la escuela", 0.8, "perfilamiento", "horarios para interceptación", "lja.mx"),
    ("a que hora estan solos en tu casa", 0.95, "perfilamiento", "ventana sin supervisión adulta", "lja.mx"),
    ("cuando salen tus papas de viaje", 0.9, "perfilamiento", "ventana sin supervisión", "lja.mx"),
    ("mandame tu cuenta para depositar", 0.85, "perfilamiento", "PII bancaria para mula/extorsión", "lisanews.org"),
    ("mandame tu clabe", 0.7, "perfilamiento", "PII bancaria CLABE", "lisanews.org"),
    ("dame tu numero de tarjeta", 0.85, "perfilamiento", "PII tarjeta = fraude/extorsión", "lisanews.org"),
    ("descarga signal y me hablas", 0.85, "aislamiento_canal", "Signal = canal cifrado fuera de moderación", "lja.mx"),
    ("descarga telegram para hablar tranquilos", 0.85, "aislamiento_canal", "Telegram = aislamiento de moderación", "lja.mx"),
    ("vamonos a wickr", 0.85, "aislamiento_canal", "Wickr = canal cifrado efímero", "lja.mx"),
    ("borra esta conversacion", 0.85, "secrecia", "petición destrucción evidencia", "lisanews.org"),
    ("borra el chat cada noche", 0.9, "secrecia", "rutina destrucción evidencia", "lisanews.org"),
    ("activa mensajes que se autodestruyen", 0.9, "secrecia", "mensajes efímeros para evitar evidencia", "lisanews.org"),
    ("esto queda entre tu y yo", 0.85, "secrecia", "pacto secreto clásico grooming", "eluniversal.com.mx"),
    ("nadie tiene que saber de esto", 0.85, "secrecia", "pacto secreto grooming", "eluniversal.com.mx"),
    ("no le digas a tu mama de mi", 0.95, "secrecia", "secrecia ante figura parental", "eluniversal.com.mx"),
    ("ni a tu mejor amiga le cuentes", 0.85, "secrecia", "aislamiento social grooming", "eluniversal.com.mx"),
    ("eres mi secretito favorito", 0.85, "grooming_emocional", "diminutivo posesivo grooming", "eluniversal.com.mx"),
    ("ya somos novios virtuales", 0.7, "grooming_emocional", "novio virtual = grooming", "eluniversal.com.mx"),
    ("nadie te entiende como yo", 0.7, "grooming_emocional", "aislamiento emocional clásico", "eluniversal.com.mx"),
    ("solo yo te quiero de verdad", 0.75, "grooming_emocional", "vínculo exclusivo grooming", "eluniversal.com.mx"),
    ("ya soy tu mejor amigo virtual", 0.65, "grooming_emocional", "rol autoasignado grooming", "eluniversal.com.mx"),
    ("te paso 200 robux ahora", 0.85, "roblox_grooming", "regalo virtual a cambio de favor", "infobae.com"),
    ("te mando robux gratis", 0.8, "roblox_grooming", "anzuelo robux", "infobae.com"),
    ("te regalo vbucks de fortnite", 0.8, "gaming_grooming", "regalo virtual gaming", "infobae.com"),
    ("te mando un nitro de discord", 0.75, "gaming_grooming", "Nitro Discord como cebo", "infobae.com"),
    ("te paso skins si me agregas", 0.8, "gaming_grooming", "intercambio digital por contacto", "infobae.com"),
    ("vente a mi server privado de discord", 0.85, "aislamiento_canal", "server privado Discord = aislamiento", "infobae.com"),
    ("vamonos a un grupo cerrado", 0.7, "aislamiento_canal", "grupo cerrado = sin moderación", "infobae.com"),
    ("tengo un grupo solo de plebes como tu", 0.85, "aislamiento_canal", "grupo segregado por edad/perfil", "infobae.com"),
    ("nos vemos en el lobby privado", 0.7, "aislamiento_canal", "lobby gaming privado", "infobae.com"),
    ("te invito al chat secreto", 0.85, "aislamiento_canal", "chat secreto = grooming", "infobae.com"),
    ("hablemos por videollamada sin tu mama", 0.95, "aislamiento_canal", "videollamada sin supervisión = grooming", "infobae.com"),
    ("vamos a una vc tu y yo", 0.7, "aislamiento_canal", "vc=videocall, intimidad forzada", "infobae.com"),
    ("primero confianza luego negocio", 0.6, "grooming_emocional", "construcción de confianza táctica", "lisanews.org"),
    ("yo te cuido mejor que tu familia", 0.85, "grooming_emocional", "desplazamiento figura parental", "lisanews.org"),
    ("yo te resuelvo lo que tu casa no", 0.85, "grooming_emocional", "supla a familia = grooming", "lisanews.org"),
]

# ============ PHASE 3 — Coerción / Sextorsión / Amenaza ============
PHASE3_NEW = [
    ("si no me contestas rapido publico tus fotos", 0.95, "sextorsion_amenaza", "amenaza divulgacion por silencio", "excelsior.com.mx"),
    ("si me ignoras subo todo", 0.95, "sextorsion_amenaza", "amenaza por silencio", "excelsior.com.mx"),
    ("voy a publicar en internet y a tus contactos", 0.95, "sextorsion_amenaza", "amenaza divulgacion masiva", "telediario.mx"),
    ("tengo tus contactos de whatsapp guardados", 0.9, "sextorsion_evidencia", "retención contactos como palanca", "telediario.mx"),
    ("ya tengo a tu mama agregada", 0.95, "sextorsion_familia", "amenaza divulgacion familiar inminente", "telediario.mx"),
    ("ya tengo a tu papa en contactos", 0.95, "sextorsion_familia", "amenaza divulgacion familiar inminente", "telediario.mx"),
    ("ya tengo el numero de tu novio", 0.9, "sextorsion_pareja", "amenaza divulgacion pareja", "telediario.mx"),
    ("le voy a decir a tu novio lo que haces", 0.9, "sextorsion_pareja", "amenaza divulgacion pareja", "telediario.mx"),
    ("agenda una cita con el jefe de plaza", 0.95, "amenaza_directa", "cita jefe plaza = coerción cartel", "telediario.mx"),
    ("o pones a un amigo o subo todo", 0.95, "sextorsion_reclutamiento", "exigencia substitución víctima", "telediario.mx"),
    ("pon a tu primo o tu hermano", 0.95, "sextorsion_reclutamiento", "exigencia substitución víctima familiar", "telediario.mx"),
    ("o me mandas otra foto o subo las que tengo", 0.95, "sextorsion_amenaza", "chantaje continuidad CSAM", "excelsior.com.mx"),
    ("o me mandas mas o se las paso a todos", 0.95, "sextorsion_amenaza", "chantaje continuidad CSAM masivo", "excelsior.com.mx"),
    ("te voy a quemar en internet", 0.9, "sextorsion_amenaza", "quemar = exhibir, amenaza divulgacion", "excelsior.com.mx"),
    ("te quemo en redes", 0.85, "sextorsion_amenaza", "quemar = exhibir, jerga MX", "excelsior.com.mx"),
    ("te exhibo en tiktok", 0.9, "sextorsion_amenaza", "amenaza divulgacion plataforma masiva", "excelsior.com.mx"),
    ("te exhibo en instagram", 0.9, "sextorsion_amenaza", "amenaza divulgacion plataforma masiva", "excelsior.com.mx"),
    ("te subo a paginas para adultos", 0.95, "sextorsion_publicacion", "amenaza distribución porno", "excelsior.com.mx"),
    ("te van a conocer en toda tu escuela", 0.95, "sextorsion_escuela", "amenaza divulgacion escolar", "excelsior.com.mx"),
    ("le mando el video al grupo de tu salon", 0.95, "sextorsion_escuela", "amenaza divulgacion grupo escolar", "excelsior.com.mx"),
    ("hago un deepfake con tu cara", 0.95, "sextorsion_ia", "amenaza CSAM sintético IA", "adn40.mx"),
    ("te hago un desnudo con ia", 0.95, "sextorsion_ia", "amenaza desnudo sintético IA", "adn40.mx"),
    ("ya tengo tu cara puesta en otro cuerpo", 0.95, "sextorsion_ia", "deepfake en uso, coerción IA", "adn40.mx"),
    ("uso ia para hacer tus nudes", 0.95, "sextorsion_ia", "anuncio creación CSAM con IA", "adn40.mx"),
    ("ya estas dentro no te puedes salir", 0.95, "coercion_no_salida", "imposibilidad salida cartel", "lisanews.org"),
    ("ya entraste y aqui no hay vuelta atras", 0.95, "coercion_no_salida", "imposibilidad salida cartel", "lisanews.org"),
    ("la firma no perdona traidores", 0.95, "amenaza_silencio", "amenaza traición=muerte", "lisanews.org"),
    ("aqui no hay renuncias", 0.9, "coercion_no_salida", "imposibilidad salida criminal", "lisanews.org"),
    ("si rajas te cae el comando", 0.95, "amenaza_directa", "rajar=delatar, comando=ataque armado", "lisanews.org"),
    ("te mando levantar si abres la boca", 0.95, "amenaza_directa", "amenaza levantón por delación", "lisanews.org"),
    ("te mando levantar a tu casa", 0.95, "amenaza_directa", "amenaza levantón en domicilio", "lisanews.org"),
    ("ya ubicamos a tu familia", 0.95, "coercion_familia", "vigilancia familiar activa", "lisanews.org"),
    ("sabemos donde estudia tu hermano", 0.95, "coercion_familia", "vigilancia familiar escolar", "lisanews.org"),
    ("sabemos donde trabaja tu mama", 0.95, "coercion_familia", "vigilancia laboral familiar", "lisanews.org"),
    ("te tenemos en la mira plebe", 0.95, "amenaza_directa", "vigilancia activa con jerga belica", "lisanews.org"),
    ("ya estas marcado plebe", 0.9, "amenaza_directa", "marcado=sentenciado, jerga MX", "lisanews.org"),
    ("o entras o te vas con todo y familia", 0.95, "coercion_familia", "amenaza colectiva familiar", "lisanews.org"),
    ("hablale al jefe ya o te jodes", 0.9, "amenaza_directa", "ultimátum jefe", "lisanews.org"),
    ("te mando una visita a la casa", 0.9, "amenaza_directa", "visita=ataque armado domicilio", "lisanews.org"),
    ("vas a aparecer en una bolsa", 0.95, "amenaza_muerte", "amenaza muerte explícita MX", "lisanews.org"),
    ("te vamos a desaparecer", 0.95, "amenaza_muerte", "amenaza desaparición forzada", "lisanews.org"),
]

# ============ PHASE 4 — Explotación / Operativa ============
PHASE4_NEW = [
    ("ve al punto a las 5", 0.85, "operativa_punto", "punto=puesto vigilancia/venta", "lja.mx"),
    ("vente al punto sin falta", 0.85, "operativa_punto", "orden presencia en puesto narco", "lja.mx"),
    ("checate el punto cada hora", 0.9, "operativa_punto", "rutina vigilancia narco", "lja.mx"),
    ("reportate al punto", 0.85, "operativa_punto", "reporte a puesto narco", "lja.mx"),
    ("te toca turno de halcon esta noche", 0.95, "operativa_halcon", "turno vigilancia narco menor", "lja.mx"),
    ("avisa cuando pase la patrulla", 0.95, "operativa_halcon", "función halcón clásica", "lja.mx"),
    ("avisa si ves verdes", 0.95, "operativa_halcon", "verdes=militares/GN, jerga halcón", "lja.mx"),
    ("avisa si ves militares", 0.95, "operativa_halcon", "función halcón vs fuerza pública", "lja.mx"),
    ("reportame movimientos raros", 0.9, "operativa_halcon", "reporte vigilancia narco", "lja.mx"),
    ("toma foto de la placa", 0.85, "operativa_halcon", "registro placa para perfilamiento", "lja.mx"),
    ("toma video del que entra a la casa de enfrente", 0.9, "operativa_halcon", "vigilancia domicilio narco", "lja.mx"),
    ("entrega el paquete en el punto", 0.95, "operativa_entrega", "paquete=droga, entrega narco", "lja.mx"),
    ("recoge el paquete en oxxo", 0.85, "operativa_entrega", "punto entrega comercial", "lja.mx"),
    ("entrega el sobre y te pago", 0.9, "operativa_entrega", "entrega contra pago", "lja.mx"),
    ("vas a llevar la merca a la zona", 0.95, "venta_droga", "merca=mercancía=droga", "lja.mx"),
    ("acomoda la merca en bolsitas", 0.95, "venta_droga", "preparación dosis venta", "lja.mx"),
    ("te toca empacar las grapas", 0.95, "venta_droga", "grapa=dosis cocaína", "lja.mx"),
    ("te toca repartir piedra", 0.95, "venta_droga", "piedra=crack/cristal", "lja.mx"),
    ("vendele al cliente del punto", 0.95, "venta_droga", "venta menudeo en punto", "lja.mx"),
    ("cobra 100 por dosis", 0.9, "venta_droga", "tarifa dosis menudeo", "lja.mx"),
    ("cobra el piso al de la tienda", 0.95, "extorsion_op", "cobro piso comerciante", "lja.mx"),
    ("ya cobraste el piso al de la tortilla", 0.95, "extorsion_op", "cobro piso negocio local", "lja.mx"),
    ("le pasas la cuota cada lunes", 0.9, "extorsion_op", "cuota periódica extorsión", "lja.mx"),
    ("le tocas la puerta al moroso", 0.85, "extorsion_op", "intimidación cobro extorsión", "lja.mx"),
    ("dale un susto al que no paga", 0.95, "extorsion_op", "violencia coerción extorsión", "lja.mx"),
    ("manda video amenazando al deudor", 0.95, "extorsion_op", "video amenaza cobro extorsión", "lja.mx"),
    ("graba al cliente sin que sepa", 0.95, "csam_op", "grabación clandestina víctima", "eluniversal.com.mx"),
    ("manda video sin ropa para el cliente", 0.95, "csam_op", "producción CSAM por encargo", "eluniversal.com.mx"),
    ("haz videollamada caliente con el cliente", 0.95, "csam_op", "explotación sexual videollamada", "eluniversal.com.mx"),
    ("atiende al cliente del cuarto 3", 0.95, "trata_op", "asignación cliente trata", "eluniversal.com.mx"),
    ("hoy te toca atender 5 clientes", 0.95, "trata_op", "cuota explotación sexual diaria", "eluniversal.com.mx"),
    ("vas con el cliente al hotel", 0.95, "trata_op", "traslado víctima trata", "eluniversal.com.mx"),
    ("la madrota te dice cuanto cobras", 0.95, "trata_op", "madrota=proxeneta, control tarifa", "eluniversal.com.mx"),
    ("no salgas del cuarto sin permiso", 0.95, "trata_op", "encierro víctima trata", "eluniversal.com.mx"),
    ("entrega la lana de la noche", 0.95, "trata_op", "entrega ganancias proxeneta", "eluniversal.com.mx"),
    ("subete a la troca negra", 0.95, "operativa_traslado", "vehículo identificable, orden traslado", "lja.mx"),
    ("vas a viajar a la frontera ya", 0.95, "operativa_traslado", "traslado urgente frontera", "lja.mx"),
    ("te pago el camion a tijuana ya", 0.95, "operativa_traslado", "traslado urgente plaza fronteriza", "lja.mx"),
    ("nos vemos en la central de autobuses 6 am", 0.85, "operativa_traslado", "punto encuentro traslado", "lja.mx"),
    ("trae el cuerno y los cargadores", 0.95, "operativa_armas", "cuerno=AK-47, jerga MX", "lja.mx"),
    ("trae el fierro al punto", 0.95, "operativa_armas", "fierro=arma de fuego", "lja.mx"),
    ("dale piso al fulano", 0.95, "amenaza_operacion", "dar piso=matar, jerga MX", "lja.mx"),
    ("ya mero levantamos al objetivo", 0.95, "amenaza_operacion", "levantón inminente", "lja.mx"),
    ("hazle el levanton al chamaco", 0.95, "amenaza_operacion", "orden levantón a menor", "lja.mx"),
    ("encarguense del soplon", 0.95, "amenaza_operacion", "orden ejecución delator", "lja.mx"),
    ("no contestes mensajes de tu casa", 0.9, "control_aislamiento", "aislamiento familiar forzado", "lisanews.org"),
    ("apaga el celular cuando te lo diga", 0.85, "control_aislamiento", "control comunicaciones víctima", "lisanews.org"),
    ("dame tu telefono cada noche", 0.85, "control_aislamiento", "confiscación periódica celular", "lisanews.org"),
    ("aqui mando yo y obedeces", 0.85, "control_aislamiento", "afirmación dominio explotador", "lisanews.org"),
]


def patch(phase_num, fname, new_patterns):
    path = KW / fname
    data = json.loads(path.read_text(encoding="utf-8"))
    patterns = data["patterns"]
    existing = {p["pattern"].lower() for p in patterns}
    next_id = max(int(p["id"].split("_")[1]) for p in patterns) + 1
    added = 0
    for entry in new_patterns:
        pat, weight, cat, expl, source_origin = entry
        if pat.lower() in existing:
            continue
        patterns.append({
            "id": f"f{phase_num}_{next_id:03d}",
            "pattern": pat,
            "weight": weight,
            "regex": False,
            "category": cat,
            "explanation": expl,
            "source": "selffeed_2026_04_25",
            "type": "selffeed_audit",
            "signal_base": weight,
            "confidence": "alta",
            "_source_origin": source_origin,
        })
        next_id += 1
        added += 1
    data["patterns"] = patterns
    data["total_patterns"] = len(patterns)
    data["last_updated"] = "2026-04-25"
    data["updated_at"] = "2026-04-25T18:00:00Z"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return added, len(patterns)


if __name__ == "__main__":
    a1, t1 = patch(1, "phase1_captacion.json", PHASE1_NEW)
    a2, t2 = patch(2, "phase2_enganche.json", PHASE2_NEW)
    a3, t3 = patch(3, "phase3_coercion.json", PHASE3_NEW)
    a4, t4 = patch(4, "phase4_explotacion.json", PHASE4_NEW)
    print(f"Phase1: +{a1} (total {t1})")
    print(f"Phase2: +{a2} (total {t2})")
    print(f"Phase3: +{a3} (total {t3})")
    print(f"Phase4: +{a4} (total {t4})")
    print(f"GRAND: +{a1 + a2 + a3 + a4}")
