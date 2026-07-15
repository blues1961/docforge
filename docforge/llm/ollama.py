from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class OllamaError(RuntimeError):
    """Erreur de communication avec Ollama."""


@dataclass(slots=True)
class OllamaResult:
    response: str
    model: str
    eval_count: int
    eval_duration: int

    @property
    def tokens_per_second(self) -> float:
        if self.eval_duration <= 0:
            return 0.0

        seconds = self.eval_duration / 1_000_000_000
        return self.eval_count / seconds


class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = 900,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def chat(
        self,
        *,
        model: str,
        system: str,
        prompt: str,
        num_ctx: int = 8192,
        temperature: float = 0.0,
        num_predict: int = 700,
    ) -> OllamaResult:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "stream": False,
            "think": False,
            "keep_alive": "5m",
            "options": {
                "num_ctx": num_ctx,
                "temperature": temperature,
                "num_predict": num_predict,
                "top_p": 0.8,
                "repeat_penalty": 1.15,
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as error:
            raise OllamaError(
                f"Impossible de communiquer avec Ollama : {error}"
            ) from error
        except ValueError as error:
            raise OllamaError(
                "Ollama a retourné une réponse JSON invalide."
            ) from error

        message = data.get("message", {})

        if not isinstance(message, dict):
            raise OllamaError(
                "Ollama n'a pas retourné de message valide."
            )

        generated_text = str(
            message.get("content", "")
        ).strip()

        if not generated_text:
            raise OllamaError(
                "Ollama n'a généré aucun contenu."
            )

        return OllamaResult(
            response=generated_text,
            model=str(data.get("model", model)),
            eval_count=int(data.get("eval_count", 0)),
            eval_duration=int(data.get("eval_duration", 0)),
        )
