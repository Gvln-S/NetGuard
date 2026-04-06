# [NetGuard](https://github.com/Gvln-S/NetGuard)

## Visión General

Este proyecto implementa un Sistema de Detección y Respuesta ante Intrusiones (IDS/IPS) de arquitectura distribuida. Su objetivo es mitigar las amenazas de red en tiempo real directamente en el switch de acceso, eliminando la latencia crítica de los modelos de seguridad basados en la nube. Al procesar el tráfico en el borde (Edge Computing), el sistema garantiza una respuesta sub-segundo ante intentos de intrusión, protegiendo la integridad de la red local sin comprometer el rendimiento del tráfico de producción.

## Justificación Técnica

La adopción de Edge Computing en este proyecto se fundamenta en tres pilares:

* **Resiliencia Térmica y de Latencia**: El procesamiento local permite tiempos de respuesta de 1-10ms, comparado con los >100ms de la nube.
* **Preservación de Ancho de Banda**: Solo las alertas críticas y metadatos se envían para monitoreo centralizado, evitando la saturación del uplink con tráfico RAW.
* **Continuidad Operativa**: El sistema mantiene su capacidad de detección y bloqueo incluso durante fallos en la conectividad WAN.

## Arquitectura del Sistema

El diseño consta de un brazo de monitoreo donde el Cisco Catalyst 2960-X actúa como recolector de tráfico mediante puertos SPAN, y la Raspberry Pi 4 actúa como procesador de seguridad corriendo el motor Suricata. La respuesta se automatiza mediante scripts de Netmiko que modifican dinámicamente las tablas de direcciones MAC del switch.

### Especificaciones de Hardware y Presupuesto

| Componente | Especificación / Restricción | Costo Estimado |
| :--- | :--- | :--- |
| Raspberry Pi 4 | CPU 4x Cortex-A72 (Throttling a 80°C) | Existente ($0) |
| RAM | 8GB LPDDR4-3200 | Incluido |
| Switch Cisco | Catalyst 2960-X (Gigabit / SPAN limitado) | Existente ($0) |
| Almacenamiento | MicroSD Clase 10 / Opcional NVMe | Existente ($0) |
| Refrigeración | Active Cooler (Obligatorio para IDS) | $10.00 |
| Alimentación | 5V/5A USB-C PD | Existente ($0) |
| **Total** | | **$10.00 USD** |

---

## Planificación de Producto (Entregable B): Backlog y MVP

Siguiendo metodologías ágiles, el proyecto se ha desglosado en historias de usuario y características técnicas, priorizando el "Mínimo Viable" para asegurar la funcionalidad básica de seguridad.

### Características "Must-Have" (MVP)
Estas funcionalidades son esenciales para que el sistema sea considerado operacional:
* **Conectividad de Espejado:** Configuración de una sesión de SPAN local en el switch Cisco que refleje el tráfico de un puerto de usuario hacia la Raspberry Pi.
* **Inspección de Paquetes:** Despliegue de Suricata configurado con el conjunto de reglas ET-Open y optimizado para la arquitectura ARM64 de la Pi 4.
* **Respuesta Automática SSH:** Script de Python capaz de interceptar alertas de Suricata y ejecutar un comando de bloqueo (`mac address-table static... drop`) en el switch vía SSH.
* **Seguridad de Acceso:** Configuración de SSH v2 y autenticación robusta en los dispositivos.

### Características "Nice-to-Have" (Roadmap)
Funcionalidades adicionales para mejorar la experiencia de gestión y la robustez:
* **Dashboard Spring Boot:** Interfaz gráfica para la visualización centralizada de eventos.
* **Notificaciones Externas:** Integración con API de Telegram para alertas instantáneas al móvil del administrador.
* **Persistencia en Base de Datos:** Registro histórico de eventos en una base de datos relacional para auditoría forense.
* **Optimización NVMe:** Uso de un SSD NVMe a través de la interfaz PCIe para acelerar la escritura de logs.

---

## Gestión de Incertidumbre (Entregable D): Spike Arquitectónico

En la gestión de proyectos ágiles, un **"Spike"** es una tarea de investigación destinada a resolver un riesgo técnico desconocido. Para este proyecto, el riesgo de mayor impacto es: *"La latencia y confiabilidad de la comunicación SSH persistente desde el entorno de análisis de tráfico hacia el hardware de conmutación"*.

### Definición del Spike: Automatización de Respuesta en Tiempo Real
Si el script de respuesta intenta abrir una nueva conexión SSH cada vez que detecta un paquete malicioso, el tiempo de establecimiento de la sesión (Handshake, KEX, Auth) podría demorar entre 1 y 3 segundos, permitiendo que miles de paquetes maliciosos pasen antes de que el bloqueo se aplique.

**Pasos para la Validación Técnica:**
1. **Evaluación de Latencia SSH:** Desarrollar un script mínimo que mida el tiempo de ejecución de un comando `config t` en el switch Cisco partiendo desde cero.
2. **Prueba de Sesión Persistente:** Comparar el tiempo de respuesta anterior frente a una conexión mantenida abierta mediante keep-alives de Netmiko.
3. **Análisis de Impacto en el Switch:** Monitorear el uso de CPU del switch Cisco durante 50 intentos rápidos de conexión SSH para asegurar que el proceso de gestión (VTY) no se sature.
4. **Validación de Bloqueo:** Verificar si el comando `mac address-table static... drop` surte efecto de manera retroactiva sobre flujos TCP ya establecidos.

> **Nota:** Este Spike debe completarse en la **Semana 2** para decidir si la arquitectura de respuesta será mediante conexiones bajo demanda o una conexión de gestión permanente.

---

## Contributions and Personalization

This is an open project for learning and experimentation. **You are more than welcome to fork this repository!**. If you want to customize it to your tastes or add something new, contributions are always appreciated.
