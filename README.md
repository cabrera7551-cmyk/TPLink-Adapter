# TPLink-Adapter

Herramienta de administración, diagnóstico, recuperación y configuración de adaptadores Wi-Fi USB en Kali Linux.

## Objetivo

Herramienta funcional para la gestión de adaptadores Wi-Fi USB, especialmente:

- TP-Link Archer T2U Plus (USB ID: 2357:0120, Chipset: Realtek RTL8821AU)
- Detección dinámica de hardware, interfaces, PHY, drivers y firmware
- Diagnóstico completo con clasificación de problemas
- Recuperación automática y manual de interfaces
- Cambio de modo seguro con rollback

## Funcionalidades

- Detección de adaptadores USB Wi-Fi
- Identificación de chipset, driver y firmware
- Detección dinámica de interfaces y PHY
- Lectura de modos soportados y modo actual
- Información de conexión Wi-Fi (SSID, BSSID, señal, etc.)
- Bandas y canales soportados
- Diagnóstico completo
- Recuperación de interfaces
- Cambio de modo con verificación y rollback
- Estado de red (todas las interfaces)
- Verificación de conectividad

## Seguridad

Este proyecto es únicamente para:
- Administración Wi-Fi
- Diagnóstico
- Recuperación
- Configuración
- Pruebas sobre equipos propios o autorizados

NO implementa:
- Captura de credenciales
- Phishing
- Evil Twin
- Deauthentication
- Cracking de contraseñas
- Ataques contra redes
- Robo de sesiones
- Bypass de autenticación

## Dependencias

- Python 3 estándar
- Herramientas nativas de Kali Linux:
  - iw, ip, nmcli, rfkill, ethtool, lsusb, modinfo, lsmod, dmesg, journalctl

## Uso

```bash
python main.py
```

## Estructura del proyecto

```
TPLink-Adapter/
├── README.md
├── .gitignore
├── main.py                 # Script principal funcional
├── legacy/
│   └── main_old.py         # Script original de referencia
├── src/                    # Infraestructura modular (para uso futuro)
│   ├── models/             # Modelos de datos y estados
│   └── commands/           # Ejecución segura de comandos
├── tests/                  # Pruebas del proyecto
│   ├── test_basic.py       # Test básico de estructura
│   └── test_syntax.py      # Test de sintaxis Python
└── reports/                # Directorio para reportes generados
```

## Características principales

### Detección dinámica
- No asume nombres fijos como wlan0, phy0, phy1, phy2
- Detecta automáticamente interfaces y PHY disponibles
- Soporta múltiples adaptadores Wi-Fi

### Manejo robusto de errores
- Timeouts en comandos
- Manejo de excepciones
- Validación de comandos existentes
- Clasificación de errores específicos

### Colores profesionales
- Solo usa: BLUE, WHITE, YELLOW, RED, GREEN
- Sin emojis ni decoración excesiva
- Diseño limpio y profesional

### Verificación de cambios
- Verificación automática después de cambio de modo
- Rollback automático si falla el cambio
- Verificación de conectividad después de recuperación

## Hardware de referencia

- TP-Link Archer T2U Plus
- USB: 2357:0120
- Chipset: RTL8821AU
- Driver: rtw88_8821au

## Tests

Los tests están diseñados para ejecutarse en Kali Linux:

```bash
python test_basic.py      # Test de estructura y sintaxis
python test_syntax.py     # Test de sintaxis Python
```

## Notas

- El script requiere Kali Linux o distribución similar
- Las herramientas de Linux específicas deben estar instaladas
- El adaptador Wi-Fi debe estar conectado para funcionamiento completo
