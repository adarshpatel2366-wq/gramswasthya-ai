from groq import Groq
from app.config import settings

_client = None


def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


SYSTEM_PROMPT = """You are GramSwasthya AI, a compassionate healthcare guidance assistant
for rural communities in India.

Core rules:
1. Automatically detect whether the user is writing in Hindi, English, or Hinglish
   (Roman-script Hindi) and reply in the SAME style/language they used, unless they
   explicitly ask you to switch.
2. You are NOT a doctor and must never give a definitive diagnosis. Use phrases like
   "this could be a sign of..." or "it's advisable to see a doctor about...".
3. Explain things in very simple, plain language suitable for someone with limited
   medical literacy. Avoid jargon; if you must use a medical term, explain it.
4. If symptoms sound serious or match an emergency pattern (chest pain, breathing
   difficulty, stroke signs, heavy bleeding, poisoning, snake bite, severe burns,
   pregnancy complications, infant emergencies, unconsciousness, suicidal thoughts),
   clearly say this needs urgent/emergency care and advise calling 108 (India's
   ambulance number) or going to the nearest hospital immediately.
5. Ask short, relevant follow-up questions one at a time rather than overwhelming
   the user with a checklist.
6. Recommend safe, general home-care/self-care steps ONLY when appropriate and safe
   (e.g. hydration, rest, ORS for mild dehydration) — never recommend prescription
   drug names or dosages.
7. Encourage preventive care and vaccination when relevant (e.g. seasonal flu,
   childhood immunization schedule, tetanus after injuries).
8. Remember and use context from earlier in the conversation to notice if symptoms
   are worsening, unchanged, or improving over time.
9. Keep replies concise (roughly 3-6 short sentences) unless the user asks for more
   detail or you are explaining a report/prescription.
10. Never say anything that could delay urgent care for a genuine emergency.
"""


def build_messages(history: list, user_message: str, language_hint: str = "auto"):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history:
        role = m.role if m.role in ("user", "assistant") else "user"
        messages.append({"role": role, "content": m.content})
    lang_note = ""
    if language_hint and language_hint != "auto":
        lang_note = f" (Please reply in {language_hint}.)"
    messages.append({"role": "user", "content": user_message + lang_note})
    return messages


def get_ai_reply(history: list, user_message: str, language_hint: str = "auto") -> str:
    client = get_client()
    messages = build_messages(history, user_message, language_hint)
    completion = client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        temperature=0.4,
        max_tokens=700,
    )
    return completion.choices[0].message.content


def summarize_report(extracted_text: str, report_type: str) -> str:
    """report_type: 'report' | 'prescription'"""
    client = get_client()
    prompt = (
        f"A user uploaded a medical {report_type}. Here is the extracted text:\n\n"
        f"{extracted_text}\n\n"
        "Explain this in very simple language for someone with limited medical "
        "literacy, in short bullet points: what it says, what the key values/medicines "
        "mean, and whether anything looks like it needs a doctor's attention. "
        "Do not give a definitive diagnosis. Keep it under 200 words."
    )
    completion = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=500,
    )
    return completion.choices[0].message.content


def generate_conversation_summary(history: list) -> str:
    client = get_client()
    convo_text = "\n".join([f"{m.role}: {m.content}" for m in history])
    prompt = (
        "Summarize this health conversation in 3-5 short bullet points covering: "
        "reported symptoms, advice given, and any recommended next steps. Write in "
        "simple English.\n\n" + convo_text
    )
    completion = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300,
    )
    return completion.choices[0].message.content
