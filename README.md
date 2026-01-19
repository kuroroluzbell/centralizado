# Asistente de Revisión de Código Potenciado por LLM

Este proyecto proporciona un conjunto de flujos de trabajo de GitHub Actions para mejorar la calidad y seguridad del código en tus repositorios, utilizando un Modelo de Lenguaje Grande (LLM) para realizar revisiones automáticas de código y un quality gate para la cobertura de pruebas.

## Características

- **Revisión de Código por IA**: Un flujo de trabajo reutilizable (`code-review-gemini.yml`) que analiza los archivos modificados en un pull request utilizando el modelo **Gemini 1.5 Flash**.
- **Quality Gate de Cobertura**: Un flujo de trabajo (`quality-gate.yml`) que valida el reporte de cobertura de pruebas y puede hacer fallar el pipeline si no se alcanza un umbral mínimo.
- **Análisis de Severidad**: El script de revisión es capaz de interpretar la severidad de los hallazgos del LLM (Alta, Media, Baja) y hacer fallar el pipeline en consecuencia.
- **Identidad de Experto**: El LLM es instruido para actuar como un Ingeniero de Software Senior y Arquitecto de Ciberseguridad, proporcionando feedback pedagógico y de alta calidad.
- **Agentes Especializados**: El repositorio incluye un directorio `agents/` con definiciones de "personas" expertas (ej. `fastapi-expert.md`), preparando el terreno para futuras especializaciones de la revisión de código.

## ¿Cómo Funciona la Revisión de Código?

1.  **Disparador**: El flujo de trabajo `code-review-gemini.yml` se invoca desde otro flujo de trabajo, pasándole una lista de archivos a analizar.
2.  **Análisis con Gemini**: El script `.github/scripts/llm_review.py` recibe la lista de archivos.
3.  **Envío al LLM**: Cada archivo es enviado a la API de Gemini con un prompt detallado que instruye al modelo para auditar el código en base a cuatro pilares:
    - **Seguridad**: Vulnerabilidades (OWASP Top 10, inyecciones, etc.).
    - **Arquitectura y Diseño**: Principios SOLID y código duplicado.
    - **Estilo y Legibilidad**: Cumplimiento de PEP 8.
    - **Optimización**: Mejoras algorítmicas o de estructuras de datos.
4.  **Reporte y Control**:
    - El LLM devuelve un análisis en formato Markdown con una matriz de hallazgos.
    - El script `llm_review.py` imprime esta revisión en los logs del workflow.
    - Si se configura `fail_on_severity`, el script busca hallazgos que cumplan o superen el umbral (ej. 'alta') y, si los encuentra, hace fallar el pipeline.

## Configuración

Para utilizar los flujos de trabajo, necesitas configurar los siguientes secretos en tu repositorio de GitHub (`Settings > Secrets and variables > Actions`):

-   `LLM_PROVIDER`: El proveedor de LLM a utilizar. Actualmente, el script soporta `gemini`.
-   `LLM_API_KEY`: Tu clave de API para el proveedor.

## Ejemplo de Uso

Puedes llamar al flujo de trabajo de revisión de código desde tu propio workflow de CI/CD de la siguiente manera:

```yaml
jobs:
  code-review:
    uses: ./.github/workflows/code-review-gemini.yml
    with:
      files_to_analyze: ${{ steps.changed-files.outputs.all_modified_files }}
      fail_level: "alta" # Opcional: media, baja, ninguna
    secrets:
      LLM_PROVIDER: ${{ secrets.LLM_PROVIDER }}
      LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
```