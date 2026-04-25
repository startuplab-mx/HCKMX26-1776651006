"""One-shot script: add audit-round-1 patterns to the 4 phase JSONs.

These patterns close gaps surfaced by the resilience + dataset audits on
Apr 25 2026: sextortion (massive gap), Roblox/Discord grooming, Mexican
slang for money without $, cartel jerga (halcon/puchador/punto/estaca),
and reception-perspective phrases across all 4 phases.

Run once. Idempotent (skips patterns already present by exact match).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KW = ROOT / "backend" / "classifier" / "keywords"

PHASE1_NEW = [
    # Mexican slang for money — without dollar sign
    ("te doy lana facil", 0.85, "jerga_dinero", "jerga lana=dinero, oferta facil"),
    ("te paso lana", 0.75, "jerga_dinero", "jerga lana=dinero"),
    ("hay billete", 0.75, "jerga_dinero", "jerga billete=dinero"),
    ("billete facil", 0.8, "jerga_dinero", "jerga billete=dinero facil"),
    ("hay feria", 0.75, "jerga_dinero", "jerga feria=dinero"),
    ("feria rapida", 0.8, "jerga_dinero", "jerga feria=dinero rapida"),
    ("te pagamos bien", 0.7, "oferta_vaga", "oferta sin detalles, primer contacto"),
    ("te pago bien", 0.7, "oferta_vaga", "oferta vaga sin contexto"),
    # Reception
    ("me ofrecieron lana", 0.8, "oferta_recibida", "jerga: oferta recibida"),
    ("me ofrecieron billete", 0.8, "oferta_recibida", "jerga: oferta recibida"),
    ("me ofrecieron feria", 0.8, "oferta_recibida", "jerga: oferta recibida"),
    # Fronts falsos / fake jobs
    ("guardia de seguridad pago diario", 0.85, "fronts_falsos", "fake job comun para sicarios"),
    ("chofer particular urgente", 0.8, "fronts_falsos", "front para narcos transportes"),
    ("valet parking se solicita", 0.7, "fronts_falsos", "front camuflado"),
    ("limpieza casa rancho", 0.85, "fronts_falsos", "front trata personas"),
    ("mesera para fiesta privada", 0.85, "fronts_falsos", "front comun de explotacion sexual"),
    ("modelos para evento", 0.8, "fronts_falsos", "front comun de explotacion"),
    ("promotora de antros", 0.75, "fronts_falsos", "front de explotacion sexual"),
    ("chico para repartir", 0.7, "fronts_falsos", "front pucho/halcon menor"),
    ("sin experiencia te capacitamos", 0.75, "fronts_falsos", "capacitacion=eufemismo reclutamiento"),
    # Recruitment via social
    ("mandame dm", 0.7, "red_social_dm", "cebo a dm en redes"),
    ("manda dm para info", 0.8, "red_social_dm", "cebo a dm para info trabajo"),
    ("dm para trabajo", 0.85, "red_social_dm", "cebo de reclutamiento via dm"),
    ("info en bio", 0.75, "red_social_bio", "patron tipico cuentas falsas reclutadoras"),
    ("checate la bio", 0.7, "red_social_bio", "derivar a perfil con info dudosa"),
    ("escribeme al privado", 0.8, "red_social_dm", "cambio a canal privado"),
    # Cartel jargon Mexico-specific
    ("halcones se solicitan", 0.85, "cartel_jerga", "halcon=vigilante en cartel"),
    ("puchador para el barrio", 0.85, "cartel_jerga", "puchador=vendedor menudeo droga"),
    ("puntero del barrio", 0.8, "cartel_jerga", "puntero=vigilante del cartel"),
    ("estaca en el punto", 0.8, "cartel_jerga", "estaca=puesto de vigilancia narco"),
    ("eres bueno para el jale", 0.75, "cartel_jerga", "jale=trabajo, halago previo"),
    ("le entras al jale", 0.85, "cartel_jerga", "entrar al jale=aceptar trabajo criminal"),
    ("te metes con la firma", 0.85, "cartel_jerga", "firma=cartel, comprometerse"),
    # Grooming / age
    ("eres muy maduro para tu edad", 0.9, "grooming_edad", "grooming clasico online"),
    ("te ves mayor", 0.85, "grooming_edad", "normalizacion edad menor"),
    ("cuantos anos tienes en realidad", 0.8, "grooming_edad", "sondaje edad para grooming"),
    ("no importa la edad", 0.8, "grooming_edad", "desestimar diferencia edad"),
    ("en otros paises esto es normal", 0.8, "normalizacion", "desculpabilizar acto ilegal"),
    # Roblox / Discord topology
    ("te paso robux", 0.85, "roblox_grooming", "gift virtual cebo grooming"),
    ("te regalo robux", 0.85, "roblox_grooming", "gift virtual cebo grooming"),
    ("robux gratis si me das", 0.95, "roblox_grooming", "quid pro quo virtual coin"),
    ("vamos a discord", 0.7, "cambio_canal", "cambio plataforma menos vigilada"),
    ("hablemos en discord", 0.7, "cambio_canal", "cambio plataforma menos vigilada"),
]

PHASE2_NEW = [
    ("pasate a discord para hablar sin filtros", 0.85, "aislamiento_plataforma", "cambio canal sin moderacion"),
    ("aqui nadie nos ve", 0.85, "aislamiento_privacidad", "falsa promesa privacidad"),
    ("te paso robux si me mandas foto", 0.95, "roblox_grooming", "quid pro quo CSAM"),
    ("vamos a snapchat que se borra", 0.85, "aislamiento_efimero", "busqueda canal efimero para evidencia"),
    ("vamos a snap que desaparece", 0.85, "aislamiento_efimero", "busqueda canal efimero"),
    ("manda en privado que aqui no", 0.8, "aislamiento_canal", "cambio canal mas privado"),
    ("dame tu ubicacion en vivo", 0.85, "recopilacion_ubicacion", "preludio levantamiento o coercion"),
    ("mandame ubicacion exacta", 0.85, "recopilacion_ubicacion", "ubicacion fina"),
    ("cual es el nombre de tu escuela", 0.85, "recopilacion_pii", "mapeo vulnerabilidad horario"),
    ("en que escuela vas", 0.85, "recopilacion_pii", "mapeo escuela menor"),
    ("cual es la direccion de tu casa", 0.95, "recopilacion_pii", "pre-requisito levantamiento"),
    ("donde queda tu casa", 0.9, "recopilacion_pii", "mapeo direccion menor"),
    ("mandame foto de la fachada", 0.95, "recopilacion_pii", "verificar direccion para coercion"),
    ("me dijeron que pasara a snapchat", 0.85, "cambio_canal_recibido", "recepcion: cambio canal efimero"),
    ("me agregaron a un grupo raro", 0.75, "recepcion_grupo", "anadido a grupo desconocido"),
    ("le digo a mis papas que viajo", 0.8, "aislamiento_mentira", "engano a familia para coercion"),
    ("me dijeron que no contara del viaje", 0.85, "secrecia_viaje", "pacto secreto viaje sospechoso"),
]

PHASE3_NEW = [
    # Sextortion threats — aggressor speech
    ("si no mandas mas voy a publicar", 0.95, "sextorsion_amenaza", "amenaza divulgacion"),
    ("si no continuas mando las fotos", 0.95, "sextorsion_amenaza", "amenaza divulgacion CSAM"),
    ("si no me mandas otra foto las publico", 0.95, "sextorsion_amenaza", "amenaza divulgacion CSAM"),
    ("voy a mostrar tus fotos a tu mama", 0.95, "sextorsion_familia", "amenaza divulgacion familiar"),
    ("voy a mostrarle a tu papa", 0.95, "sextorsion_familia", "amenaza divulgacion familiar"),
    ("lo subo a tu escuela", 0.95, "sextorsion_escuela", "amenaza divulgacion escolar"),
    ("lo subo al chat de tu salon", 0.95, "sextorsion_escuela", "amenaza divulgacion grupo escolar"),
    ("tengo screenshots de todo", 0.85, "sextorsion_evidencia", "retencion evidencia coercitiva"),
    ("tengo tus capturas", 0.85, "sextorsion_evidencia", "retencion evidencia coercitiva"),
    ("te voy a publicar en porno", 0.95, "sextorsion_publicacion", "amenaza distribucion porno"),
    ("te subo a paginas porno", 0.95, "sextorsion_publicacion", "amenaza distribucion porno"),
    ("si no pagas mando las fotos", 0.95, "sextorsion_chantaje", "extorsion economica con fotos"),
    ("si no pagas mando los videos", 0.95, "sextorsion_chantaje", "extorsion economica con videos"),
    # Sextortion — reception (victim describes)
    ("me piden fotos intimas amenazandome", 0.95, "sextorsion_recibida", "recepcion sextorsion activa"),
    ("me amenazan con publicar fotos", 0.95, "sextorsion_recibida", "recepcion amenaza divulgacion"),
    ("me piden mandar nudes", 0.9, "sextorsion_recibida", "recepcion exigencia CSAM"),
    ("me ofrecen dinero por nudes", 0.9, "sextorsion_comercial", "comercializacion CSAM"),
    ("me ofrecen lana por fotos", 0.9, "sextorsion_comercial", "comercializacion CSAM jerga"),
    ("me dijeron que mande fotos sin ropa", 0.95, "sextorsion_recibida", "exigencia recibida"),
    ("me dicen que si no mando me publican", 0.95, "sextorsion_recibida", "recepcion chantaje"),
    ("me amenazaron con mostrar mis fotos", 0.95, "sextorsion_recibida", "recepcion amenaza divulgacion"),
    ("me piden videos intimos", 0.95, "sextorsion_recibida", "recepcion exigencia video"),
    ("me piden video llamada sin ropa", 0.95, "sextorsion_video", "sextorsion en vivo"),
    # Cartel coercion reception
    ("me dijeron que ya sabia mucho", 0.9, "amenaza_silencio_recibida", "recepcion amenaza por conocimiento"),
    ("me amenazaron si hablo", 0.95, "amenaza_silencio_recibida", "recepcion amenaza silencio"),
    ("me amenazaron de muerte si cuento", 0.95, "amenaza_silencio_recibida", "recepcion amenaza muerte por delacion"),
    ("me dijeron que no podia salirme", 0.9, "coercion_no_salida", "imposibilidad de salida criminal"),
    ("me tienen vigilado", 0.85, "coercion_vigilancia", "estado de vigilancia activa"),
    ("saben donde vivo", 0.85, "coercion_vigilancia_recibida", "recepcion vigilancia"),
    ("saben donde estudio", 0.85, "coercion_vigilancia_recibida", "recepcion vigilancia escolar"),
]

PHASE4_NEW = [
    ("graba videos sin que sepan", 0.95, "sextorsion_operacion", "orden creacion CSAM clandestino"),
    ("graba a tus amigas", 0.95, "sextorsion_operacion", "orden CSAM amistades"),
    ("saca nudes a chicas", 0.95, "sextorsion_operacion", "orden creacion CSAM"),
    ("sextorsiona a perfiles que veas", 0.95, "sextorsion_reclutamiento", "reclutar como sextorsionador"),
    ("cobramos 50 50 de lo que saques", 0.85, "sextorsion_estructura", "comision sextortion network"),
    ("cobras la mitad de lo que saques", 0.85, "sextorsion_estructura", "comision sextortion network"),
    ("haces deepfakes y vendemos", 0.95, "csam_operacion", "creacion de deepfakes pornograficos"),
    ("manda fotos para hacer deepfake", 0.95, "csam_deepfake", "recolectar caras para deepfake"),
    ("vamos al rancho ya", 0.85, "recruit_op", "orden traslado a base operativa"),
    ("subete al carro", 0.85, "recruit_op", "orden traslado de campo"),
    ("llevate la troca", 0.85, "recruit_op", "orden uso vehiculo de cartel"),
    ("hay que limpiar el punto", 0.85, "recruit_op", "orden remover testigos en puesto"),
    ("hay que callar al cuervo", 0.95, "amenaza_operacion", "jerga: silenciar persona"),
    ("le sacas el alma", 0.95, "amenaza_operacion", "jerga matar a alguien"),
    ("aqui te pasamos las dosis", 0.85, "venta_droga_op", "instruccion venta droga"),
    ("cobras x dosis vendida", 0.8, "venta_droga_op", "estructura comision dosis"),
    ("te toca vender en la prepa", 0.95, "venta_droga_op", "orden venta en escuela"),
    ("te toca cobrar piso a vendedores", 0.9, "extorsion_op", "orden cobro piso a comerciantes"),
]


def patch(phase_num, fname, new_patterns):
    path = KW / fname
    data = json.loads(path.read_text(encoding="utf-8"))
    patterns = data["patterns"]
    existing = {p["pattern"].lower() for p in patterns}
    next_id = max(int(p["id"].split("_")[1]) for p in patterns) + 1
    added = 0
    for pat, weight, cat, expl in new_patterns:
        if pat.lower() in existing:
            continue
        patterns.append({
            "id": f"f{phase_num}_{next_id:03d}",
            "pattern": pat,
            "weight": weight,
            "regex": False,
            "category": cat,
            "explanation": expl,
            "source": "audit_round1_2026_04_25",
            "type": "audit_gap_fill",
            "signal_base": weight,
            "confidence": "alta",
            "_source_origin": "resilience_audit",
        })
        next_id += 1
        added += 1
    data["patterns"] = patterns
    data["updated_at"] = "2026-04-25T15:00:00Z"
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
