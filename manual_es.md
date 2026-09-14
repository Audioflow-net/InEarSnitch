# InEar Snitch: Manual de Usuario

Bienvenido a InEar Snitch, el software profesional para medir, analizar y diagnosticar monitores in-ear (IEMs).
Este manual explica las funciones principales y le guía para realizar mediciones precisas.

## Atajos de Teclado (Keyboard Shortcuts)

Los siguientes atajos acelerarán su flujo de trabajo:
- `Espacio`: Ejecutar barrido (Iniciar medición)
- `Ctrl+S` / `Cmd+S`: Guardar curva (Save Trace)
- `Retroceso` / `Suprimir`: Borrar curva (Clear Trace)
- `Ctrl+1`, `Ctrl+2`, `Ctrl+3`, `Ctrl+4`: Cambiar entre pestañas (Profile, Measurement, Analysis, History)

## 1. La Interfaz de Usuario (Pestañas)

La aplicación está dividida en cuatro áreas principales (pestañas):

- **Measurement (Medición):** Aquí se capturan las respuestas de frecuencia en tiempo real.
- **Analysis (Análisis):** Dedicado al examen detallado de sus mediciones, incluyendo el "Motor de Diagnóstico Automático" y comparaciones L/R (Izquierda/Derecha).
- **History (Historial/Vault):** Una base de datos de todas sus mediciones pasadas. Puede cargar, comparar y exportar curvas antiguas aquí.
- **Profile (Perfil):** Configure perfiles específicos para diferentes modelos de IEM, incluyendo curvas objetivo e imágenes de referencia.

## 2. Realización de Mediciones

En la pestaña **Measurement**, se realizan las mediciones acústicas de sus IEMs.

- **Multi-Sweep (Barrido Múltiple):** Para mayor precisión, el software puede emitir varios barridos de frecuencia consecutivamente y promediar los resultados. Esto minimiza el ruido de fondo y las interferencias.
- **Smoothing (Suavizado):** Los datos acústicos brutos a menudo contienen pequeños picos inaudibles (filtro de peine). Usar la función de *Smoothing* (ej. 1/12 o 1/24 de octava) promedia la curva, haciéndola más acorde con la audición humana y más fácil de leer visualmente.
- **Proceso:** Coloque el IEM en el acoplador de medición, asegúrese de que haya un sellado acústico hermético y presione Start (o `Espacio`). Una vez finalizado, puede guardar la curva resultante.

## 3. Menú Lateral de Configuración (Routing y Calibración)

A un lado de la aplicación, encontrará el **Settings Slide-Out** (Menú lateral de ajustes).

- **Routing (Enrutamiento):** Defina qué entradas de audio (micrófono de medición/acoplador) y salidas (salida de auriculares al IEM) se utilizarán.
- **Calibration (Calibración):** Los micrófonos rara vez son 100% lineales. Cargue un archivo de calibración (`.cal` o `.txt`) para compensar las desviaciones específicas de su micrófono. La calibración se aplica en tiempo real a todas las mediciones entrantes.

## 4. Análisis y Motor de Diagnóstico Automático

El "Automated Diagnostics Engine" (en la pestaña Analysis) evalúa su medición para detectar defectos de hardware o errores del usuario automáticamente. Compara el balance Izquierda/Derecha o mide contra una curva de referencia cargada.

Las principales detecciones de diagnóstico incluyen:
- **Acoustic Seal Leak (Fuga de Sello Acústico):** Si la respuesta de graves cae ligeramente (ej. ~4 dB), el motor advierte de una fuga. Esto suele ocurrir cuando el IEM no está correctamente sellado en el acoplador (ej. falta de blu-tack) y no es un defecto de hardware.
- **Dead Bass Driver (Driver de Graves Muerto):** Una caída masiva en la región de graves (ej. >15 dB) indica que el driver dinámico o woofer está defectuoso o masivamente bloqueado.
- **Wax Clog / Dead Tweeter (Obstrucción por Cera / Tweeter Muerto):** Una caída extrema de alta frecuencia (ej. >12 dB) sugiere un filtro acústico/boquilla obstruido (cera del oído) o un tweeter completamente muerto.
- **L/R Imbalance (Desequilibrio L/R):** Advierte de diferencias significativas de volumen entre el auricular izquierdo y derecho, lo que podría indicar un defecto en un lado.

## 5. Historial (History Vault)

La pestaña **History** actúa como su caja fuerte. Cada medición que tome se puede guardar y organizar aquí.
- Puede superponer múltiples curvas históricas para comparar el desgaste de un IEM a lo largo del tiempo o comprobar la consistencia después de la limpieza.
- Exporte fácilmente curvas seleccionadas como CSV para compartir o analizar externamente.
- **Import CSV:** Haga clic en "Import CSV" para añadir una medición externa directamente a la base de datos.
- **Save as Target:** Exporte cualquier curva del historial directamente a su carpeta Reference Targets, haciéndola disponible inmediatamente como una curva Target en toda la aplicación (similar a los targets de squiglink).
- **Renombrar Mediciones:** Haga doble clic en la columna "Notes" para renombrar las mediciones en la base de datos del historial directamente.

## 6. Calibración Automática (Auto-Generate from Reference)

Si no posee un micrófono de medición IEC 711 calibrado costoso (sino que usa un acoplador "falso" asequible), ¡puede usar la aplicación para generar un archivo de calibración personalizado!

Use el botón **"🪄 Auto-Generate from Reference"** en el menú de Calibración:

1. **Cree su propia medición:** Mida un IEM conocido y de alta calidad utilizando su propio acoplador (falso) y guarde esta curva en la pestaña Measurement como CSV.
2. **Haga clic en el botón:** Abra el menú de Calibración (Settings Slide-Out) y haga clic en "🪄 Auto-Generate from Reference".
3. **Seleccione los archivos:**
   - *Paso 1:* Seleccione el archivo CSV de SU medición (con el acoplador falso).
   - *Paso 2:* Seleccione la medición profesional en CSV (la Referencia "Verdadera") del mismo IEM de la carpeta `reference_targets`.
4. **¡Magia!** El software interpola ambas curvas, iguala su volumen a 500Hz y calcula la diferencia exacta. Luego genera un archivo `Auto_Generated_Fake711_Cal.txt` en la carpeta `calibrations` y lo aplica de inmediato. ¡Su micrófono asequible ahora medirá tan linealmente como la costosa configuración de referencia!

## 7. Gestión de Base de Datos (Database Management)

El menú de Configuración (Settings) ahora tiene una sección de **Database Management** donde puede realizar una copia de seguridad (Backup) de toda su base de datos SQLite (`inearsnitch.db`) y restaurar desde copias de seguridad anteriores (Restore). El sistema crea automáticamente un archivo `.safety.bak` al restaurar para evitar la pérdida accidental de datos.

## 8. Menús Desplegables de Búsqueda Inteligente (Smart Searchable Dropdowns)

Los comboboxes (menús desplegables) de Target e History en toda la aplicación ahora permiten búsquedas completas. Puede escribir cualquier parte del nombre (ej., "v7") para encontrar rápidamente entradas coincidentes (ej., "Vision Ears v7").

## 9. RTA en Vivo y Guía IEC (Profundidad de Inserción)

En la parte inferior derecha de la interfaz principal, encontrará el botón **RTA (Real-Time Analyzer / Analizador en Tiempo Real)**. Este modo reproduce "Pink Noise" (ruido rosa) y muestra el espectro de frecuencia medido en tiempo real. Se utiliza para posicionar el IEM perfectamente en el acoplador de medición *antes* de iniciar el barrido (sweep) propiamente dicho.

Directamente debajo del botón RTA se encuentra la casilla **"IEC Guide"** (anteriormente "8k Helper").

### ¿Cómo funciona la Guía IEC?
Cuando el IEM se inserta en el tubo de medición (acoplador IEC 711), se forma una pequeña cavidad entre el IEM y el micrófono. El aire en esta cavidad resuena físicamente a una frecuencia muy específica: la "Resonancia del Acoplador" (Coupler Resonance).

El estándar IEC 711 fue diseñado específicamente en los años 80 para que esta resonancia simule el canal auditivo humano. Para obtener una medición comparable (p. ej., con bases de datos de Crinacle o Super*Review), el IEM DEBE insertarse a una profundidad en la que esta resonancia física se produzca exactamente en el rango de **7.000 Hz a 8.600 Hz** (clásicamente ~8 kHz).

La *Guía IEC* muestra una zona verde objetivo (7 - 8,6 kHz) y una cruz de referencia que rastrea el pico de resonancia actual en tiempo real.
- Texto rojo ("Push Deeper" / "Empuje más profundo"): La resonancia está por debajo de 7 kHz -> Empuje el IEM más adentro del tubo.
- Texto rojo ("Pull Out Slightly" / "Retire ligeramente"): La resonancia está por encima de 8,6 kHz -> Retire el IEM un poco.
- Texto verde ("Depth OK" / "Profundidad correcta"): ¡Se ha alcanzado la profundidad de inserción perfecta!

### ¿Por qué siempre 8 kHz, incluso con diferentes calibraciones?
Una pregunta frecuente es por qué la guía *siempre* apunta a 8 kHz, incluso si se han cargado perfiles de calibración de micrófono completamente diferentes.
La respuesta está en la **física**: Un archivo de calibración (ya sea Dayton, Sonarworks o "Fake 711") solo corrige las imperfecciones internas de la diminuta cápsula del micrófono (p. ej., si el micrófono graba de forma natural un poco más bajo a 10 kHz).
Sin embargo, el tubo metálico físico del acoplador mantiene exactamente la misma longitud. Por lo tanto, una calibración por software nunca desplaza la resonancia física del aire a 8 kHz. La guía siempre le mostrará la profundidad de inserción física acústicamente correcta, completamente independiente del archivo de calibración seleccionado.

## 10. Aviso de Salud y Seguridad (EULA)

En el primer inicio de InEar Snitch, aparece un **aviso de Salud y Seguridad** (Health & Safety Disclaimer). Este diálogo le informa sobre dos riesgos esenciales:

- **Daños auditivos:** ¡**Nunca** lleve los IEMs puestos en los oídos mientras se ejecuta una medición (barrido o prueba de estrés)! Los niveles de señal producidos durante las mediciones pueden dañar permanentemente su audición.
- **Daños al hardware:** Ajustes de nivel inadecuados pueden dañar drivers de IEM sensibles (especialmente drivers de armadura balanceada / Balanced Armature).

Debe hacer clic en **"Accept"** (Aceptar) para continuar usando la aplicación. Si hace clic en **"Decline"** (Rechazar), la aplicación se cerrará inmediatamente. Este diálogo aparece solo una vez – su aceptación se almacena permanentemente en los ajustes de la aplicación.

## 11. Calibración del Nivel de Salida (Output Level Calibration)

La aplicación incluye una función de calibración automática de nivel que determina el **nivel de salida** (output level / amplitud de salida) óptimo para su configuración de hardware específica. Encontrará esta función en **Settings > "Start Auto-Calibration"**.

### Proceso de calibración:
1. La aplicación reproduce una serie de tonos de prueba ascendentes (comenzando a un nivel bajo).
2. Analiza el nivel grabado y encuentra automáticamente la amplitud de barrido óptima.
3. **Pico de grabación objetivo:** -15 dBFS – esto garantiza un margen de seguridad suficiente frente al clipping, manteniendo una relación señal-ruido adecuada.

### Posibles advertencias:
- **Pico de grabación demasiado bajo (< -30 dBFS):** La señal grabada es demasiado débil a pesar de la amplitud máxima del barrido. **Solución:** Aumente el nivel de salida del sistema (volumen del sistema operativo) y ejecute la calibración de nuevo.
- **Prueba de estrés limitada:** Si la prueba de estrés no puede emitirse a un nivel más alto que el barrido normal (ambos al máximo de amplitud), aparece una advertencia indicando que la detección de Rub & Buzz puede ser poco fiable.

> ⚠️ **Nota importante sobre terminología:** Esta calibración ajusta el **nivel de salida** (output level / amplitud del barrido) – ¡NO la ganancia (gain)! La ganancia se refiere a la preamplificación del micrófono en la entrada de su interfaz de audio y no es modificada por la aplicación.

## 12. Verificación de Nivel Previa (Preflight Level Check)

Antes de **cada** medición – tanto en barridos normales como en pruebas de estrés – InEar Snitch realiza automáticamente una rápida **verificación de nivel previa** (Preflight Level Check).

### Proceso:
1. La aplicación reproduce un breve tono de prueba (100 ms).
2. El nivel grabado se compara con el **valor de referencia de calibración** almacenado.

### Situaciones detectadas:

- **Desviación de nivel > 4 dB:** Si el nivel ha cambiado más de 4 dB desde la última calibración (p. ej., porque alguien modificó el nivel de salida del sistema), aparece una ventana emergente:
  > *"Level shifted by X dB since calibration. Do you want to continue anyway?"*
  
  Puede continuar con **Yes** (Sí) o cancelar con **No** y recalibrar primero.

- **Clipping detectado (> -1 dBFS):** La señal de entrada está saturada – el nivel debe reducirse.
- **Sin señal detectada (< -55 dBFS):** No se recibe ninguna señal utilizable – verifique el cableado y el enrutamiento (routing).

## 13. Límite de Seguridad DSP/EQ (DSP/EQ Safety Cap)

Cuando el **motor DSP** integrado (el EQ incorporado) está activo, los refuerzos de frecuencia (boosts) pueden amplificar la señal de salida más allá de la amplitud original del barrido.

Para prevenir daños en drivers sensibles, InEar Snitch **aplica automáticamente un limitador de seguridad después del procesamiento del EQ**. Esto garantiza que los boosts del EQ **nunca** puedan superar la amplitud máxima del barrido.

Esto es especialmente importante para los sensibles **drivers de armadura balanceada (Balanced Armature)**, que pueden dañarse permanentemente por sobreexcitación. El Safety Cap funciona de forma transparente en segundo plano – no requiere configuración alguna.

## 14. Guía de Solución de Problemas (Troubleshooting)

> **MENSAJE CLAVE:** En caso de duda: retire el IEM, vuelva a colocarlo y mida de nuevo. La mayoría de los problemas se deben a un mal sellado, no a defectos.

| Síntoma | Causa | Solución |
| :--- | :--- | :--- |
| **Clipping / Saturación** (La respuesta de frecuencia se ve cortada, meseta en dB altos) | Output Level configurado demasiado alto | Rehacer calibración de nivel, objetivo -15 dBFS |
| **Caída de Graves / Sin Graves** (El gráfico cae abruptamente por debajo de 200 Hz) | 1. Mal sellado en el acoplador, 2. Previo de auriculares débil, 3. Caída normal de driver BA | Volver a colocar el IEM, comprobar Blu-Tack, usar mejor salida de auriculares si es necesario |
| **Fase Invertida** (El diagnóstico indica "L/R OUT OF PHASE") | Tarjetas de sonido USB baratas invierten la fase | Comprobar orientación del cable de 2 pines. Si ambos lados están invertidos = no hay problema |
| **Alta Distorsión (THD)** (El gráfico THD muestra >5% en medios) | 1. Ruido de fondo (AC, pisadas), 2. La interfaz satura internamente | Medir en un entorno silencioso, comprobar Level |
| **Señal Demasiado Baja** (Gráfico < -50 dBFS, el diagnóstico no funciona) | Mic Gain en la interfaz demasiado bajo | Subir el Gain en el previo (¡no el Output Level!) |
| **Resultados Inconsistentes** (Cada medición se ve diferente) | La posición en el acoplador varía, el IEM resbala | Usar Sweep x5 (Promedio), fijar IEM con Blu-Tack |
| **Picos de Agudos en 8 kHz** (Pico agudo en 8 kHz) | Resonancia propia del acoplador IEC-711 (¡normal!) | Es normal, no un defecto. Usar la Guía IEC (herramienta de profundidad) para calibrar la inserción |

## 15. Más Solución de Problemas y Mejores Prácticas (IMPORTANTE)

### 1. ¡Mi respuesta de frecuencia es una línea perfectamente plana!
Si ves una línea casi perfectamente plana después de ejecutar un barrido (sweep), el 99% de las veces se debe a los **Filtros de Audio del Sistema Operativo** (AGC / Auto-Gain / Voice Isolation):
- **macOS:** Haz clic en el ícono del micrófono amarillo en el Centro de Control (arriba a la derecha) y cambia el modo del micrófono estrictamente a **"Estándar"** (NO a "Aislamiento de voz").
- **Windows:** En la configuración de sonido, desactiva todas las "Mejoras de audio" (Audio Enhancements) para tu micrófono de medición.
Estos compresores de rango dinámico intentan suprimir agresivamente el sonido extremadamente fuerte del barrido en tiempo real. Esto aplana la amplitud del audio grabado, resultando en un gráfico de línea plana completamente falso e inválido tras la deconvolución.

### 2. Advertencia: "Signal too quiet" a pesar del alto volumen
InEar Snitch emite intencionalmente el barrido de medición a un volumen digital muy bajo (-20 dBFS) para evitar que tu micrófono se sature (clipping). ¡Un monitor intrauditivo dentro de un acoplador de silicona sellado genera más de 115 dB SPL! Emitir un barrido a máxima escala (0 dBFS) saturaría instantáneamente el ADC de tu tarjeta de sonido, lo que *también* resulta en una curva perfectamente plana e inválida. Si la aplicación te advierte que la señal es demasiado baja, debes aumentar la ganancia de entrada física (Gain) en tu interfaz de micrófono, no el volumen de los auriculares.
