"""Comprehensive test corpus v2 — 240+ phrases organized for iterative testing.

Each entry: (phrase, expected_level, expected_phase, category, notes)
- expected_level: SEGURO | ATENCION | PELIGRO | ATENCION_OR_PELIGRO
- expected_phase: 1-4, 'safe', or 'distress'
- category: short tag
- notes: free text (variant type, source pattern, etc.)

Categories aim to stress all known weak spots:
- aggressor speech (canonical) — should ALL hit
- victim reception ("me X-aron")
- chat abbreviations + typos
- money without $
- Mexican slang (lana, billete, feria, varos)
- regional + emerging cartel jerga
- Roblox/Discord/TikTok grooming
- sextortion (aggressor + victim)
- distress signals
- HARD-MODE safe phrases (look risky but aren't)
"""
from __future__ import annotations

CORPUS = [
    # ────────────────── PHASE 1 — Captación (60 phrases) ──────────────────
    # Aggressor canonical (5)
    ("te pago 15000 a la semana de halcón", "ATENCION_OR_PELIGRO", 1, "aggressor_canon", "money+role"),
    ("te ofrezco chamba fácil", "ATENCION_OR_PELIGRO", 1, "aggressor_canon", "fake_job"),
    ("hay jale para ti", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "jale=trabajo"),
    ("se solicita gente para la mana", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "mana=cartel"),
    ("trabajo para las 4 letras", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "4letras=cartel"),

    # Victim reception (10)
    ("me ofrecieron 15000 pesos a la semana", "ATENCION_OR_PELIGRO", 1, "victim_offer", "money_received"),
    ("me ofrecieron jale en TikTok", "ATENCION_OR_PELIGRO", 1, "victim_offer", "platform+jale"),
    ("alguien me escribió ofreciendo dinero", "ATENCION_OR_PELIGRO", 1, "victim_offer", "stranger_offer"),
    ("un desconocido me contactó por Instagram", "ATENCION_OR_PELIGRO", 1, "victim_offer", "stranger_platform"),
    ("me ofrecieron lana fácil", "ATENCION_OR_PELIGRO", 1, "victim_jerga", "money_slang"),
    ("me prometieron pago semanal", "ATENCION_OR_PELIGRO", 1, "victim_offer", "promise"),
    ("me invitaron a un jale", "ATENCION_OR_PELIGRO", 1, "victim_jerga", "invitation"),
    ("vi un anuncio de dinero fácil en redes", "ATENCION_OR_PELIGRO", 1, "victim_ad", "platform_ad"),
    ("me agregaron de la nada y me ofrecieron trabajo", "ATENCION_OR_PELIGRO", 1, "victim_offer", "stranger_addd"),
    ("me dijeron que ganaba 20 mil semanales", "ATENCION_OR_PELIGRO", 1, "victim_offer", "promise_high"),

    # Chat abbreviations + typos (10)
    ("me ofresieron 15 mil x semana", "ATENCION_OR_PELIGRO", 1, "typo_chat", "ofresieron+x"),
    ("me ofrecio chamba xq necesito feria", "ATENCION_OR_PELIGRO", 1, "typo_chat", "xq+feria"),
    ("k onda con el jale", "ATENCION_OR_PELIGRO", 1, "chat_abbr", "k=que"),
    ("me dijo q hay billete", "ATENCION_OR_PELIGRO", 1, "chat_abbr", "q=que"),
    ("toy buscando jale rapido", "ATENCION_OR_PELIGRO", 1, "chat_abbr", "toy=estoy"),
    ("vrdd hay paga buena", "ATENCION_OR_PELIGRO", 1, "chat_abbr", "vrdd=verdad"),
    ("dame DM para pasarte la info", "ATENCION_OR_PELIGRO", 1, "social_dm", "dm_recruit"),
    ("escribeme al privado y te paso", "ATENCION_OR_PELIGRO", 1, "social_dm", "privado_recruit"),
    ("info en bio para los que se animen", "ATENCION_OR_PELIGRO", 1, "social_bio", "bio_recruit"),
    ("checate la bio", "ATENCION_OR_PELIGRO", 1, "social_bio", "bio_redirect"),

    # Money without $ + slang (10)
    ("hay billete para ti", "ATENCION_OR_PELIGRO", 1, "jerga_money", "billete"),
    ("te paso lana facil", "ATENCION_OR_PELIGRO", 1, "jerga_money", "lana"),
    ("hay feria semanal segura", "ATENCION_OR_PELIGRO", 1, "jerga_money", "feria"),
    ("ganas 30 mil al mes garantizado", "ATENCION_OR_PELIGRO", 1, "money_promise", "guaranteed"),
    ("te pagamos por viaje 5 mil", "ATENCION_OR_PELIGRO", 1, "money_promise", "per_trip"),
    ("buena paga semanal hospedaje y comida", "ATENCION_OR_PELIGRO", 1, "fronts_falsos", "extras_included"),
    ("vacaciones equipo táctico calzado y ropa", "ATENCION_OR_PELIGRO", 1, "cartel_oferta", "tactical_gear"),
    ("te damos casa carro y mujeres", "ATENCION_OR_PELIGRO", 1, "cartel_oferta", "lifestyle_lure"),
    ("la firma cuida a los suyos", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "firma=cartel"),
    ("la empresa te da seguridad", "ATENCION_OR_PELIGRO", 1, "cartel_eufemismo", "empresa=cartel"),

    # Cartel jerga regional (10)
    ("se busca puchador para el barrio", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "puchador=vendedor"),
    ("solicitamos halcones de confianza", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "halcon=vigia"),
    ("se necesita puntero del barrio", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "puntero"),
    ("tenemos estaca abierta en el punto", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "estaca"),
    ("eres bueno para el jale duro", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "jale_duro"),
    ("le entras al jale o no", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "presion_decision"),
    ("te metes con la firma o que", "ATENCION_OR_PELIGRO", 1, "cartel_jerga", "presion_firma"),
    ("se busca chofer particular urgente", "ATENCION_OR_PELIGRO", 1, "fronts_falsos", "chofer_front"),
    ("guardia de seguridad pago diario en efectivo", "ATENCION_OR_PELIGRO", 1, "fronts_falsos", "guardia_front"),
    ("modelos para evento privado", "ATENCION_OR_PELIGRO", 1, "fronts_falsos", "modelo_front"),

    # Fronts engañosos (5)
    ("limpieza casa rancho buen pago", "ATENCION_OR_PELIGRO", 1, "fronts_falsos", "rancho_front"),
    ("mesera para fiesta privada vip", "ATENCION_OR_PELIGRO", 1, "fronts_falsos", "vip_front"),
    ("promotora de antros viernes y sabados", "ATENCION_OR_PELIGRO", 1, "fronts_falsos", "antros_front"),
    ("sin experiencia te capacitamos", "ATENCION_OR_PELIGRO", 1, "fronts_falsos", "capacitacion_front"),
    ("apoyamos a madres solteras y estudiantes", "ATENCION_OR_PELIGRO", 1, "fronts_falsos", "vulnerable_targeting"),

    # Topología narco (5)
    ("nos vemos al rancho mañana", "ATENCION_OR_PELIGRO", 1, "topologia_narco", "rancho"),
    ("te recogemos para llevarte al monte", "ATENCION_OR_PELIGRO", 1, "topologia_narco", "monte"),
    ("vamos a la finca el sabado", "ATENCION_OR_PELIGRO", 1, "topologia_narco", "finca"),
    ("si voy al rancho me pagan", "ATENCION_OR_PELIGRO", 1, "topologia_narco", "rancho_recibida"),
    ("el punto te queda cerca", "ATENCION_OR_PELIGRO", 1, "topologia_narco", "punto"),

    # Roblox/Discord grooming (5)
    ("te paso 5 mil robux si me das tus datos", "ATENCION_OR_PELIGRO", 1, "roblox_grooming", "robux_quid"),
    ("eres muy maduro para tu edad", "ATENCION_OR_PELIGRO", 1, "grooming_edad", "age_flattery"),
    ("vamos a Discord para hablar mejor", "ATENCION_OR_PELIGRO", 1, "cambio_canal", "discord_pivot"),
    ("dame tu user de Roblox y te regalo", "ATENCION_OR_PELIGRO", 1, "roblox_grooming", "user_collect"),
    ("tu mamá no se enteraría", "ATENCION_OR_PELIGRO", 1, "grooming_secreto", "secrecy_explicit"),

    # ────────────────── PHASE 2 — Enganche (40 phrases) ──────────────────
    # Aggressor canonical (5)
    ("pásate a Telegram para hablar a solas", "ATENCION_OR_PELIGRO", 2, "aggressor_canon", "telegram_pivot"),
    ("no le digas a nadie de esto", "ATENCION_OR_PELIGRO", 2, "aggressor_canon", "secrecy"),
    ("dame tu ubicación en vivo", "ATENCION_OR_PELIGRO", 2, "aggressor_canon", "location_request"),
    ("cuál es la dirección de tu casa", "ATENCION_OR_PELIGRO", 2, "aggressor_canon", "address_request"),
    ("vámonos a Signal que es más privado", "ATENCION_OR_PELIGRO", 2, "aggressor_canon", "signal_pivot"),

    # Victim reception (10)
    ("me pidieron que me pasara a Telegram", "ATENCION_OR_PELIGRO", 2, "victim_reception", "telegram_received"),
    ("me dijeron que no le contara a nadie", "ATENCION_OR_PELIGRO", 2, "victim_reception", "secrecy_received"),
    ("me pidieron mi ubicación", "ATENCION_OR_PELIGRO", 2, "victim_reception", "location_received"),
    ("me preguntaron donde vivo", "ATENCION_OR_PELIGRO", 2, "victim_reception", "address_received"),
    ("me pidieron mi escuela", "ATENCION_OR_PELIGRO", 2, "victim_reception", "school_received"),
    ("me pidieron mi número de teléfono", "ATENCION_OR_PELIGRO", 2, "victim_reception", "phone_received"),
    ("me dijeron que era nuestro secreto", "ATENCION_OR_PELIGRO", 2, "victim_reception", "secret_received"),
    ("me presionaron para responder rapido", "ATENCION_OR_PELIGRO", 2, "victim_reception", "pressure_received"),
    ("me agregaron a un grupo extraño", "ATENCION_OR_PELIGRO", 2, "victim_reception", "group_added"),
    ("me dijeron que no avisara a mis papás", "ATENCION_OR_PELIGRO", 2, "victim_reception", "parents_secrecy"),

    # Channel jumping variants (8)
    ("vamos a Snapchat porque desaparece", "ATENCION_OR_PELIGRO", 2, "ephemeral_pivot", "snap_disappear"),
    ("pásamelo por DM porque aquí no", "ATENCION_OR_PELIGRO", 2, "channel_pivot", "dm_pivot"),
    ("me pidieron pasarme a Snap", "ATENCION_OR_PELIGRO", 2, "ephemeral_pivot", "snap_received"),
    ("aquí nadie nos ve, dime", "ATENCION_OR_PELIGRO", 2, "false_privacy", "isolation_promise"),
    ("vamos a un chat secreto", "ATENCION_OR_PELIGRO", 2, "channel_pivot", "secret_chat"),
    ("borra los mensajes después", "ATENCION_OR_PELIGRO", 2, "evidence_destruction", "delete_after"),
    ("usa modo incógnito", "ATENCION_OR_PELIGRO", 2, "evidence_destruction", "incognito"),
    ("apaga la ubicación de tu celular", "ATENCION_OR_PELIGRO", 2, "evidence_destruction", "location_off"),

    # PII collection (8)
    ("mándame foto de la fachada de tu casa", "ATENCION_OR_PELIGRO", 2, "pii_collection", "facade_photo"),
    ("dame el nombre completo de tu mamá", "ATENCION_OR_PELIGRO", 2, "pii_collection", "mother_name"),
    ("a qué hora sales de la escuela", "ATENCION_OR_PELIGRO", 2, "pii_schedule", "school_schedule"),
    ("por dónde caminas a tu casa", "ATENCION_OR_PELIGRO", 2, "pii_schedule", "route_mapping"),
    ("tu papá tiene dinero", "ATENCION_OR_PELIGRO", 2, "pii_economic", "family_economic"),
    ("vives sola con tu mamá", "ATENCION_OR_PELIGRO", 2, "pii_household", "household_mapping"),
    ("a qué se dedican tus papás", "ATENCION_OR_PELIGRO", 2, "pii_household", "parents_job"),
    ("cuántos hermanos tienes", "ATENCION_OR_PELIGRO", 2, "pii_household", "siblings"),

    # Friendship pretense (5)
    ("nadie te entiende como yo", "ATENCION_OR_PELIGRO", 2, "false_friendship", "isolation_emotional"),
    ("yo sí te valoro", "ATENCION_OR_PELIGRO", 2, "false_friendship", "value_promise"),
    ("yo te cuido mejor que tu familia", "ATENCION_OR_PELIGRO", 2, "false_friendship", "family_replacement"),
    ("eres especial para mí", "ATENCION_OR_PELIGRO", 2, "false_friendship", "specialness"),
    ("confía solo en mí", "ATENCION_OR_PELIGRO", 2, "false_friendship", "trust_isolation"),

    # Pressure tactics (4)
    ("apurate que no tenemos tiempo", "ATENCION_OR_PELIGRO", 2, "pressure_tactic", "time_pressure"),
    ("decide ya o pierdes la oportunidad", "ATENCION_OR_PELIGRO", 2, "pressure_tactic", "ultimatum"),
    ("no me hagas perder la paciencia", "ATENCION_OR_PELIGRO", 2, "pressure_tactic", "patience_threat"),
    ("contesta rapido si quieres entrar", "ATENCION_OR_PELIGRO", 2, "pressure_tactic", "quick_response"),

    # ────────────────── PHASE 3 — Coerción (50 phrases) ──────────────────
    # Aggressor canonical death threats (10)
    ("te voy a matar", "PELIGRO", 3, "death_threat", "canonical"),
    ("te vamos a matar si te rajas", "PELIGRO", 3, "death_threat", "conditional"),
    ("te voy a desaparecer", "PELIGRO", 3, "death_threat", "disappear"),
    ("te voy a dar piso", "PELIGRO", 3, "death_threat", "jerga_dar_piso"),
    ("te ponemos en bolsa negra", "PELIGRO", 3, "death_threat", "jerga_bolsa"),
    ("te toca el levantón", "PELIGRO", 3, "death_threat", "jerga_levanton"),
    ("ya estás en la lista", "PELIGRO", 3, "marked_for_death", "list"),
    ("ya estás marcado", "PELIGRO", 3, "marked_for_death", "marked"),
    ("te vamos a tronar", "PELIGRO", 3, "death_threat", "jerga_tronar"),
    ("te toca dar el viaje", "PELIGRO", 3, "death_threat", "jerga_viaje"),

    # Victim reception (15)
    ("me van a matar", "PELIGRO", 3, "victim_threat", "received_death"),
    ("me dijeron que me iban a matar", "PELIGRO", 3, "victim_threat", "received_past"),
    ("me amenazaron de muerte", "PELIGRO", 3, "victim_threat", "threat_explicit"),
    ("me amenazaron con matarme", "PELIGRO", 3, "victim_threat", "threat_with_murder"),
    ("me van a desaparecer si no respondo", "PELIGRO", 3, "victim_threat_conditional", "disappear_received"),
    ("me dijeron que ya saben demasiado", "PELIGRO", 3, "knowledge_threat", "knows_too_much"),
    ("me dijeron que no hay vuelta atras", "PELIGRO", 3, "no_escape", "no_return"),
    ("me amenazaron si hablo", "PELIGRO", 3, "silence_threat", "speak_threat"),
    ("alguien me dijo que me iban a desaparecer si no coopero", "PELIGRO", 3, "victim_threat_conditional", "long_form"),
    ("me tienen amenazado", "PELIGRO", 3, "ongoing_threat", "active_state"),
    ("me tienen vigilado", "PELIGRO", 3, "surveillance", "active_surveillance"),
    ("saben donde vivo", "PELIGRO", 3, "doxx_received", "doxxed"),
    ("saben donde estudio", "PELIGRO", 3, "doxx_received", "school_doxx"),
    ("me siguieron hasta mi casa", "PELIGRO", 3, "physical_following", "followed_home"),
    ("me obligaron a hacer cosas", "PELIGRO", 3, "coercion_obligacion", "forced"),

    # Distress states (10)
    ("tengo mucho miedo", "ATENCION_OR_PELIGRO", "distress", "distress_fear", "fear_state"),
    ("tengo miedo de que me hagan algo", "PELIGRO", "distress", "distress_anticipation", "fear_specific"),
    ("estoy aterrado", "ATENCION_OR_PELIGRO", "distress", "distress_terror", "terror"),
    ("estoy asustada porque no me dejan en paz", "PELIGRO", "distress", "distress_followup", "harassment_state"),
    ("creo que me van a hacer algo", "PELIGRO", "distress", "distress_anticipation", "anticipation"),
    ("siento que estoy en peligro", "PELIGRO", "distress", "distress_self_assess", "self_assess"),
    ("no puedo dormir del miedo", "ATENCION_OR_PELIGRO", "distress", "distress_physiological", "insomnia_fear"),
    ("me siento atrapado", "ATENCION_OR_PELIGRO", "distress", "distress_trapped", "trapped"),
    ("me siento atrapada y sola", "PELIGRO", "distress", "distress_isolation", "alone_trapped"),
    ("ya no se que hacer", "ATENCION_OR_PELIGRO", "distress", "distress_helpless", "helpless"),

    # Conditional threats (10)
    ("si no respondo me van a", "PELIGRO", 3, "conditional_threat", "incomplete_threat"),
    ("si no contesto me van a buscar", "PELIGRO", 3, "conditional_threat", "search_threat"),
    ("si no voy me van a matar", "PELIGRO", 3, "conditional_threat", "go_or_die"),
    ("si no pago me van a hacer daño", "PELIGRO", 3, "conditional_threat", "pay_or_harm"),
    ("si no obedeces hay consecuencias", "PELIGRO", 3, "conditional_threat", "obey_or_else"),
    ("si me rajo me matan", "PELIGRO", 3, "conditional_threat", "betray_or_die"),
    ("si hablo me desaparecen", "PELIGRO", 3, "silence_or_die", "speak_die"),
    ("si me ignoras subo todo", "PELIGRO", 3, "publish_threat", "ignore_publish"),
    ("si no me contestas rapido publico tus fotos", "PELIGRO", 3, "sextort_conditional", "fast_or_publish"),
    ("una sola palabra y se acabó", "PELIGRO", 3, "silence_or_die", "one_word"),

    # Surveillance and stalking (5)
    ("me tienen viendo todo el tiempo", "ATENCION_OR_PELIGRO", 3, "surveillance", "constant_watch"),
    ("hay un carro afuera de mi casa todos los días", "PELIGRO", 3, "stalking", "vehicle_outside"),
    ("vi al mismo tipo en la escuela y en la casa", "PELIGRO", 3, "stalking", "same_person"),
    ("me han llamado de números desconocidos", "ATENCION_OR_PELIGRO", 3, "harassment", "unknown_numbers"),
    ("alguien comparte mi ubicación", "PELIGRO", 3, "stalking", "location_shared"),

    # ────────────────── PHASE 4 — Explotación (40 phrases) ──────────────────
    # Aggressor sextortion (10)
    ("manda fotos sin ropa", "PELIGRO", 4, "sextort_request", "nude_request"),
    ("mandame nudes ahora", "PELIGRO", 4, "sextort_request", "nudes_now"),
    ("manda video sin ropa", "PELIGRO", 4, "sextort_request", "video_request"),
    ("mandame fotos o las publico en tu escuela", "PELIGRO", 4, "sextort_threat", "publish_school"),
    ("si no mandas las publico todas", "PELIGRO", 4, "sextort_threat", "publish_all"),
    ("voy a mostrar tus fotos a tu mamá", "PELIGRO", 4, "sextort_family", "mother_show"),
    ("le voy a mandar todo a tu papá", "PELIGRO", 4, "sextort_family", "father_show"),
    ("voy a publicar el video", "PELIGRO", 4, "sextort_publish", "video_publish"),
    ("te subo a páginas porno", "PELIGRO", 4, "sextort_porn", "porn_upload"),
    ("le mando todo a tus contactos", "PELIGRO", 4, "sextort_contacts", "contacts_share"),

    # Victim sextortion reception (10)
    ("me piden fotos íntimas", "PELIGRO", 4, "victim_sextort_request", "intimate_received"),
    ("me piden nudes amenazandome", "PELIGRO", 4, "victim_sextort_threat", "nudes_threatened"),
    ("me amenazan con publicar mis fotos", "PELIGRO", 4, "victim_sextort_threat", "publish_received"),
    ("me amenazan con publicar mis videos", "PELIGRO", 4, "victim_sextort_threat", "video_publish_received"),
    ("me dicen que si no mando me publican", "PELIGRO", 4, "victim_sextort_conditional", "publish_conditional"),
    ("me chantajearon con fotos mías", "PELIGRO", 4, "victim_sextort_blackmail", "blackmailed"),
    ("me extorsionan con mis fotos", "PELIGRO", 4, "victim_extortion", "extorted"),
    ("me piden video llamada sin ropa", "PELIGRO", 4, "victim_sextort_video", "video_call"),
    ("me hicieron deepfakes con mis fotos", "PELIGRO", 4, "victim_deepfake", "deepfake_received"),
    ("me sacaron videos sin permiso", "PELIGRO", 4, "victim_csam", "non_consensual"),

    # Operative orders narco (10)
    ("ve armado mañana", "PELIGRO", 4, "operative_order", "armed_order"),
    ("trae la coca al punto", "PELIGRO", 4, "drug_transport", "coca_transport"),
    ("tienes que levantar a alguien", "PELIGRO", 4, "kidnap_order", "kidnap"),
    ("vamos al punto a vender", "PELIGRO", 4, "drug_sales", "sell_at_point"),
    ("te toca cargar piedra", "PELIGRO", 4, "drug_transport", "piedra_transport"),
    ("hay que callar al cuervo", "PELIGRO", 4, "silencing_order", "silence_order"),
    ("le sacas el alma", "PELIGRO", 4, "kill_order_jerga", "soul_extract"),
    ("hay que limpiar el punto", "PELIGRO", 4, "removal_order", "clean_point"),
    ("vas a halconear hoy", "PELIGRO", 4, "halcon_order", "halconeo_order"),
    ("vas a vender en la prepa", "PELIGRO", 4, "school_sales", "school_drug_sales"),

    # Victim operative coercion (5)
    ("me obligaron a llevar algo al punto", "PELIGRO", 4, "victim_operative", "forced_transport"),
    ("me obligaron a vender droga en la escuela", "PELIGRO", 4, "victim_operative", "forced_school_sales"),
    ("me obligaron a reclutar a mis amigos", "PELIGRO", 4, "victim_recruit", "forced_recruit"),
    ("me forzaron a hacer cosas peligrosas", "PELIGRO", 4, "victim_operative", "forced_dangerous"),
    ("me hicieron entregar paquetes", "PELIGRO", 4, "victim_operative", "forced_delivery"),

    # Money/payment exploitation (5)
    ("deposita 5000 pesos a esta cuenta", "PELIGRO", 4, "payment_demand", "deposit_demand"),
    ("transfiere 10 mil ahora mismo", "PELIGRO", 4, "payment_demand", "transfer_demand"),
    ("paga gift card de Amazon o subo todo", "PELIGRO", 4, "giftcard_extort", "giftcard_amazon"),
    ("me piden gift card de Steam", "PELIGRO", 4, "giftcard_extort_received", "giftcard_steam"),
    ("dame los datos de tu tarjeta", "PELIGRO", 4, "card_phishing", "card_request"),

    # ────────────────── SAFE phrases (50 — should NEVER fire) ──────────────────
    # Casual conversation (10)
    ("hola que onda", "SEGURO", "safe", "greeting", "casual"),
    ("buenas tardes amigo", "SEGURO", "safe", "greeting", "polite"),
    ("nos vemos mañana", "SEGURO", "safe", "scheduling", "tomorrow"),
    ("vienes al cumple el sabado", "SEGURO", "safe", "scheduling", "birthday"),
    ("vamos al cine este finde", "SEGURO", "safe", "scheduling", "cinema"),
    ("como estuvo tu dia", "SEGURO", "safe", "casual", "day_check"),
    ("estoy bien gracias", "SEGURO", "safe", "casual", "small_talk"),
    ("que vas a hacer", "SEGURO", "safe", "casual", "plans"),
    ("estoy aburrido", "SEGURO", "safe", "casual", "bored"),
    ("ya merito llegamos", "SEGURO", "safe", "casual", "almost_there"),

    # School (8)
    ("tengo mucha tarea", "SEGURO", "safe", "school", "homework"),
    ("me reprobaron en mate", "SEGURO", "safe", "school", "failed_math"),
    ("saque buena nota en historia", "SEGURO", "safe", "school", "good_grade"),
    ("el examen estuvo facil", "SEGURO", "safe", "school", "easy_exam"),
    ("la clase de inglés me aburre", "SEGURO", "safe", "school", "boring_class"),
    ("voy a estudiar para el final", "SEGURO", "safe", "school", "studying"),
    ("el maestro me regañó", "SEGURO", "safe", "school", "teacher_scold"),
    ("ya termine la tarea", "SEGURO", "safe", "school", "homework_done"),

    # Family (6)
    ("mi mamá no me deja salir", "SEGURO", "safe", "family", "mom_no_out"),
    ("mi papá esta enojado", "SEGURO", "safe", "family", "dad_angry"),
    ("mi hermana me molesta", "SEGURO", "safe", "family", "sister_annoy"),
    ("voy con mis tios el domingo", "SEGURO", "safe", "family", "uncles_visit"),
    ("mi abuela me hizo de comer", "SEGURO", "safe", "family", "grandma_cooked"),
    ("me voy con mis primos", "SEGURO", "safe", "family", "cousins_outing"),

    # Casual money (10) — HARD CASE: must not trigger as extortion
    ("me sacaron 500 pesos del monedero", "SEGURO", "safe", "casual_money", "wallet_stolen"),
    ("me robaron la cartera ayer", "SEGURO", "safe", "casual_money", "wallet_pickpocket"),
    ("me cobraron 200 pesos por el envio", "SEGURO", "safe", "casual_money", "shipping_cost"),
    ("compre un cafe de 50 pesos", "SEGURO", "safe", "casual_money", "coffee_bought"),
    ("le pague 100 pesos a mi amigo", "SEGURO", "safe", "casual_money", "friend_paid"),
    ("tengo que ahorrar para los tenis", "SEGURO", "safe", "casual_money", "saving_shoes"),
    ("cuanto cuesta el helado", "SEGURO", "safe", "casual_money", "ice_cream_price"),
    ("me prestaron 200 pesos en la cooperativa", "SEGURO", "safe", "casual_money", "loan_coop"),
    ("me regalaron mi mesada", "SEGURO", "safe", "casual_money", "allowance"),
    ("voy al super con mi papá", "SEGURO", "safe", "casual_money", "supermarket"),

    # Gaming (8)
    ("me ganaron en free fire", "SEGURO", "safe", "gaming", "lost_match"),
    ("subi de rango en valorant", "SEGURO", "safe", "gaming", "ranked_up"),
    ("vamos a jugar minecraft", "SEGURO", "safe", "gaming", "play_invite"),
    ("estoy en la final del torneo de fifa", "SEGURO", "safe", "gaming", "tournament"),
    ("ya termine el pase de batalla", "SEGURO", "safe", "gaming", "battle_pass_done"),
    ("me dieron item raro en el dungeon", "SEGURO", "safe", "gaming", "rare_item"),
    ("voy a stream en twitch", "SEGURO", "safe", "gaming", "stream"),
    ("subi un video a youtube", "SEGURO", "safe", "gaming", "youtube"),

    # Series/movies (5)
    ("vi el capítulo de narcos en netflix", "SEGURO", "safe", "media", "narcos_series"),
    ("estoy viendo stranger things", "SEGURO", "safe", "media", "stranger_things"),
    ("vi la nueva pelicula de marvel", "SEGURO", "safe", "media", "marvel_movie"),
    ("que peli vamos a ver", "SEGURO", "safe", "media", "movie_pick"),
    ("la película fue buenísima", "SEGURO", "safe", "media", "good_movie"),

    # Sports (3)
    ("voy a ir al gym", "SEGURO", "safe", "sports", "gym"),
    ("ganamos el partido ayer", "SEGURO", "safe", "sports", "won_match"),
    ("estoy entrenando para el maraton", "SEGURO", "safe", "sports", "training"),
]


if __name__ == "__main__":
    # Quick stats
    by_phase = {}
    by_level = {}
    for entry in CORPUS:
        ph = entry[2]
        lvl = entry[1]
        by_phase[ph] = by_phase.get(ph, 0) + 1
        by_level[lvl] = by_level.get(lvl, 0) + 1
    print(f"Total: {len(CORPUS)} phrases")
    print(f"By phase: {by_phase}")
    print(f"By expected level: {by_level}")
