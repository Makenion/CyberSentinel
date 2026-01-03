# CyberSentinel: Security & Vulnerability Toolkit 🛡️

Proyecto modular desarrollado en Python enfocado en la automatización de tareas de ciberseguridad, monitoreo de vulnerabilidades y herramientas de reconocimiento (Pentesting). 

Este proyecto nace como un desafío personal de desarrollo constante, con el objetivo de profundizar en el ecosistema de la seguridad informática y la ingeniería de software.

## 🚀 Objetivos del Proyecto
- Monitoreo de CVEs: Rastreador automatizado de vulnerabilidades usando la API de NIST/NVD.
- Network Recon: Módulos de escaneo de puertos, enumeración de subdominios y análisis de cabeceras.
- Notificaciones: Sistema de alertas para vulnerabilidades críticas vía Discord/Telegram.
- Calidad de Software: Implementación de logs, manejo de excepciones y tests unitarios.

## 🛠️ Tecnologías
- Lenguaje: Python 3.10+
- Librerías principales: `requests`, `python-dotenv`, `sqlite3`, `socket`.
- Base de Datos: SQLite (para persistencia de vulnerabilidades).

## 📅 Bitácora de Desarrollo (Enero 2026)
| Día de Trabajo | Fecha  | Hito | Descripción |
|:---------------|:-------| :--- | :--- |
| 01             | 01 Ene | Inicio & Estructura | Repositorio, .gitignore y arquitectura modular. |
| 02             | 02 Ene | Configuración | Carga de .env y validación de seguridad de llaves. |
| 03             | 03 Ene | Alertas & Persistencia | Creación del notificador de Discord y gestión de historial para evitar duplicados. |
---
Desarrollado por [Esteban Tamayo - Makenion] - Ingeniero en Informática.