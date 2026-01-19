import os
import sys
import argparse
import re
import google.generativeai as genai
from typing import List, Dict

def has_blocking_issues(review_text: str, fail_severity: str) -> bool:
    """
    Analiza el texto de una revisión en busca de hallazgos que cumplan o superen
    un nivel de severidad determinado.
    """
    severities: Dict[str, int] = {'baja': 1, 'media': 2, 'alta': 3}
    fail_level = severities.get(fail_severity.lower(), 4) # 4 para 'ninguna'

    # Expresión regular para encontrar la gravedad en la tabla Markdown, insensible a mayúsculas/minúsculas
    # Busca el patrón | (Gravedad) |
    pattern = re.compile(r"\|\s*\((Alta|Media|Baja)\)\s*\|", re.IGNORECASE)
    
    found_severities = pattern.findall(review_text)
    
    for severity_str in found_severities:
        found_level = severities.get(severity_str.lower())
        if found_level and found_level >= fail_level:
            print(f"Hallazgo de bloqueo detectado: Se encontró un problema de gravedad '{severity_str}', que cumple o supera el umbral de fallo '{fail_severity}'.")
            return True
            
    return False

def analyze_code_with_llm(files: List[str], provider: str, api_key: str) -> List[str]:
    """
    Analiza el contenido de los archivos especificados y devuelve las revisiones del LLM.
    """
    if provider.lower() != 'gemini':
        print(f"Error: Este script actualmente solo es compatible con el proveedor 'gemini'. Se encontró '{provider}'.")
        sys.exit(1)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Error: Fallo al inicializar el cliente de Gemini: {e}")
        sys.exit(1)

    llm_prompt = """
### IDENTIDAD
Eres un Ingeniero de Software Senior y Arquitecto de Ciberseguridad con especialidad en el ecosistema Python. Tu tono es estrictamente formal, académico y extremadamente pedagógico. Tu propósito no es solo corregir, sino formar al usuario como si fuera un estudiante de alto rendimiento que se integra a un entorno profesional.

### MISIÓN
Tu objetivo es auditar código Python buscando la excelencia técnica. Debes pensar paso a paso (Chain of Thought) antes de emitir un juicio, evaluando los siguientes pilares:
1. **Seguridad:** Identificar vulnerabilidades (OWASP Top 10, inyecciones, fugas de memoria).
2. **Arquitectura:** Detectar código duplicado y violaciones a los principios SOLID.
3. **Estilo Profesional:** Cumplimiento riguroso de PEP 8 y legibilidad.
4. **Optimización:** Sugerir mejores estructuras de datos o algoritmos más eficientes.

### RESTRICCIONES
- NUNCA entregues código sin explicar la teoría detrás del cambio.
- Prohibido el uso de lenguaje coloquial; mantén un nivel de "Seniority" en cada palabra.
- No omitas errores de tipado (Type Hinting) aunque el código funcione.
- Si el código es propenso a errores de ejecución, explica la jerarquía de excepciones necesaria.

### FORMATO DE SALIDA
Para cada revisión, utiliza obligatoriamente esta estructura de encabezados:

### 1. Diagnóstico Inicial
[Resumen ejecutivo de la calidad del código recibido]

### 2. Matriz de Hallazgos
| Gravedad | Categoría | Descripción del Riesgo o Mejora |
| :--- | :--- | :--- |
| (Alta/Media/Baja) | (Seguridad/Diseño/PEP8) | Detalle técnico breve |

### 3. El Porqué del Cambio (Explicación Paso a Paso)
[Aquí aplicas la pedagogía: explica la lógica del error y cómo impacta en un entorno de producción real]

### 4. Propuesta de Refactorización
```python
# Código corregido con comentarios profesionales y Type Hinting
    """
    
    reviews = []
    for file_path in files:
        print(f"\n--- Analizando {file_path} ---\n")
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            if not code.strip():
                print(f"Omitiendo archivo vacío o ilegible: {file_path}")
                continue

            full_prompt = f"{llm_prompt}\n\nPor favor, revisa el siguiente código del archivo '{file_path}':\n\n```python\n{code}\n```"
            response = model.generate_content(full_prompt)
            review_text = response.text
            
            print(review_text) # Imprime la revisión para el log
            reviews.append(review_text)

        except FileNotFoundError:
            print(f"Error: Archivo no encontrado en {file_path}")
        except Exception as e:
            print(f"Ocurrió un error al procesar {file_path}: {e}")
            
    return reviews

def main():
    parser = argparse.ArgumentParser(description="Analiza cambios en el código con un LLM y opcionalmente falla basado en la severidad.")
    parser.add_argument('--provider', type=str, default=os.getenv('LLM_PROVIDER', 'gemini'), help='Proveedor de LLM (gemini, openai, etc)')
    parser.add_argument('--api-key', type=str, default=os.getenv('LLM_API_KEY'), help='Clave de API para el proveedor de LLM')
    parser.add_argument('--files', nargs='+', required=True, help='Archivos a analizar')
    parser.add_argument('--fail-on-severity', type=str, default='ninguna',
                        choices=['alta', 'media', 'baja', 'ninguna'],
                        help='Falla el pipeline si se encuentra un hallazgo con esta severidad o una superior. Por defecto: ninguna.')
    args = parser.parse_args()

    if not args.api_key:
        print("Error: Se requiere la clave de API (--api-key).")
        sys.exit(1)

    reviews = analyze_code_with_llm(args.files, args.provider, args.api_key)
    
    if args.fail_on_severity == 'ninguna':
        print("\nAnálisis completado. No se configuró el fallo por severidad.")
        sys.exit(0)
        
    print(f"\nVerificando revisiones en busca de hallazgos con severidad '{args.fail_on_severity}' o superior...")
    
    pipeline_should_fail = False
    for review in reviews:
        if has_blocking_issues(review, args.fail_on_severity):
            pipeline_should_fail = True
            break # Un hallazgo de bloqueo es suficiente para fallar
            
    if pipeline_should_fail:
        print("\nERROR: El pipeline ha fallado debido a hallazgos críticos en la revisión de código.")
        sys.exit(1)
    else:
        print("\nAnálisis completado. No se encontraron hallazgos que superen el umbral de fallo.")
        sys.exit(0)

if __name__ == "__main__":
    main()
