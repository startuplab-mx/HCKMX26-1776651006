"""TRACK 1 self-feed harness — tests candidate phrases against /analyze (use_llm=false).

Reads CANDIDATES (phrase, source_url, expected_phase, suggested_category, suggested_weight),
hits POST http://159.223.187.6/analyze, captures risk_level + risk_score + categories,
and writes:
  - dataset_self_feed_results.csv
  - _selffeed_neg.json  (the "FALSE NEGATIVE" rows for the patcher script)

Rate limit: ~12 POSTs/min (one every 5s, well under 15/min cap).
"""
import csv
import json
import time
import unicodedata
import urllib.request
import urllib.error
from pathlib import Path

API = "http://159.223.187.6/analyze"
ROOT = Path(__file__).resolve().parent.parent
OUT_CSV = ROOT / "scripts" / "dataset_self_feed_results.csv"
OUT_NEG = ROOT / "scripts" / "_selffeed_neg.json"


def strip_diacritics(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


# (phrase, source_url, expected_phase 1-4, suggested_category, suggested_weight)
# Phrases curated from real reporting (Infobae, Tercera Vía, Proceso, El Universal,
# Telediario, Excélsior, La Jornada, REDIM, Colmex, Consejo Ciudadano), plus
# operative jerga reported by Mexican press 2024-2026 about TikTok/IG/Discord/Roblox
# narco recruitment and sextortion of minors.
CANDIDATES = [
    # ============ PHASE 1 — Captación / Ofertas / Glorificación ============
    # Direct cartel hashtag/slogan style (textified)
    ("trabajo para la mana", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.9),
    ("hay jale para la mana", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.9),
    ("se solicita gente para las 4 letras", "https://www.proceso.com.mx/nacional/2025/4/22/", 1, "cartel_jerga", 0.95),
    ("se recluta gente para las 4letras", "https://www.proceso.com.mx/nacional/2025/4/22/", 1, "cartel_jerga", 0.95),
    ("manden mensaje si quieren superarse", "https://www.proceso.com.mx/nacional/2025/4/22/", 1, "oferta_vaga", 0.65),
    ("buena paga semanal hospedaje y comida", "https://www.proceso.com.mx/nacional/2025/4/22/", 1, "oferta_economica", 0.85),
    ("vacaciones equipo tactico calzado y ropa", "https://www.proceso.com.mx/nacional/2025/4/22/", 1, "cartel_oferta", 0.9),
    ("quien se anima al jale", "https://www.infobae.com/mexico/2025/04/18/", 1, "oferta_vaga", 0.7),
    ("la empresa cuida a los suyos", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.85),
    ("la firma cuida a los suyos", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.85),
    ("aqui se gana bien y rapido", "https://www.lisanews.org/", 1, "oferta_vaga", 0.65),
    ("apoyamos a madres solteras y estudiantes", "https://terceravia.mx/2025/04/", 1, "oferta_vaga", 0.55),
    ("apoyo economico para estudiantes", "https://terceravia.mx/2025/04/", 1, "oferta_vaga", 0.5),
    ("entrenamiento pagado garantizado", "https://terceravia.mx/2025/04/", 1, "oferta_vaga", 0.6),
    ("te doy 6 mil a la semana", "https://www.proceso.com.mx/nacional/2026/4/17/", 1, "oferta_economica", 0.85),
    ("te pago 8 mil semanal sin experiencia", "https://www.proceso.com.mx/nacional/2026/4/17/", 1, "oferta_economica", 0.9),
    ("ofrezco 20 mil pesos a la semana", "https://www.proceso.com.mx/nacional/2026/4/17/", 1, "oferta_economica", 0.9),
    ("te ofrezco 5 mil semanal", "https://www.proceso.com.mx/nacional/2026/4/17/", 1, "oferta_economica", 0.85),
    ("pago semanal asegurado", "https://www.lisanews.org/", 1, "oferta_economica", 0.55),
    ("paga diaria al cierre del turno", "https://www.lisanews.org/", 1, "oferta_economica", 0.55),
    # narcocultura / belica register
    ("solo para puros belicones", "https://www.infobae.com/mexico/2025/04/18/", 1, "narcocultura", 0.7),
    ("puros plebes belicos", "https://www.infobae.com/mexico/2025/04/18/", 1, "narcocultura", 0.7),
    ("plebes con actitud", "https://www.infobae.com/mexico/2025/04/18/", 1, "narcocultura", 0.55),
    ("aqui no se anda jugando plebe", "https://www.infobae.com/mexico/2025/04/18/", 1, "narcocultura", 0.65),
    ("ondeado y al tiro", "https://www.infobae.com/mexico/2025/04/18/", 1, "narcocultura", 0.7),
    ("se buscan plebes con huevos", "https://www.infobae.com/mexico/2025/04/18/", 1, "narcocultura", 0.7),
    ("compa bienvenido al equipo", "https://terceravia.mx/2025/04/", 1, "cartel_jerga", 0.6),
    ("aqui se trabaja para el senor", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.85),
    ("trabajamos para el senor de los gallos", "https://www.proceso.com.mx/nacional/2025/4/22/", 1, "cartel_jerga", 0.95),
    ("trabajo para el m", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.85),
    ("te quieres unir a la maña", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.95),
    ("entrale a la mana", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.95),
    ("le entras o no le entras al jale", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.9),
    # roles
    ("se solicitan choferes con licencia", "https://www.infobae.com/mexico/2025/04/18/", 1, "fronts_falsos", 0.6),
    ("se solicitan vigilantes 24 horas", "https://www.infobae.com/mexico/2025/04/18/", 1, "fronts_falsos", 0.65),
    ("se buscan cocineros para rancho", "https://www.infobae.com/mexico/2025/04/18/", 1, "fronts_falsos", 0.85),
    ("cocineros para laboratorio", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.95),
    ("se buscan halconeros", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.95),
    ("se solicitan punteros", "https://www.infobae.com/mexico/2025/04/18/", 1, "cartel_jerga", 0.9),
    ("buscamos morros sin vicios", "https://www.lja.mx/2025/04/", 1, "perfilamiento", 0.7),
    ("morros que no le saquen", "https://www.lja.mx/2025/04/", 1, "narcocultura", 0.75),
    ("plebe que no raje", "https://www.infobae.com/mexico/2025/04/18/", 1, "narcocultura", 0.75),
    # platform contact
    ("checa mi bio para info del jale", "https://terceravia.mx/2025/04/", 1, "red_social_bio", 0.85),
    ("dm para entrarle", "https://terceravia.mx/2025/04/", 1, "red_social_dm", 0.85),
    ("escribeme al privado de tiktok", "https://terceravia.mx/2025/04/", 1, "red_social_dm", 0.8),
    ("info por inbox", "https://terceravia.mx/2025/04/", 1, "red_social_dm", 0.55),
    ("dejen su numero les marco", "https://www.lisanews.org/", 1, "red_social_dm", 0.65),
    # Trafficking fronts
    ("modelos webcam bien pagado", "https://www.eluniversal.com.mx/", 1, "fronts_falsos", 0.85),
    ("se buscan edecanes para evento privado", "https://www.eluniversal.com.mx/", 1, "fronts_falsos", 0.85),
    ("damas de compania bien pagado", "https://www.eluniversal.com.mx/", 1, "fronts_falsos", 0.95),
    ("acompanantes vip a domicilio", "https://www.eluniversal.com.mx/", 1, "fronts_falsos", 0.9),
    ("masajistas sin experiencia", "https://www.eluniversal.com.mx/", 1, "fronts_falsos", 0.75),
    ("modelos para contenido adulto", "https://www.eluniversal.com.mx/", 1, "fronts_falsos", 0.9),
    ("chicas para fiestas privadas", "https://www.eluniversal.com.mx/", 1, "fronts_falsos", 0.9),
    ("trae tu acta de nacimiento y vente", "https://www.eluniversal.com.mx/", 1, "fronts_falsos", 0.7),

    # ============ PHASE 2 — Enganche / Aislamiento / PII ============
    ("dame tus datos y te resuelvo", "https://www.lisanews.org/", 2, "perfilamiento", 0.7),
    ("mandame foto de tu credencial", "https://www.eluniversal.com.mx/", 2, "perfilamiento", 0.9),
    ("mandame foto de tu ine", "https://www.eluniversal.com.mx/", 2, "perfilamiento", 0.9),
    ("foto de tu identificacion porfa", "https://www.eluniversal.com.mx/", 2, "perfilamiento", 0.85),
    ("dime tu curp", "https://www.eluniversal.com.mx/", 2, "perfilamiento", 0.85),
    ("a que prepa vas", "https://www.lja.mx/2025/04/", 2, "perfilamiento", 0.75),
    ("en que secu vas", "https://www.lja.mx/2025/04/", 2, "perfilamiento", 0.75),
    ("en que turno entras a la escuela", "https://www.lja.mx/2025/04/", 2, "perfilamiento", 0.8),
    ("a que hora sales de la escuela", "https://www.lja.mx/2025/04/", 2, "perfilamiento", 0.8),
    ("cuantos hermanos tienes", "https://www.lja.mx/2025/04/", 2, "perfilamiento", 0.5),
    ("vives con tus papas", "https://www.lja.mx/2025/04/", 2, "perfilamiento", 0.55),
    ("trabajan tus papas", "https://www.lja.mx/2025/04/", 2, "perfilamiento", 0.55),
    ("a que hora estan solos en tu casa", "https://www.lja.mx/2025/04/", 2, "perfilamiento", 0.95),
    ("cuando salen tus papas de viaje", "https://www.lja.mx/2025/04/", 2, "perfilamiento", 0.9),
    ("mandame tu cuenta para depositar", "https://www.lisanews.org/", 2, "perfilamiento", 0.85),
    ("mandame tu clabe", "https://www.lisanews.org/", 2, "perfilamiento", 0.7),
    ("dame tu numero de tarjeta", "https://www.lisanews.org/", 2, "perfilamiento", 0.85),
    ("descarga signal y me hablas", "https://www.lja.mx/2025/04/", 2, "aislamiento_canal", 0.85),
    ("descarga telegram para hablar tranquilos", "https://www.lja.mx/2025/04/", 2, "aislamiento_canal", 0.85),
    ("vamonos a wickr", "https://www.lja.mx/2025/04/", 2, "aislamiento_canal", 0.85),
    ("borra esta conversacion", "https://www.lisanews.org/", 2, "secrecia", 0.85),
    ("borra el chat cada noche", "https://www.lisanews.org/", 2, "secrecia", 0.9),
    ("activa mensajes que se autodestruyen", "https://www.lisanews.org/", 2, "secrecia", 0.9),
    ("esto queda entre tu y yo", "https://www.eluniversal.com.mx/", 2, "secrecia", 0.85),
    ("nadie tiene que saber de esto", "https://www.eluniversal.com.mx/", 2, "secrecia", 0.85),
    ("no le digas a tu mama de mi", "https://www.eluniversal.com.mx/", 2, "secrecia", 0.95),
    ("ni a tu mejor amiga le cuentes", "https://www.eluniversal.com.mx/", 2, "secrecia", 0.85),
    ("eres mi secretito favorito", "https://www.eluniversal.com.mx/", 2, "grooming_emocional", 0.85),
    ("ya somos novios virtuales", "https://www.eluniversal.com.mx/", 2, "grooming_emocional", 0.7),
    ("nadie te entiende como yo", "https://www.eluniversal.com.mx/", 2, "grooming_emocional", 0.7),
    ("solo yo te quiero de verdad", "https://www.eluniversal.com.mx/", 2, "grooming_emocional", 0.75),
    ("ya soy tu mejor amigo virtual", "https://www.eluniversal.com.mx/", 2, "grooming_emocional", 0.65),
    ("te paso 200 robux ahora", "https://www.infobae.com/sociedad/2025/09/04/", 2, "roblox_grooming", 0.85),
    ("te mando robux gratis", "https://www.infobae.com/sociedad/2025/09/04/", 2, "roblox_grooming", 0.8),
    ("te regalo vbucks de fortnite", "https://www.infobae.com/sociedad/2025/09/04/", 2, "gaming_grooming", 0.8),
    ("te mando un nitro de discord", "https://www.infobae.com/sociedad/2025/09/04/", 2, "gaming_grooming", 0.75),
    ("te paso skins si me agregas", "https://www.infobae.com/sociedad/2025/09/04/", 2, "gaming_grooming", 0.8),
    ("vente a mi server privado de discord", "https://www.infobae.com/sociedad/2025/09/04/", 2, "aislamiento_canal", 0.85),
    ("vamonos a un grupo cerrado", "https://www.infobae.com/sociedad/2025/09/04/", 2, "aislamiento_canal", 0.7),
    ("tengo un grupo solo de plebes como tu", "https://www.infobae.com/sociedad/2025/09/04/", 2, "aislamiento_canal", 0.85),
    ("nos vemos en el lobby privado", "https://www.infobae.com/sociedad/2025/09/04/", 2, "aislamiento_canal", 0.7),
    ("te invito al chat secreto", "https://www.infobae.com/sociedad/2025/09/04/", 2, "aislamiento_canal", 0.85),
    ("hablemos por videollamada sin tu mama", "https://www.infobae.com/sociedad/2025/09/04/", 2, "aislamiento_canal", 0.95),
    ("vamos a una vc tu y yo", "https://www.infobae.com/sociedad/2025/09/04/", 2, "aislamiento_canal", 0.7),
    ("primero confianza luego negocio", "https://www.lisanews.org/", 2, "grooming_emocional", 0.6),
    ("yo te cuido mejor que tu familia", "https://www.lisanews.org/", 2, "grooming_emocional", 0.85),
    ("yo te resuelvo lo que tu casa no", "https://www.lisanews.org/", 2, "grooming_emocional", 0.85),

    # ============ PHASE 3 — Coerción / Amenaza / Sextorsión ============
    ("si no me contestas rapido publico tus fotos", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_amenaza", 0.95),
    ("si me ignoras subo todo", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_amenaza", 0.95),
    ("voy a publicar en internet y a tus contactos", "https://www.telediario.mx/nacional/", 3, "sextorsion_amenaza", 0.95),
    ("tengo tus contactos de whatsapp guardados", "https://www.telediario.mx/nacional/", 3, "sextorsion_evidencia", 0.9),
    ("ya tengo a tu mama agregada", "https://www.telediario.mx/nacional/", 3, "sextorsion_familia", 0.95),
    ("ya tengo a tu papa en contactos", "https://www.telediario.mx/nacional/", 3, "sextorsion_familia", 0.95),
    ("ya tengo el numero de tu novio", "https://www.telediario.mx/nacional/", 3, "sextorsion_pareja", 0.9),
    ("le voy a decir a tu novio lo que haces", "https://www.telediario.mx/nacional/", 3, "sextorsion_pareja", 0.9),
    ("agenda una cita con el jefe de plaza", "https://www.telediario.mx/nacional/", 3, "amenaza_directa", 0.95),
    ("o pones a un amigo o subo todo", "https://www.telediario.mx/nacional/", 3, "sextorsion_reclutamiento", 0.95),
    ("pon a tu primo o tu hermano", "https://www.telediario.mx/nacional/", 3, "sextorsion_reclutamiento", 0.95),
    ("o me mandas otra foto o subo las que tengo", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_amenaza", 0.95),
    ("o me mandas mas o se las paso a todos", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_amenaza", 0.95),
    ("te voy a quemar en internet", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_amenaza", 0.9),
    ("te quemo en redes", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_amenaza", 0.85),
    ("te exhibo en tiktok", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_amenaza", 0.9),
    ("te exhibo en instagram", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_amenaza", 0.9),
    ("te subo a paginas para adultos", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_publicacion", 0.95),
    ("te van a conocer en toda tu escuela", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_escuela", 0.95),
    ("le mando el video al grupo de tu salon", "https://www.excelsior.com.mx/comunidad/", 3, "sextorsion_escuela", 0.95),
    ("hago un deepfake con tu cara", "https://www.adn40.mx/es-tendencia/2025-07-23/", 3, "sextorsion_ia", 0.95),
    ("te hago un desnudo con ia", "https://www.adn40.mx/es-tendencia/2025-07-23/", 3, "sextorsion_ia", 0.95),
    ("ya tengo tu cara puesta en otro cuerpo", "https://www.adn40.mx/es-tendencia/2025-07-23/", 3, "sextorsion_ia", 0.95),
    ("uso ia para hacer tus nudes", "https://www.adn40.mx/es-tendencia/2025-07-23/", 3, "sextorsion_ia", 0.95),
    # cartel coercion
    ("ya estas dentro no te puedes salir", "https://www.lisanews.org/", 3, "coercion_no_salida", 0.95),
    ("ya entraste y aqui no hay vuelta atras", "https://www.lisanews.org/", 3, "coercion_no_salida", 0.95),
    ("la firma no perdona traidores", "https://www.lisanews.org/", 3, "amenaza_silencio", 0.95),
    ("aqui no hay renuncias", "https://www.lisanews.org/", 3, "coercion_no_salida", 0.9),
    ("si rajas te cae el comando", "https://www.lisanews.org/", 3, "amenaza_directa", 0.95),
    ("te mando levantar si abres la boca", "https://www.lisanews.org/", 3, "amenaza_directa", 0.95),
    ("te mando levantar a tu casa", "https://www.lisanews.org/", 3, "amenaza_directa", 0.95),
    ("ya ubicamos a tu familia", "https://www.lisanews.org/", 3, "coercion_familia", 0.95),
    ("sabemos donde estudia tu hermano", "https://www.lisanews.org/", 3, "coercion_familia", 0.95),
    ("sabemos donde trabaja tu mama", "https://www.lisanews.org/", 3, "coercion_familia", 0.95),
    ("te tenemos en la mira plebe", "https://www.lisanews.org/", 3, "amenaza_directa", 0.95),
    ("ya estas marcado plebe", "https://www.lisanews.org/", 3, "amenaza_directa", 0.9),
    ("o entras o te vas con todo y familia", "https://www.lisanews.org/", 3, "coercion_familia", 0.95),
    ("hablale al jefe ya o te jodes", "https://www.lisanews.org/", 3, "amenaza_directa", 0.9),
    ("te mando una visita a la casa", "https://www.lisanews.org/", 3, "amenaza_directa", 0.9),
    ("vas a aparecer en una bolsa", "https://www.lisanews.org/", 3, "amenaza_muerte", 0.95),
    ("te vamos a desaparecer", "https://www.lisanews.org/", 3, "amenaza_muerte", 0.95),

    # ============ PHASE 4 — Explotación / Operativa ============
    ("ve al punto a las 5", "https://www.lja.mx/2025/04/", 4, "operativa_punto", 0.85),
    ("vente al punto sin falta", "https://www.lja.mx/2025/04/", 4, "operativa_punto", 0.85),
    ("checate el punto cada hora", "https://www.lja.mx/2025/04/", 4, "operativa_punto", 0.9),
    ("repórtate al punto", "https://www.lja.mx/2025/04/", 4, "operativa_punto", 0.85),
    ("te toca turno de halcon esta noche", "https://www.lja.mx/2025/04/", 4, "operativa_halcon", 0.95),
    ("avisa cuando pase la patrulla", "https://www.lja.mx/2025/04/", 4, "operativa_halcon", 0.95),
    ("avisa si ves verdes", "https://www.lja.mx/2025/04/", 4, "operativa_halcon", 0.95),
    ("avisa si ves militares", "https://www.lja.mx/2025/04/", 4, "operativa_halcon", 0.95),
    ("repórtame movimientos raros", "https://www.lja.mx/2025/04/", 4, "operativa_halcon", 0.9),
    ("toma foto de la placa", "https://www.lja.mx/2025/04/", 4, "operativa_halcon", 0.85),
    ("toma video del que entra a la casa de enfrente", "https://www.lja.mx/2025/04/", 4, "operativa_halcon", 0.9),
    ("entrega el paquete en el punto", "https://www.lja.mx/2025/04/", 4, "operativa_entrega", 0.95),
    ("recoge el paquete en oxxo", "https://www.lja.mx/2025/04/", 4, "operativa_entrega", 0.85),
    ("entrega el sobre y te pago", "https://www.lja.mx/2025/04/", 4, "operativa_entrega", 0.9),
    ("vas a llevar la merca a la zona", "https://www.lja.mx/2025/04/", 4, "venta_droga", 0.95),
    ("acomoda la merca en bolsitas", "https://www.lja.mx/2025/04/", 4, "venta_droga", 0.95),
    ("te toca empacar las grapas", "https://www.lja.mx/2025/04/", 4, "venta_droga", 0.95),
    ("te toca repartir piedra", "https://www.lja.mx/2025/04/", 4, "venta_droga", 0.95),
    ("vendele al cliente del punto", "https://www.lja.mx/2025/04/", 4, "venta_droga", 0.95),
    ("cobra 100 por dosis", "https://www.lja.mx/2025/04/", 4, "venta_droga", 0.9),
    ("cobra el piso al de la tienda", "https://www.lja.mx/2025/04/", 4, "extorsion_op", 0.95),
    ("ya cobraste el piso al de la tortilla", "https://www.lja.mx/2025/04/", 4, "extorsion_op", 0.95),
    ("le pasas la cuota cada lunes", "https://www.lja.mx/2025/04/", 4, "extorsion_op", 0.9),
    ("le tocas la puerta al moroso", "https://www.lja.mx/2025/04/", 4, "extorsion_op", 0.85),
    ("dale un susto al que no paga", "https://www.lja.mx/2025/04/", 4, "extorsion_op", 0.95),
    ("manda video amenazando al deudor", "https://www.lja.mx/2025/04/", 4, "extorsion_op", 0.95),
    ("graba al cliente sin que sepa", "https://www.eluniversal.com.mx/", 4, "csam_op", 0.95),
    ("manda video sin ropa para el cliente", "https://www.eluniversal.com.mx/", 4, "csam_op", 0.95),
    ("haz videollamada caliente con el cliente", "https://www.eluniversal.com.mx/", 4, "csam_op", 0.95),
    ("atiende al cliente del cuarto 3", "https://www.eluniversal.com.mx/", 4, "trata_op", 0.95),
    ("hoy te toca atender 5 clientes", "https://www.eluniversal.com.mx/", 4, "trata_op", 0.95),
    ("vas con el cliente al hotel", "https://www.eluniversal.com.mx/", 4, "trata_op", 0.95),
    ("la madrota te dice cuanto cobras", "https://www.eluniversal.com.mx/", 4, "trata_op", 0.95),
    ("no salgas del cuarto sin permiso", "https://www.eluniversal.com.mx/", 4, "trata_op", 0.95),
    ("entrega la lana de la noche", "https://www.eluniversal.com.mx/", 4, "trata_op", 0.95),
    # operativa traslado
    ("subete a la troca negra", "https://www.lja.mx/2025/04/", 4, "operativa_traslado", 0.95),
    ("vas a viajar a la frontera ya", "https://www.lja.mx/2025/04/", 4, "operativa_traslado", 0.95),
    ("te pago el camion a tijuana ya", "https://www.lja.mx/2025/04/", 4, "operativa_traslado", 0.95),
    ("nos vemos en la central de autobuses 6 am", "https://www.lja.mx/2025/04/", 4, "operativa_traslado", 0.85),
    ("trae el cuerno y los cargadores", "https://www.lja.mx/2025/04/", 4, "operativa_armas", 0.95),
    ("trae el fierro al punto", "https://www.lja.mx/2025/04/", 4, "operativa_armas", 0.95),
    ("dale piso al fulano", "https://www.lja.mx/2025/04/", 4, "amenaza_operacion", 0.95),
    ("ya mero levantamos al objetivo", "https://www.lja.mx/2025/04/", 4, "amenaza_operacion", 0.95),
    ("hazle el levanton al chamaco", "https://www.lja.mx/2025/04/", 4, "amenaza_operacion", 0.95),
    ("encarguense del soplon", "https://www.lja.mx/2025/04/", 4, "amenaza_operacion", 0.95),
    # control / lock-in
    ("no contestes mensajes de tu casa", "https://www.lisanews.org/", 4, "control_aislamiento", 0.9),
    ("apaga el celular cuando te lo diga", "https://www.lisanews.org/", 4, "control_aislamiento", 0.85),
    ("dame tu telefono cada noche", "https://www.lisanews.org/", 4, "control_aislamiento", 0.85),
    ("aqui mando yo y obedeces", "https://www.lisanews.org/", 4, "control_aislamiento", 0.85),
]


def post(text: str):
    body = json.dumps({"text": text, "use_llm": False}).encode("utf-8")
    req = urllib.request.Request(
        API,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')[:200]}"}
    except Exception as e:
        return {"_error": str(e)}


def main():
    rows = []
    falsneg = []
    n = len(CANDIDATES)
    print(f"Testing {n} phrases against {API} (rate limit ~12/min)...")
    for i, (phrase, src, expected_phase, cat, weight) in enumerate(CANDIDATES, 1):
        r = post(phrase)
        if "_error" in r:
            level = "ERROR"
            score = 0.0
            cats = []
            print(f"[{i}/{n}] ERROR: {r['_error']}  ({phrase[:50]})")
        else:
            level = r.get("risk_level", "?")
            score = float(r.get("risk_score", 0.0))
            cats = r.get("categories", []) or []
            print(f"[{i}/{n}] {level:9s} {score:.2f}  {phrase[:60]}")
        if level == "SEGURO":
            verdict = "FALSE_NEGATIVE"
            falsneg.append({
                "phrase": strip_diacritics(phrase.lower()),
                "phrase_raw": phrase,
                "source_url": src,
                "expected_phase": expected_phase,
                "suggested_category": cat,
                "suggested_weight": weight,
            })
        elif level == "ERROR":
            verdict = "ERROR"
        else:
            verdict = "ALREADY_COVERED"
        rows.append({
            "phrase": phrase,
            "source_url": src,
            "expected_phase": expected_phase,
            "actual_level": level,
            "actual_score": f"{score:.3f}",
            "verdict": verdict,
            "suggested_weight": weight,
            "suggested_category": cat,
            "categories_returned": "|".join(cats[:6]),
        })
        # rate limit: ~12/min
        if i < n:
            time.sleep(5.1)

    # write CSV
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "phrase", "source_url", "expected_phase",
                "actual_level", "actual_score", "verdict",
                "suggested_weight", "suggested_category",
                "categories_returned",
            ],
        )
        w.writeheader()
        for row in rows:
            w.writerow(row)
    print(f"\nCSV written: {OUT_CSV}")

    # write neg JSON for the patcher
    OUT_NEG.write_text(json.dumps(falsneg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"FN JSON written: {OUT_NEG}  ({len(falsneg)} rows)")

    by_phase = {1: 0, 2: 0, 3: 0, 4: 0}
    for fn in falsneg:
        by_phase[fn["expected_phase"]] = by_phase.get(fn["expected_phase"], 0) + 1
    print(f"FN by phase: {by_phase}")
    total_already = sum(1 for r in rows if r["verdict"] == "ALREADY_COVERED")
    total_err = sum(1 for r in rows if r["verdict"] == "ERROR")
    print(f"Tested: {n}  | Already covered: {total_already}  | FN: {len(falsneg)}  | Errors: {total_err}")


if __name__ == "__main__":
    main()
