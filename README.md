# Vinted Telegram Bot

Un bot de scraping en Python diseñado para monitorizar Vinted de forma automática y enviar notificaciones en tiempo real a Telegram cuando aparece una oferta que coincide con tus criterios. 

Actualmente configurado para cazar chollos del manga Slam Dunk, pero fácilmente adaptable a cualquier otro artículo.

## Características

- **Alertas enriquecidas en Telegram:** Envía el título, enlace directo y la foto de portada del artículo directamente a tu chat.
- **Bypass de Caché:** Genera URLs dinámicas (`timestamp`) para forzar a Vinted a mostrar los artículos más recientes saltándose los sistemas de caché.
- **Scroll Inteligente (Lazy Loading):** Simula el comportamiento humano bajando hasta el fondo de la página para cargar todo el catálogo reciente antes de analizarlo.
- **Filtro Positivo Estricto:** Solo avisa si el anuncio contiene las palabras clave exactas.
- **Muro Anti-Basura (Filtro Negativo):** Bloquea automáticamente:
  - Artículos en otros idiomas (francés, italiano, etc.).
  - Ropa y zapatillas (camisetas, sudaderas, sneakers).
  - Merchandising (figuras, pósters, cartas).
- **Memoria Local:** Guarda un registro (`historial.txt`) de los artículos ya vistos para no enviar alertas repetidas.
