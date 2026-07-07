"""Rule-based fallback engine for StadiumIQ.

Guarantees 100% availability by matching common fan questions with
vetted response templates. Supports translations across 9 languages.
"""

from __future__ import annotations

import re

from app.models import AssistantResponse, FanAssistantQuery, Language, SuggestedAction

# Multilingual map for fallback answers
FALLBACK_ANSWERS: dict[Language, dict[str, str]] = {
    Language.EN: {
        "restroom": "Accessible restrooms are available on all main concourses, specifically near Sections 2, 4, 6, and 8.",
        "medical": "The Main Medical Center is located near Section 1. In case of immediate emergency, please alert the nearest stadium steward.",
        "transit": "The main Transit Hub is located just outside the North Gate, offering express metro line and shuttle access.",
        "sustainability": "StadiumIQ promotes sustainability! Use the smart waste bins located throughout the concourses to sort compost, recycling, and landfill.",
        "general": "Welcome to the FIFA World Cup 2026 venue. Please let us know if you need directions, facility information, or support.",
    },
    Language.ES: {
        "restroom": "Los baños accesibles están disponibles en todos los pasillos principales, específicamente cerca de las Secciones 2, 4, 6 y 8.",
        "medical": "El Centro Médico Principal está ubicado cerca de la Sección 1. En caso de emergencia inmediata, avise al personal del estadio más cercano.",
        "transit": "El centro de tránsito principal está ubicado justo fuera de la Puerta Norte, ofreciendo acceso al metro y transbordadores.",
        "sustainability": "¡StadiumIQ promueve la sostenibilidad! Utilice los contenedores inteligentes ubicados en los pasillos para clasificar sus residuos.",
        "general": "Bienvenido al estadio de la Copa Mundial de la FIFA 2026. Por favor, díganos si necesita direcciones, información de instalaciones o ayuda.",
    },
    Language.FR: {
        "restroom": "Des toilettes accessibles sont disponibles dans tous les halls principaux, notamment à proximité des sections 2, 4, 6 et 8.",
        "medical": "Le centre médical principal est situé près de la section 1. En cas d'urgence immédiate, veuillez alerter l'agent du stade le plus proche.",
        "transit": "Le pôle de transport principal est situé juste à l'extérieur de la porte Nord, offrant un accès au métro express et aux navettes.",
        "sustainability": "StadiumIQ encourage la durabilité ! Utilisez les bacs de tri situés dans les halls pour trier le compost et le recyclage.",
        "general": "Bienvenue au site de la Coupe du Monde de la FIFA 2026. Veuillez nous faire savoir si vous avez besoin d'itinéraires ou d'aide.",
    },
}

# Fill remaining languages with English fallback to guarantee coverage
for lang in Language:
    if lang not in FALLBACK_ANSWERS:
        FALLBACK_ANSWERS[lang] = FALLBACK_ANSWERS[Language.EN]


def get_rule_based_assistance(query: FanAssistantQuery) -> AssistantResponse:
    """Provide structured response matching simple regex categories.

    Always returns a valid AssistantResponse object, ensuring
    graceful degradation.
    """
    text = query.question.lower()
    lang = query.language

    # Categorization based on simple keyword matches
    category = "general"
    suggested = []
    zone_ref = None

    if re.search(r"(restroom|toilet|ba[ñn]os?|toilette|wc)", text, re.IGNORECASE | re.UNICODE):
        category = "restroom"
        suggested = [
            SuggestedAction(action="find_nearest", details="Navigate to the nearest accessible restroom"),
            SuggestedAction(action="accessibility_options", details="View all accessible amenities"),
        ]
        zone_ref = "restroom_north"

    elif re.search(r"\b(medical|doctor|hospital|injury|hurt|médico|médica|aide)\b", text):
        category = "medical"
        suggested = [
            SuggestedAction(action="find_nearest", details="Show directions to Main Medical Center"),
            SuggestedAction(action="alert_steward", details="Notify stadium emergency contact"),
        ]
        zone_ref = "medical_main"

    elif re.search(r"(transit|metro|bus|shuttle|train|taxi|rideshare|transporte?)", text, re.IGNORECASE | re.UNICODE):
        category = "transit"
        suggested = [
            SuggestedAction(action="transit_schedule", details="View live departure boards"),
            SuggestedAction(action="find_accessible_shuttle", details="Request an accessible shuttle seat"),
        ]
        zone_ref = "transit_hub"

    elif re.search(r"\b(sustainability|recycle|waste|bin|trash|co2|carbon|carbono|vert|déchets)\b", text):
        category = "sustainability"
        suggested = [
            SuggestedAction(action="eco_dashboard", details="View matchday sustainability impact"),
        ]
        zone_ref = "concourse_north"

    else:
        suggested = [
            SuggestedAction(action="view_map", details="Show stadium zone interactive map"),
            SuggestedAction(action="transport_options", details="View stadium egress transit guidance"),
        ]

    answer = FALLBACK_ANSWERS[lang].get(category, FALLBACK_ANSWERS[Language.EN]["general"])

    return AssistantResponse(
        answer=answer,
        suggested_actions=suggested,
        zone_reference=zone_ref,
        confidence=0.8,
        source="rules",
        language=lang,
    )
