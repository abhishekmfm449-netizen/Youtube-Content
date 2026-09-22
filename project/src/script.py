"""The narration script and scene map.

`text` is the exact supplied voiceover wording and is never altered - it is what
gets burned into the captions and the .srt.  `speak` exists only because the TTS
front-end mispronounces the stylised capitalisation of "Vayu UTtaM"; it changes
spelling for the synthesiser, never wording.  When a real human voiceover is
dropped into assets/voiceover/ the `speak` field is ignored entirely.
"""

# lead_in  - beat of silence before the line, in seconds
# scene    - which visual scene this line drives
LINES = [
    dict(
        scene=1,
        lead_in=0.35,
        text="What if India could track every drone flying through its airspace?",
        speak="What if India could track every drone flying through its airspace?",
    ),
    dict(
        scene=2,
        lead_in=0.45,
        text="The Indian Air Force has demonstrated a new indigenous system called... Vayu UTtaM.",
        speak="The Indian Air Force has demonstrated a new indigenous system called... Vaayu Uttam.",
    ),
    dict(
        scene=3,
        lead_in=0.40,
        text="It was showcased during Dronathon 2026, at Pokhran, Rajasthan.",
        speak="It was showcased during Dronathon twenty twenty six, at Pokh-ran, Rajasthan.",
    ),
    dict(
        scene=4,
        lead_in=0.45,
        text="So... what does it actually do?",
        speak="So... what does it actually do?",
    ),
    dict(
        scene=5,
        lead_in=0.35,
        text="Vayu UTtaM is an Unmanned Traffic Management system, designed to detect and track "
             "both military and civilian drones, in real time.",
        speak="Vaayu Uttam is an Unmanned Traffic Management system, designed to detect and track "
              "both military and civilian drones, in real time.",
    ),
    dict(
        scene=6,
        lead_in=0.45,
        text="And here's where it gets interesting.",
        speak="And here's where it gets interesting.",
    ),
    dict(
        scene=7,
        lead_in=0.35,
        text="As the number of drones in the sky keeps increasing, it becomes harder to know "
             "which drone is authorised...",
        speak="As the number of drones in the sky keeps increasing, it becomes harder to know "
              "which drone is authorised...",
    ),
    dict(
        scene=8,
        lead_in=0.25,
        text="and which one could be a potential threat.",
        speak="and which one could be a potential threat.",
    ),
    dict(
        scene=9,
        lead_in=0.50,
        text="Vayu UTtaM is designed to help manage this increasingly crowded airspace, and "
             "support the identification of unauthorised or rogue drones.",
        speak="Vaayu Uttam is designed to help manage this increasingly crowded airspace, and "
              "support the identification of unauthorised or rogue drones.",
    ),
    dict(
        scene=10,
        lead_in=0.45,
        text="The system could potentially have applications beyond the military too...",
        speak="The system could potentially have applications beyond the military too...",
    ),
    dict(
        scene=11,
        lead_in=0.25,
        text="including civil aviation, critical infrastructure, and public safety.",
        speak="including civil aviation, critical infrastructure, and public safety.",
    ),
    dict(
        scene=12,
        lead_in=0.50,
        text="And this is just one of the technologies India showcased at Dronathon 2026.",
        speak="And this is just one of the technologies India showcased at Dronathon twenty twenty six.",
    ),
    dict(
        scene=13,
        lead_in=0.45,
        text="The future of airspace may not just be about fighter jets...",
        speak="The future of airspace may not just be about fighter jets...",
    ),
    dict(
        scene=14,
        lead_in=0.30,
        text="but also about who controls the drones in the sky.",
        speak="but also about who controls the drones in the sky.",
    ),
]

TAIL = 1.8  # seconds of held end card after the last word

# Words that get caption emphasis, matched case-insensitively as phrases.
EMPHASIS = [
    "Vayu UTtaM",
    "Dronathon 2026",
    "Indian Air Force",
    "Pokhran",
    "Unmanned Traffic Management",
    "military",
    "civilian drones",
    "real time",
    "authorised",
    "potential threat",
    "rogue drones",
    "civil aviation",
    "critical infrastructure",
    "public safety",
    "fighter jets",
]
