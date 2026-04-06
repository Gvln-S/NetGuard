# [NetGuard](https://github.com/Gvln-S/NetGuard)

## Visión General

Este proyecto implementa un Sistema de Detección y Respuesta ante Intrusiones (IDS/IPS) de arquitectura distribuida. Su objetivo es mitigar las amenazas de red en tiempo real directamente en el switch de acceso, eliminando la latencia crítica de los modelos de seguridad basados en la nube. Al procesar el tráfico en el borde (Edge Computing), el sistema garantiza una respuesta sub-segundo ante intentos de intrusión, protegiendo la integridad de la red local sin comprometer el rendimiento del tráfico de producción.

## Justificación Técnica

La adopción de Edge Computing en este proyecto se fundamenta en tres pilares:

* **Resiliencia Térmica y de Latencia**: El procesamiento local permite tiempos de respuesta de 1-10ms, comparado con los >100ms de la nube.
* **Preservación de Ancho de Banda**: Solo las alertas críticas y metadatos se envían para monitoreo centralizado, evitando la saturación del uplink con tráfico RAW.
* **Continuidad Operativa**: El sistema mantiene su capacidad de detección y bloqueo incluso durante fallos en la conectividad WAN.

## Arquitectura del Sistema

El diseño consta de un brazo de monitoreo donde el Cisco Catalyst 2960-X actúa como recolector de tráfico mediante puertos SPAN, y la Raspberry Pi 5 actúa como procesador de seguridad corriendo el motor Suricata. La respuesta se automatiza mediante scripts de Netmiko que modifican dinámicamente las tablas de direcciones MAC del switch.

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

## Contributions and Personalization

This is an open project for learning and experimentation. **You are more than welcome to fork this repository!** Feel free to add new textures, implement a complex lighting systems, or even add enemies. If you want to customize it to your tastes or add something new, contributions are always appreciated.

