import base64
import time
from app.config import settings

# provider -> (api key, model, base url) for OpenAI-compatible APIs
OPENAI_COMPAT = {
    "openai": lambda: (settings.OPENAI_API_KEY, settings.OPENAI_MODEL, None),
    "groq": lambda: (settings.GROQ_API_KEY, settings.GROQ_MODEL, "https://api.groq.com/openai/v1"),
    "gemini": lambda: (
        settings.GEMINI_API_KEY,
        settings.GEMINI_MODEL,
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    ),
}

_models = {}      # (provider, json_mode) -> chat model
_cooldown = {}    # (provider, json_mode) -> time until which it is skipped
STATE = {"last_provider": None}


def provider_chain():
    """Providers in priority order. Cloud providers without a key are skipped."""
    chain = []
    for name in [p.strip().lower() for p in settings.LLM_PROVIDERS.split(",") if p.strip()]:
        if name == "ollama":
            chain.append(name)
        elif name in OPENAI_COMPAT and OPENAI_COMPAT[name]()[0]:
            chain.append(name)
    return chain or ["ollama"]


def _build(name: str, json_mode: bool):
    key = (name, json_mode)
    if key in _models:
        return _models[key]

    if name == "ollama":
        from langchain_ollama import ChatOllama

        model = ChatOllama(
            model=settings.LLM_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0,
            format="json" if json_mode else None,
        )
    else:
        from langchain_openai import ChatOpenAI

        api_key, model_name, base_url = OPENAI_COMPAT[name]()
        kwargs = {}
        reasoning = model_name.startswith(("gpt-5", "gpt-6", "o1", "o3", "o4"))
        if name == "groq" or (name == "openai" and not reasoning):
            kwargs["temperature"] = 0  # gemini and reasoning models keep their default
        if json_mode:
            kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
        model = ChatOpenAI(
            model=model_name, api_key=api_key, base_url=base_url, timeout=30, max_retries=1, **kwargs
        )

    _models[key] = model
    return model


class FailoverLLM:
    """Tries providers in order. A failed provider is skipped for a while."""

    def __init__(self, json_mode: bool = False):
        self.json_mode = json_mode

    def invoke(self, prompt):
        chain = provider_chain()
        now = time.time()
        ready = [p for p in chain if _cooldown.get((p, self.json_mode), 0) <= now]
        errors = []
        for name in ready or chain:
            try:
                result = _build(name, self.json_mode).invoke(prompt)
                STATE["last_provider"] = name
                print(f"[LLM] answered by {name}", flush=True)
                return result
            except Exception as e:
                msg = str(e).lower()
                wait = 600 if any(w in msg for w in ("401", "403", "api key", "api_key")) else 60
                _cooldown[(name, self.json_mode)] = time.time() + wait
                errors.append(f"{name}: {str(e)[:120]}")
                print(f"[LLM] {name} failed, switching to next provider. {str(e)[:120]}", flush=True)
        raise RuntimeError("All LLM providers failed: " + " | ".join(errors))


def get_chat_model(json_mode: bool = False):
    return FailoverLLM(json_mode)

# ---------------- image understanding (vision) ----------------
# Ollama llama3.2:3b is text-only, so only cloud providers are used for images.
VISION_PROVIDERS = ("gemini", "openai", "groq")

IMAGE_PROMPT = (
    "This image was sent to an IT helpdesk. Read any visible error message or text exactly, "
    "then describe the problem in 2 to 3 short sentences. Do not guess beyond what is visible."
)


def _vision_model(name: str):
    from langchain_openai import ChatOpenAI

    api_key, model_name, base_url = OPENAI_COMPAT[name]()
    if name == "groq":
        model_name = settings.GROQ_VISION_MODEL  # Groq text model cannot read images
        if not model_name:
            return None
    return ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url, timeout=45, max_retries=1)


def describe_image(data: bytes, mime: str) -> str:
    """Return a short text description of a screenshot. Empty string if no provider could read it."""
    from langchain_core.messages import HumanMessage

    b64 = base64.b64encode(data).decode()
    msg = HumanMessage(content=[
        {"type": "text", "text": IMAGE_PROMPT},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
    ])
    for name in provider_chain():
        if name not in VISION_PROVIDERS:
            continue
        try:
            model = _vision_model(name)
            if model is None:
                continue
            text = model.invoke([msg]).content
            STATE["last_provider"] = name
            print(f"[LLM] image read by {name}", flush=True)
            return text.strip() if isinstance(text, str) else str(text)
        except Exception as e:
            print(f"[LLM] {name} could not read image. {str(e)[:120]}", flush=True)
    return ""