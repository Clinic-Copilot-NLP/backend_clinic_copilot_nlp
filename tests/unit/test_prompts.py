"""
Tests unitarios para los prompts clínicos.
"""

from app.core.prompts.clinical import SYSTEM_PROMPT, build_user_prompt


class TestSystemPrompt:
    def test_system_prompt_not_empty(self):
        """SYSTEM_PROMPT debe ser una cadena no vacía."""
        assert isinstance(SYSTEM_PROMPT, str)
        assert len(SYSTEM_PROMPT) > 0

    def test_system_prompt_contains_json_instructions(self):
        """SYSTEM_PROMPT debe mencionar JSON (formato de respuesta esperado)."""
        assert "json" in SYSTEM_PROMPT.lower()


class TestBuildUserPrompt:
    def test_build_user_prompt_wraps_in_xml(self):
        """El texto de la historia debe quedar entre etiquetas XML."""
        historia = "Paciente de prueba con hipertensión."
        result = build_user_prompt(historia)
        assert "<historia_clinica>" in result
        assert historia in result
        assert "</historia_clinica>" in result

    def test_build_user_prompt_returns_string(self):
        """build_user_prompt debe retornar un str."""
        result = build_user_prompt("texto de prueba cualquiera aquí.")
        assert isinstance(result, str)

    def test_build_user_prompt_contains_input(self):
        """El input debe estar presente en el output."""
        historia = "Texto clínico de prueba con detalles médicos relevantes."
        result = build_user_prompt(historia)
        assert historia in result
