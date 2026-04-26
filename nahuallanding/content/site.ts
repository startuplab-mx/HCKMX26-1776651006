export type MetricCard = {
  value: number;
  suffix: string;
  label: string;
  detail: string;
};

export type SurveyHighlight = {
  title: string;
  value: string;
  description: string;
};

export type PhaseCard = {
  id: string;
  title: string;
  accent: string;
  weight: string;
  summary: string;
  patterns: string[];
  source: string;
  badge?: string;
};

export type SourceLink = {
  label: string;
  href: string;
  note: string;
};

export type ArchitectureNode = {
  id: string;
  title: string;
  subtitle: string;
  detail: string;
  x: number;
  y: number;
  w: number;
  h: number;
};

export type ArchitectureEdge = {
  from: string;
  to: string;
};

export type AdvancedFeature = {
  id: string;
  title: string;
  icon: "mic" | "activity" | "shield" | "scale";
  description: string;
};

export type PlainTechItem = {
  id: string;
  title: string;
  /** Plain-Spanish explanation of what the user/operator gains. */
  layman: string;
  /** Hands-on technical detail for engineers (file paths, primitives).
   *  Optional — some items are pure UX/legal and don't have a stack
   *  trace to attach. The card hides the toggle when this is absent. */
  technical?: string;
};

export const site = {
  name: "Nahual",
  repoUrl: "https://github.com/cocopsn/nahuallanding-demo",
  description:
    "Sistema de detección de reclutamiento criminal digital para menores en México. Bot de WhatsApp, extensión de monitoreo y análisis modular para alertas tempranas.",
  badge:
    "Hackathon 404: Threat Not Found 2026 | Embajada de EE.UU. × StartupLab MX",
  heroLabel: "Sistema de Detección de Reclutamiento Criminal Digital",
  heroTitle: "NAHUAL",
  heroTagline: "Detecta manipulación digital antes de que escale a daño real",
  heroCopy:
    "Bot de WhatsApp, extensión de monitoreo y clasificador de riesgo para detectar captación criminal en conversaciones digitales antes de que el daño escale.",
  heroMetrics: [
    {
      value: 92.2,
      suffix: "%",
      label: "usarían o considerarían usar Nahual",
      detail: "Encuesta propia Nahual · n=129 · 24 de abril de 2026"
    },
    {
      value: 45.7,
      suffix: "%",
      label: "reportó al menos una señal de riesgo digital",
      detail: "Encuesta propia Nahual · jóvenes participantes del hackathon"
    },
    {
      value: 73.6,
      suffix: "%",
      label: "asocia confianza con privacidad de datos",
      detail: "Insight que define el diseño privacy-first del producto"
    }
  ] satisfies MetricCard[],
  signalTape: [
    "ONC + REDIM estiman entre 145 mil y 250 mil niñas, niños y adolescentes en riesgo de reclutamiento o utilización delictiva en México.",
    "El Seminario sobre Violencia y Paz de El Colegio de México documentó una muestra de 100 cuentas de TikTok vinculadas con reclutamiento y propaganda criminal.",
    "FBI y HSI reportaron más de 13 mil casos de sextorsión financiera de menores entre octubre de 2021 y marzo de 2023."
  ],
  problemNarrative: [
    "El 5 de marzo de 2025, el caso del Rancho Izaguirre en Teuchitlán, Jalisco, volvió visible una cadena que ya se estaba incubando en línea: captación, traslado, coerción y explotación de jóvenes.",
    "El Seminario sobre Violencia y Paz de El Colegio de México documentó el uso de TikTok para ofrecer pagos, entrenamiento, hospedaje, símbolos de facciones criminales y promesas de pertenencia.",
    "El 4 de marzo de 2026, la Cámara de Diputados aprobó una minuta para agravar el artículo 201 del Código Penal Federal con penas de 10 a 20 años cuando niñas, niños y adolescentes sean involucrados en delincuencia organizada; el Senado recibió esa minuta el 10 de marzo de 2026.",
    "El vacío sigue estando antes de la desaparición: casi no existen herramientas preventivas para detectar señales de reclutamiento digital en el momento en que aparecen."
  ],
  pipeline: [
    {
      title: "Captación",
      accent: "var(--green)",
      description: "Promesas de dinero, estatus, protección o pertenencia.",
      example: "$15,000 por semana · te pago el viaje"
    },
    {
      title: "Enganche",
      accent: "var(--yellow)",
      description: "Cambio de plataforma, secreto, solicitud de datos y aislamiento.",
      example: "Pásate a Telegram · no le digas a nadie"
    },
    {
      title: "Coerción",
      accent: "var(--cobre-light)",
      description: "Amenazas, presión de tiempo y control de la conversación.",
      example: "Contesta ya · te vamos a buscar"
    },
    {
      title: "Explotación",
      accent: "var(--red)",
      description: "Traslado, sextorsión, cobros, tareas ilícitas o violencia.",
      example: "Ve al punto · manda fotos · deposita"
    }
  ],
  validationHighlights: [
    {
      title: "Riesgo real",
      value: "59 de 129",
      description:
        "jóvenes reportaron haber vivido al menos una señal compatible con captación, persuasión, cambio de plataforma o presión digital."
    },
    {
      title: "Adopción",
      value: "93.2%",
      description:
        "de quienes sí reportaron alguna señal usarían o considerarían usar una herramienta como Nahual."
    },
    {
      title: "Diseño de confianza",
      value: "62.0%",
      description:
        "prefiere ver primero el resultado por sí mismo; la notificación a un adulto debe ser opcional, no automática."
    }
  ] satisfies SurveyHighlight[],
  privacyBars: [
    { label: "Privacidad sobre tus datos", value: 73.6 },
    { label: "Precisión en el resultado", value: 14.0 },
    { label: "Rapidez en responder", value: 7.0 },
    { label: "Anonimato del resultado", value: 5.4 }
  ],
  controlPreference: [
    { label: "Solo yo veo el resultado", value: 62.0 },
    { label: "Ambas opciones", value: 29.5 },
    { label: "Notificar a un adulto", value: 8.5 }
  ],
  architectureNodes: [
    {
      id: "bot",
      title: "Bot WhatsApp",
      subtitle: "Canal reactivo",
      detail:
        "Recibe mensajes sospechosos, clasifica riesgo, responde en lenguaje claro y permite escalar a un adulto o generar evidencia. Live en +52 844 538 7404.",
      x: 28,
      y: 52,
      w: 160,
      h: 52
    },
    {
      id: "backend",
      title: "Backend FastAPI",
      subtitle: "Orquestación",
      detail:
        "Normaliza entradas, corre 4 capas cognitivas, registra eventos y coordina generación de reportes y panel.",
      x: 258,
      y: 48,
      w: 176,
      h: 60
    },
    {
      id: "extension",
      title: "Nahual Shield",
      subtitle: "Modo proactivo",
      detail:
        "Observa texto visible en WA Web / IG / Discord / Roblox. URL allowlist + whitelist + scope al chat container para evitar falsos positivos.",
      x: 510,
      y: 52,
      w: 170,
      h: 52
    },
    {
      id: "classifier",
      title: "Clasificador",
      subtitle: "4 capas cognitivas",
      detail:
        "Heurístico → Bayesiano → LLM → Trayectoria. Cada capa aporta señal independiente con merge ponderado y override en alto riesgo.",
      x: 288,
      y: 170,
      w: 116,
      h: 52
    },
    {
      id: "heuristic",
      title: "Heurístico",
      subtitle: "900 patrones",
      detail:
        "Regex + categorías ponderadas por fase. Normalización avanzada (chat MX, dígitos escritos, typos). 487 patrones de alta confianza.",
      x: 76,
      y: 274,
      w: 128,
      h: 52
    },
    {
      id: "bayesian",
      title: "Bayesiano",
      subtitle: "Capa 1.5 · 1031 docs",
      detail:
        "Naive Bayes con n-gramas (1,2,3) que aprende de cada feedback. Aporta señal complementaria sin reemplazar al heurístico.",
      x: 220,
      y: 274,
      w: 128,
      h: 52
    },
    {
      id: "claude",
      title: "Sonnet 4.5",
      subtitle: "Análisis contextual",
      detail:
        "Activa en zona gris (0.3-0.6), score=0+keywords o texto>30 chars. Razonamiento en lenguaje natural sobre contexto sutil.",
      x: 364,
      y: 274,
      w: 128,
      h: 52
    },
    {
      id: "trajectory",
      title: "Trayectoria",
      subtitle: "EscalationDetector",
      detail:
        "Rastrea evolución de riesgo entre mensajes de una misma sesión. Override automático cuando el riesgo escala rápido o cambia de fase.",
      x: 508,
      y: 274,
      w: 128,
      h: 52
    },
    {
      id: "sqlite",
      title: "SQLite",
      subtitle: "Persistencia",
      detail:
        "WAL + retry on lock + atomic writes. Solo SHA-256 + resumen anonimizado — nunca el texto original.",
      x: 112,
      y: 396,
      w: 114,
      h: 52
    },
    {
      id: "pdf",
      title: "PDF Forense",
      subtitle: "Cadena de evidencia",
      detail:
        "Reporte oficial con folio NAH-2026-XXXX, marco legal mexicano (LGDNNA, CPF 209 Sextus, Ley Olimpia), autoridades y derechos.",
      x: 290,
      y: 396,
      w: 108,
      h: 52
    },
    {
      id: "panel",
      title: "Panel Web",
      subtitle: "Live · 159.223.187.6",
      detail:
        "Dashboard con auto-refresh, manual analyze textbox, deep healthcheck, PELIGRO toast, alertas filtrables, exportación CSV.",
      x: 468,
      y: 396,
      w: 118,
      h: 52
    }
  ] satisfies ArchitectureNode[],
  architectureEdges: [
    { from: "bot", to: "backend" },
    { from: "extension", to: "backend" },
    { from: "backend", to: "classifier" },
    { from: "classifier", to: "heuristic" },
    { from: "classifier", to: "bayesian" },
    { from: "classifier", to: "claude" },
    { from: "classifier", to: "trajectory" },
    { from: "heuristic", to: "sqlite" },
    { from: "claude", to: "pdf" },
    { from: "trajectory", to: "panel" },
    { from: "backend", to: "panel" }
  ] satisfies ArchitectureEdge[],
  techStack: [
    "Next.js 14",
    "TypeScript",
    "Tailwind CSS",
    "Framer Motion",
    "Node.js 20",
    "Baileys 6.7",
    "Python 3.12",
    "FastAPI",
    "SQLite + WAL",
    "ReportLab",
    "Manifest V3",
    "Claude Sonnet 4.5",
    "Naive Bayes",
    "Whisper-large-v3",
    "Nginx",
    "DigitalOcean"
  ],
  classifierPhases: [
    {
      id: "captacion",
      title: "CAPTACIÓN",
      accent: "var(--green)",
      weight: "15%",
      summary: "Ofertas falsas, narcocultura, glorificación criminal y víctimas reportando \"me ofrecieron…\".",
      patterns: [
        "te pago $15,000 semanales",
        "me ofrecieron jale en TikTok",
        "se solicita gente para la mana",
      ],
      source: "Colmex · Infobae · Proceso · 299 patrones"
    },
    {
      id: "enganche",
      title: "ENGANCHE",
      accent: "var(--yellow)",
      weight: "25%",
      summary: "Extracción de datos, cambio de canal, secrecía y confianza artificial — desde aggresor y víctima.",
      patterns: [
        "pásate a Telegram, no le digas",
        "me pidieron mi ubicación",
        "vamos a Snapchat que se borra",
      ],
      source: "Colmex · evidencia de campo · 192 patrones"
    },
    {
      id: "coercion",
      title: "COERCIÓN",
      accent: "var(--cobre-light)",
      weight: "35%",
      summary: "Amenazas directas + recibidas (\"me van a matar\"), distress, vigilancia, stalking.",
      patterns: [
        "te voy a matar",
        "me amenazaron de muerte",
        "saben dónde vivo",
      ],
      source: "FBI · sobrevivientes · 236 patrones",
      badge: "OVERRIDE: score ≥ 0.80 → peligro inminente"
    },
    {
      id: "explotacion",
      title: "EXPLOTACIÓN",
      accent: "var(--red)",
      weight: "25%",
      summary: "Sextorsión (agresor + víctima), órdenes operativas narco, deepfakes CSAM, demanda financiera.",
      patterns: [
        "manda fotos o las publico",
        "me forzaron a vender",
        "tienes que levantar a alguien",
      ],
      source: "FBI · Ley Olimpia · CSAM · 173 patrones",
      badge: "OVERRIDE: score ≥ 0.80 → peligro inminente"
    }
  ] satisfies PhaseCard[],
  riskFormula: "risk_score = P1×0.15 + P2×0.25 + P3×0.35 + P4×0.25",
  riskScore: 0.87,
  botFlow: {
    question: "¿Recibiste un mensaje sospechoso?",
    safe: "SEGURO",
    warning: "ATENCIÓN",
    danger: "PELIGRO"
  },
  dashboardStats: [
    { label: "Total", value: "23" },
    { label: "Peligro", value: "5" },
    { label: "Atención", value: "11" },
    { label: "Seguro", value: "7" }
  ],
  dashboardRows: [
    {
      time: "24 Abr 2026 · 08:14",
      platform: "WhatsApp",
      level: "PELIGRO",
      score: "0.92",
      note: "Oferta de dinero + presión de traslado"
    },
    {
      time: "24 Abr 2026 · 08:21",
      platform: "Discord",
      level: "ATENCIÓN",
      score: "0.58",
      note: "Cambio de plataforma y secreto"
    },
    {
      time: "24 Abr 2026 · 08:33",
      platform: "Instagram",
      level: "SEGURO",
      score: "0.16",
      note: "Conversación sin marcadores de captación"
    }
  ],
  roadmap: [
    {
      phase: "Hackathon MVP",
      date: "Abril 2026",
      description: "Bot + clasificador + panel + extensión + PDF"
    },
    {
      phase: "Programa de Acompañamiento",
      date: "Mayo-Junio 2026",
      description: "8 semanas con StartupLab MX para validar despliegue y pilotos"
    },
    {
      phase: "Piloto Escolar",
      date: "Julio-Septiembre 2026",
      description: "Implementación en escuelas de Coahuila con protocolo de derivación"
    },
    {
      phase: "API Pública",
      date: "Octubre 2026",
      description: "Integración abierta para plataformas, observatorios y terceros"
    },
    {
      phase: "Expansión Nacional",
      date: "2027",
      description: "Ruta de escalamiento vía alianzas educativas e institucionales"
    }
  ],
  team: [
    {
      name: "Armando Flores",
      role: "Lead Developer",
      background: "ITC, Tecnológico de Monterrey",
      bio: [
        "Fundador de AUCTORUM, agencia de agentes IA de WhatsApp en producción.",
        "Perfil en ciberseguridad y automatización aplicada a riesgo digital juvenil."
      ],
      chips: ["Node.js", "Python", "FastAPI", "WhatsApp Bots", "Cybersecurity"]
    },
    {
      name: "Marco Espinosa",
      role: "Clinical Validation & UX",
      background: "Medicina, Universidad Autónoma de Coahuila",
      bio: [
        "Validación clínica del lenguaje del bot y protocolos de primer contacto.",
        "Traducción de riesgo digital a una experiencia usable, ética y accionable."
      ],
      chips: ["Clinical Psychology", "Legal Protocols", "UX Research", "Public Speaking"]
    }
  ],
  impactStats: [
    {
      value: 900,
      suffix: "",
      label: "patrones de detección en el clasificador",
      detail: "487 de alta confianza · 4 fases · victim + aggressor perspectives"
    },
    {
      value: 99.6,
      suffix: "%",
      label: "precisión en suite de validación de 240 frases",
      detail: "0 falsos negativos · 1 falso positivo · sin LLM · 4 iteraciones"
    },
    {
      value: 4,
      suffix: "",
      label: "capas cognitivas independientes",
      detail: "Heurístico · Naive Bayes (1031 docs) · Sonnet 4.5 · Trayectoria"
    },
    {
      value: 250,
      suffix: "k",
      label: "NNA en el extremo alto del rango de riesgo",
      detail: "Estimación ONC + REDIM en México"
    }
  ] satisfies MetricCard[],
  institutionBadges: [
    "Embajada de EE.UU. / INL",
    "StartupLab MX",
    "Tec de Monterrey",
    "UAdeC"
  ],
  sources: [
    {
      label: "ONC + REDIM",
      href: "https://onc.org.mx/public/onc_site/uploads/doc-reclutamiento.pdf",
      note:
        "Reporte sobre reclutamiento y utilización de niñas, niños y adolescentes; estimación entre 145 mil y 250 mil NNA en riesgo."
    },
    {
      label: "Seminario sobre Violencia y Paz · El Colegio de México",
      href: "https://violenciaypaz.colmex.mx/archivos/UHVibGljYWNpb24KIDExNQpkb2N1bWVudG8%3D/SVyP%20-%20TikTok%20reclutamiento%20-%20abril%202024.pdf",
      note:
        "Investigación sobre más de 100 cuentas activas en TikTok vinculadas con reclutamiento y propaganda criminal."
    },
    {
      label: "FBI · Sextortion: A Growing Threat Targeting Minors",
      href: "https://www.fbi.gov/news/press-releases/sextortion-a-growing-threat-targeting-minors",
      note:
        "Alerta del FBI sobre más de 13 mil reportes de sextorsión financiera de menores recibidos junto con HSI."
    },
    {
      label: "Cámara de Diputados · 4 de marzo de 2026",
      href: "https://cronica.diputados.gob.mx/Ve04mar2026.html",
      note:
        "Crónica parlamentaria de la aprobación de la minuta para agravar el artículo 201 del Código Penal Federal."
    },
    {
      label: "Senado de la República · 10 de marzo de 2026",
      href: "https://comunicacionsocial.senado.gob.mx/informacion/comunicados/14613-recibe-senado-minuta-para-imponer-hasta-20-anos-de-prision-a-quien-involucre-a-menores-en-delincuencia-organizada",
      note:
        "Recepción en el Senado de la minuta sobre sanciones de 10 a 20 años cuando menores sean involucrados en delincuencia organizada."
    }
  ] satisfies SourceLink[],
  advancedFeatures: [
    {
      id: "bayesian",
      title: "Capa Bayesiana que aprende del feedback",
      icon: "activity",
      description: "Naive Bayes con n-gramas (1, 2, 3) entrenado con 1031 ejemplos. Cada vez que un usuario confirma o niega una alerta, el modelo se re-entrena automáticamente — sin reentrenamiento batch ni GPU. Vocabulario de 6104 features, 5 clases balanceadas. Aporta el 20% del score final junto con el heurístico (50%) y el LLM (30%)."
    },
    {
      id: "privacy",
      title: "Data Anónima by Design",
      icon: "shield",
      description: "Construido bajo el Art. 16 de la Constitución. Nunca se almacena el texto original — solo el hash SHA-256 + un resumen anonimizado + los pattern_ids que matchearon. Cumplimiento LFPDPPP (datos personales) y LGDNNA (derechos de menores). Validación Pydantic con extra=\"forbid\" en cada endpoint."
    },
    {
      id: "multimedia",
      title: "OCR + STT con confirmación explícita",
      icon: "mic",
      description: "Pipeline para audios (Groq Whisper-large-v3) y capturas (Anthropic Claude Vision). El usuario debe confirmar el texto extraído antes del análisis — los bytes originales se descartan al instante. MIME normalization para formatos WhatsApp (audio/ogg; codecs=opus, image/jpeg;charset=binary)."
    },
    {
      id: "trayectory",
      title: "Trayectory Override & Memoria de Sesión",
      icon: "activity",
      description: "El abuso criminal es progresivo. El EscalationDetector rastrea velocidad de cambio + desviación + progresión de fase a través del ciclo de vida de una sesión. Si el perpetrador transita ATENCIÓN → ATENCIÓN → ATENCIÓN con velocity ≥ 0.20, dispara un PELIGRO por trayectoria antes de que llegue a override estático."
    },
    {
      id: "legal",
      title: "Trazabilidad Forense Automática",
      icon: "scale",
      description: "No solo predice riesgo; lo mapea legalmente. Cada fase referencia los artículos aplicables: LGDNNA (Art. 47, 101 Bis 2), CPF Art. 209 Sextus (propuesto), Ley Olimpia, LGAMVLV 20 Quáter, LGPSEDMTP 10. Compila un reporte PDF con folio NAH-2026-XXXX listo para abrir carpeta en Policía Cibernética 088."
    },
    {
      id: "hardening",
      title: "Hardening en producción (Apr 26)",
      icon: "shield",
      description: "9 olas de auditoría desplegadas a producción: webhooks firmados con HMAC-SHA256, magic-byte validation antes de Whisper/Vision, rate-limit anti-poisoning del auto-tuner (3/(IP, alert_id)/10min), ReDoS guard (cap 4000 chars + audit estático de patrones catastróficos), Bayesian persistence con tmp por-PID + fsync, life-safety FSM sin gating por estado, opt-out del notify que evita dead-ends, 4 taglines rotativos para SEGURO, panel API base auto-detect. 163/163 tests verde."
    }
  ] satisfies AdvancedFeature[],
  liveDemo: {
    panelUrl: "http://159.223.187.6/",
    swaggerUrl: "http://159.223.187.6/docs",
    botPhone: "+52 844 538 7404",
    botPhoneIntl: "5218445387404",
    waLink: "https://wa.me/5218445387404?text=Hola%20Nahual",
    note: "Sistema en producción 24/7. Mánda \"hola\" al número del bot para probar el flujo completo."
  },
  // "Cómo funciona por dentro" — explica capas técnicas en lenguaje
  // plano + ficha técnica para engineers. Cada item refleja una
  // ola de hardening real (commits 45a140d, b543ae5, 119b581, 4a3b100,
  // 7970804) que llegó a prod entre 25-26 abril 2026.
  plainTech: [
    {
      id: "override",
      title: "Detección de peligro inminente (Override)",
      layman:
        "Cuando un mensaje cruza una línea — una amenaza directa de muerte, una orden para enviar fotos íntimas — el sistema NO promedia con el resto de señales. Se dispara ALARMA inmediata aunque el resto del mensaje suene casual. Las víctimas no llegan al peligro paso a paso ordenado: a veces el agresor salta directo a la amenaza.",
      technical:
        "Si phase3 (coerción) o phase4 (explotación) individualmente alcanzan score ≥ 0.80 en `pipeline.py`, se ignora el promedio ponderado (P1×0.15 + P2×0.25 + P3×0.35 + P4×0.25) y se eleva risk_score a 1.0 con override_triggered=True. La regla es non-negotiable y testeada en tests/test_classifier.py."
    },
    {
      id: "four-layers",
      title: "Cuatro cerebros revisando el mismo mensaje",
      layman:
        "En vez de confiar en un solo modelo, Nahual pasa cada mensaje por cuatro filtros distintos que trabajan en paralelo: (1) un diccionario afinado con 900 frases reales del crimen organizado mexicano, (2) un modelo estadístico que aprende de cada feedback, (3) Claude (la IA de Anthropic) cuando hay duda contextual, y (4) un detector de patrones que rastrea si la conversación está escalando. Si tres de cuatro disienten, el panel lo muestra para que un humano decida.",
      technical:
        "Capa 0: override estático. Capa 1: HeuristicClassifier en classifier/heuristic.py — 900 regex compilados con normalización de chat MX (xq→porque, q→que, 15 mil → 15000), whitelist contextual, contextual_boost 1.30×/1.50× para combos peligrosos. Capa 1.5: NaiveBayesClassifier (n-gramas 1+2+3, smoothing Laplace, 1031 docs entrenados, vocab 6104). Capa 2: claude-sonnet-4-5-20250929 en zona gris (0.3-0.6) o cuando heur=0+texto>30 chars. Capa 3: EscalationDetector rastrea velocity + phase progression en sesión multi-mensaje. Merge: heur 50% + bayes 20% + LLM 30%."
    },
    {
      id: "privacy",
      title: "Nunca guardamos tu mensaje original",
      layman:
        "Lo que mandas se borra al instante. Solo conservamos un código irreversible (como una huella digital) y un resumen sin nombres ni datos personales. Si un día nos hackean — o un juez ordena entregar conversaciones — no hay nada que entregar. Tu privacidad no depende de prometerla, depende de que el sistema técnicamente no pueda traicionarla.",
      technical:
        "SHA-256 del texto + summary anonimizado + lista de pattern_ids que matchearon. Eso es TODO lo que se persiste en SQLite. Audio/imagen se reenvía a Groq Whisper / Anthropic Vision y el byte stream se descarta inmediatamente — no hay archivo intermedio en disco. El modelo Pydantic de /contribute usa `extra=\"forbid\"` que rechaza con HTTP 422 cualquier campo desconocido. Cumple Art. 16 CPEUM, LFPDPPP y LGDNNA."
    },
    {
      id: "webhook-hmac",
      title: "Avisos al adulto de confianza, criptográficamente firmados",
      layman:
        "Cuando el bot avisa a un papá/mamá/tutor, ese mensaje va con una firma criptográfica que solo nuestro servidor puede generar. Si alguien intercepta el aviso e intenta cambiarle el texto — o suplantar al sistema enviando un aviso falso — la firma deja de cuadrar y el receptor lo detecta. Es la misma tecnología que usan los bancos para no dejar que nadie modifique una transferencia en tránsito.",
      technical:
        "HMAC-SHA256 sobre el payload completo en webhooks.py: `X-Nahual-Signature: sha256=<hex>` + `X-Nahual-Signature-Algo: hmac-sha256`. Configurado vía NAHUAL_WEBHOOK_SECRET. Reemplaza el shared-secret estático que pasaba en plain text antes de Apr 26."
    },
    {
      id: "magic-bytes",
      title: "Verificamos que un audio sea audio (y no un virus disfrazado)",
      layman:
        "Antes de mandar tu audio o foto a la IA que lo procesa, miramos los primeros bytes del archivo y comparamos contra firmas conocidas. Un atacante podría renombrar un script de Python como \"audio.ogg\" y mandárnoslo esperando que lo reenviemos a Groq. Con esto, el sistema dice \"esto no huele a audio\" antes de que cualquier servicio externo lo toque.",
      technical:
        "_AUDIO_SIGNATURES y _IMAGE_SIGNATURES en main.py: cubre Ogg (`OggS`), MP3 (`ID3`/`FF FB`/`FF F3`), WAV (`RIFF...WAVE`), M4A (`ftyp`), WebM (`1A 45 DF A3`), FLAC (`fLaC`), PNG (`89 50 4E 47`), JPEG (`FF D8 FF`), GIF87a/89a, WebP (`RIFF...WEBP`). MIME normalization adicional para `audio/ogg; codecs=opus` y `image/jpeg;charset=binary` que WhatsApp manda."
    },
    {
      id: "feedback-rl",
      title: "Anti-envenenamiento del modelo que aprende",
      layman:
        "El sistema aprende: cada vez que un usuario dice \"esto NO era peligro\", el modelo se reentrena para no equivocarse igual la próxima. Pero un atacante podría hacer un script que mande 10,000 \"esto no era peligro\" sobre amenazas REALES para volver al sistema ciego. Detectamos esos patrones de spam y los bloqueamos: máximo 3 feedbacks por persona por alerta cada 10 minutos.",
      technical:
        "_feedback_rate_check() en main.py: sliding-window dict-of-deques con clave `(client_ip, alert_id)`. _client_ip() honra X-Forwarded-For solo cuando el peer inmediato es loopback (Nginx) — bloquea spoofing directo a uvicorn. 4ta submission devuelve 429 con header Retry-After. Audit log: `INFO: feedback id=X type=Y alert=Z ip=W ua=...`. Configurable vía FEEDBACK_RATE_LIMIT_MAX / FEEDBACK_RATE_WINDOW_S."
    },
    {
      id: "redos",
      title: "Mensajes gigantes no pueden colapsar el sistema",
      layman:
        "Hay un truco viejo de internet — un \"mensaje\" de 1 MB con un patrón malicioso puede congelar al servidor que lo analiza durante horas, dejando a todos los demás usuarios sin servicio. Cortamos cualquier mensaje a 4,000 caracteres antes de analizarlo (un WhatsApp normal cabe ahí) y revisamos automáticamente que ningún patrón de búsqueda nuevo tenga la forma peligrosa que causa congelamientos.",
      technical:
        "MAX_INPUT_CHARS=4000 capa input en `classify()` antes de los 900+ `re.search()`. _looks_redos_dangerous() audita cada patrón al compilar y descarta `(...+)+`, `(...*)*`, `(...|...)*`, `.+.+`. _MAX_TOKENS_PER_DOC=5000 en bayesian.py capa la generación de n-gramas (sin esto, un paste de 1 MB alocaría ~3M de strings y tira al worker)."
    },
    {
      id: "fsm-life-safety",
      title: "Si dices que necesitas ayuda, el bot escucha primero",
      layman:
        "Si en cualquier momento de la conversación el menor escribe \"me quiero morir\" o \"tengo miedo\" o \"necesito ayuda\", el bot pausa lo que esté haciendo y le ofrece la Línea de la Vida (800-911-2000) y el 088. Antes había un bug: si el menor estaba en el paso de \"dame el teléfono del adulto\" y escribía algo de crisis, el bot lo trataba como un teléfono inválido. Ahora es imposible que el menor quede atrapado.",
      technical:
        "DISTRESS_RE y SUPPORT_RE en bot/handlers/flowController.js fired ANTES del switch del current_step — sin gates por estado. Adicional: NO_GUARDIAN_RE matchea \"ahorita no\" / \"luego\" / \"sin tutor\" / \"primero el reporte\" en el state `notify`, evitando el dead-end donde cualquier mensaje no-teléfono daba \"Número no válido\". Bouncea a ask_contribute con notifyOptOut block (PDF + Línea de la Vida + 088 + invitación a contribuir)."
    },
    {
      id: "self-learning",
      title: "El sistema mejora con cada uso, sin reentrenamiento manual",
      layman:
        "Cada vez que tú o un operador del panel dicen \"sí, esto era peligro\" o \"no, falsa alarma\", el sistema ajusta automáticamente los pesos. No hay un científico de datos sentado reentrenando un modelo cada noche — el aprendizaje es continuo. En 24 horas de uso real, el sistema queda calibrado al lenguaje específico de tu región.",
      technical:
        "AutoTuner en classifier/precision.py ajusta weight overrides por pattern_id (clip [0.0, 1.5]) basado en ratio de confirms vs denies. NaiveBayesClassifier.train_one() corre en cada feedback (atomic-save cada 10 trains). Surrogate text: summary + reconstructed why-list (NO el original — privacy by design). Endpoint /precision/state expone qué patrones subieron/bajaron de peso."
    },
    {
      id: "legal-traceability",
      title: "Cada alerta lleva el marco legal mexicano que la respalda",
      layman:
        "Un PDF auto-generado por cada alerta. Trae el folio (NAH-2026-XXXX), los artículos del Código Penal Federal y la LGDNNA que aplican al caso, las autoridades a las que se debe escalar (088, FEVIMTRA, Comisión de Búsqueda) con sus teléfonos y horarios, los derechos de la víctima, y las acciones recomendadas paso a paso. La intención es que cuando un tutor lo lleva a Policía Cibernética, ya tiene la carpeta lista — no es \"ayuda, mi hijo recibió un mensaje raro\", es \"infracción al Art. 209 Sextus CPF, anexo evidencia\"."
    }
  ] satisfies PlainTechItem[]
};
