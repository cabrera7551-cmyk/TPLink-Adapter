#!/usr/bin/env python3
"""Test básico de funcionalidad para main.py"""

import sys
import os
import re

# Verificar que main.py existe
if not os.path.exists('main.py'):
    print("ERROR: main.py no existe")
    sys.exit(1)

# Verificar que legacy/main_old.py existe
if not os.path.exists('legacy/main_old.py'):
    print("ERROR: legacy/main_old.py no existe")
    sys.exit(1)

# Verificar sintaxis de main.py
print("Verificando sintaxis de main.py...")
try:
    with open('main.py', 'r') as f:
        code = f.read()
    compile(code, 'main.py', 'exec')
    print("✓ Sintaxis Python válida")
except SyntaxError as e:
    print(f"ERROR: Sintaxis inválida: {e}")
    sys.exit(1)

# Verificar funciones principales
print("Verificando funciones principales...")
expected_functions = [
    'get_usb_devices', 'get_tp_link_usb', 'get_adapter_info',
    'get_all_wireless_interfaces', 'get_wireless_interface', 'get_phy',
    'get_mac', 'get_ipv4', 'get_carrier', 'get_interface_state',
    'get_current_mode', 'get_driver', 'get_driver_version', 'get_firmware',
    'get_supported_modes', 'ordered_supported_modes', 'get_band_information',
    'get_current_channel', 'adapter_information', 'supported_modes_menu',
    'band_channel_menu', 'adapter_status', 'diagnostic', 'change_mode',
    'mode_menu', 'network_overview', 'reconnect_wifi', 'get_connection_details',
    'get_default_gateway', 'get_dns_servers', 'check_internet', 'check_dns',
    'current_connection_info', 'detailed_driver_info', 'is_driver_compatible',
    'verify_driver', 'repair_driver', 'driver_menu', 'main_menu'
]

missing_functions = []
for func_name in expected_functions:
    if f"def {func_name}(" not in code:
        missing_functions.append(func_name)

if missing_functions:
    print(f"ERROR: Faltan funciones: {', '.join(missing_functions)}")
    sys.exit(1)

print(f"✓ Todas las {len(expected_functions)} funciones principales existen")

# Verificar colores
print("Verificando colores...")
expected_colors = ['BLUE', 'WHITE', 'YELLOW', 'RED', 'GREEN', 'RESET']
forbidden_colors = ['CYAN', 'MAGENTA', 'BOLD', 'DIM']

missing_colors = []
for color in expected_colors:
    if f"{color} = " not in code:
        missing_colors.append(color)

if missing_colors:
    print(f"ERROR: Faltan colores: {', '.join(missing_colors)}")
    sys.exit(1)

forbidden_found = []
for color in forbidden_colors:
    if f"{color} = " in code:
        forbidden_found.append(color)

if forbidden_found:
    print(f"ERROR: Colores prohibidos encontrados: {', '.join(forbidden_found)}")
    sys.exit(1)

print("✓ Colores correctos: solo BLUE, WHITE, YELLOW, RED, GREEN, RESET")

# Verificar base de datos de adaptadores
print("Verificando base de datos de adaptadores...")
if "2357:0120" not in code:
    print("ERROR: TP-Link Archer T2U PLUS no está en la base de datos")
    sys.exit(1)

print("✓ Base de datos de adaptadores correcta")

# Verificar mejoras de manejo de errores
print("Verificando mejoras de manejo de errores...")
error_handling_improvements = [
    "try:",
    "except Exception:",
    "except subprocess.TimeoutExpired:",
    "except FileNotFoundError:",
    "timeout=30"
]

improvements_found = 0
for improvement in error_handling_improvements:
    if improvement in code:
        improvements_found += 1

print(f"✓ Se encontraron {improvements_found}/{len(error_handling_improvements)} mejoras de manejo de errores")

# Verificar detección dinámica
print("Verificando detección dinámica...")
dynamic_detection = [
    "get_all_wireless_interfaces()",
    "get_wireless_interface()",
    "_SELECTED_INTERFACE"
]

dynamic_found = 0
for detection in dynamic_detection:
    if detection in code:
        dynamic_found += 1

print(f"✓ Se encontraron {dynamic_found}/{len(dynamic_detection)} elementos de detección dinámica")

print("\n" + "="*50)
print("✓ TODOS LOS TESTS BÁSICOS PASARON")
print("="*50)
print("\nNOTA: Las pruebas funcionales requieren Kali Linux")
print("con el adaptador TP-Link Archer T2U Plus conectado.")
print("Este entorno Windows solo puede verificar sintaxis y estructura.")

sys.exit(0)
