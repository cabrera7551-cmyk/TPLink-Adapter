import os
import re
import shutil
import signal
import subprocess
import time

# ============================================================
# COLORES — PALETA HACKER
# ============================================================

BLUE = "\033[94m"
WHITE = "\033[97m"
YELLOW = "\033[93m"
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

# ============================================================
# BANNER ASCII
# ============================================================

BANNER = r"""
████████╗███████╗███╗   ███╗██████╗ ██╗███╗   ██╗
╚══██╔══╝██╔════╝████╗ ████║██╔══██╗██║████╗  ██║
   ██║   █████╗  ██╔████╔██║██████╔╝██║██╔██╗ ██║
   ██║   ██╔══╝  ██║╚██╔╝██║██╔══██╗██║██║╚██╗██║
   ██║   ███████╗██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
"""

# ============================================================
# BASE DE DATOS DE ADAPTADORES
# ============================================================

ADAPTER_DATABASE = {
    "2357:0120": {
        "model": "TP-Link Archer T2U PLUS",
        "chipset": "RTL8821AU",
        "driver": "rtw88_8821au",
        "package": "firmware-realtek",
    }
}

MODE_DESCRIPTIONS = {
    "managed": "Conectarse normalmente a una red Wi-Fi.",
    "monitor": "Observar señales y tráfico de paquetes Wi-Fi.",
    "AP": "Funcionamiento como punto de acceso Wi-Fi.",
    "AP/VLAN": "Interfaz virtual asociada a un punto de acceso.",
    "IBSS": "Crear una red Wi-Fi ad-hoc entre dispositivos.",
}

PREFERRED_MODE_ORDER = ["managed", "monitor", "AP", "IBSS", "AP/VLAN"]

COMPATIBLE_DRIVER_PATTERNS = {
    "RTL8821AU": [r"rtw88", r"8821au", r"rtl8821au"],
}

# ============================================================
# UTILIDADES
# ============================================================

def clear():
    os.system("clear")

def pause():
    input(f"\n{WHITE}Presiona {YELLOW}ENTER{RESET}{WHITE} para continuar...{RESET}")

def separator():
    line = "═" * 41
    print(f"{BLUE}{line}{RESET}")

def header(title):
    clear()
    separator()
    print(f"{WHITE}{title:^41}{RESET}")
    separator()
    print()

def run(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception:
        return ""

def run_result(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout.strip()
        if result.stderr.strip():
            output = f"{output}\n{result.stderr.strip()}" if output else result.stderr.strip()
        return result.returncode, output
    except Exception as e:
        return 1, str(e)

def run_argv(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except FileNotFoundError:
        return ""
    except Exception:
        return ""

def run_result_argv(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()
        if result.stderr.strip():
            output = f"{output}\n{result.stderr.strip()}" if output else result.stderr.strip()
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return 1, "Command timeout"
    except FileNotFoundError:
        return 1, "Command not found"
    except Exception as e:
        return 1, str(e)

def parse_nmcli_terse_line(line):
    fields = re.split(r"(?<!\\):", line)
    return [f.replace("\\:", ":").replace("\\\\", "\\") for f in fields]

def command_exists(command):
    return shutil.which(command) is not None

def exit_program(signum=None, frame=None):
    print(f"\n{RED}⚡{RESET} {YELLOW}Saliendo del sistema...{RESET}")
    raise SystemExit

signal.signal(signal.SIGINT, exit_program)

# ============================================================
# ICONOS DE ESTADO
# ============================================================

def ok(msg):
    print(f"{GREEN}  [OK]{RESET} {WHITE}{msg}{RESET}")

def err(msg):
    print(f"{RED}  [ERROR]{RESET} {WHITE}{msg}{RESET}")

def warn(msg):
    print(f"{YELLOW}  [WARNING]{RESET} {WHITE}{msg}{RESET}")

def info(label, value, value_color=YELLOW):
    print(f"{WHITE}{label}{RESET} {value_color}{value}{RESET}")

# ============================================================
# DETECCIÓN USB
# ============================================================

def get_usb_devices():
    if not command_exists("lsusb"):
        return []
    devices = []
    for line in run_argv(["lsusb"]).splitlines():
        match = re.search(r"ID\s+([0-9a-fA-F]{4}:[0-9a-fA-F]{4})\s+(.*)", line)
        if match:
            devices.append({"id": match.group(1).lower(), "description": match.group(2).strip()})
    return devices

def get_tp_link_usb():
    for device in get_usb_devices():
        if device["id"].startswith("2357:"):
            return device
    return None

def get_adapter_info():
    usb = get_tp_link_usb()
    if usb:
        usb_id = usb["id"]
        if usb_id in ADAPTER_DATABASE:
            data = ADAPTER_DATABASE[usb_id].copy()
            data["usb_id"] = usb_id
            data["usb_description"] = usb["description"]
            return data
        return {"usb_id": usb_id, "usb_description": usb["description"],
                "model": "TP-Link no registrado", "chipset": "Desconocido",
                "driver": "Desconocido", "package": "Desconocido"}
    return {"usb_id": "No detectado", "usb_description": "No detectado",
            "model": "No detectado", "chipset": "No detectado",
            "driver": "No detectado", "package": "No detectado"}

# ============================================================
# INTERFAZ / PHY / MAC / ESTADO / MODO
# ============================================================

_SELECTED_INTERFACE = None

def get_all_wireless_interfaces():
    interfaces = []
    output = run_argv(["iw", "dev"])
    if not output:
        return interfaces
    for line in output.splitlines():
        if line.strip().startswith("Interface "):
            interface = line.strip().split()[1]
            if interface not in interfaces:
                interfaces.append(interface)
    return interfaces

def choose_wireless_interface(interfaces):
    global _SELECTED_INTERFACE
    header("VARIAS INTERFACES WI-FI DETECTADAS")
    for idx, iface in enumerate(interfaces, start=1):
        print(
            f"{GREEN}[{idx}]{RESET} {WHITE}{iface}{RESET}  "
            f"{WHITE}MAC: {get_mac(iface)}{RESET}"
        )
    print()
    choice = input(f"{YELLOW}>{RESET} {WHITE}¿Cuál interfaz deseas administrar?:{RESET} ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(interfaces):
        _SELECTED_INTERFACE = interfaces[int(choice) - 1]
    else:
        _SELECTED_INTERFACE = interfaces[0]
        warn(f"Opción inválida, usando {_SELECTED_INTERFACE} por defecto.")
    return _SELECTED_INTERFACE

def get_wireless_interface():
    global _SELECTED_INTERFACE
    interfaces = get_all_wireless_interfaces()

    if not interfaces:
        _SELECTED_INTERFACE = None
        return None

    if len(interfaces) == 1:
        _SELECTED_INTERFACE = interfaces[0]
        return _SELECTED_INTERFACE

    if _SELECTED_INTERFACE in interfaces:
        return _SELECTED_INTERFACE

    return choose_wireless_interface(interfaces)

def change_managed_interface():
    header("CAMBIAR INTERFAZ ADMINISTRADA")
    interfaces = get_all_wireless_interfaces()
    if not interfaces:
        err("No se detectaron interfaces Wi-Fi.")
        pause()
        return
    if len(interfaces) == 1:
        info("Solo hay una interfaz Wi-Fi disponible:", interfaces[0], BLUE)
        global _SELECTED_INTERFACE
        _SELECTED_INTERFACE = interfaces[0]
        pause()
        return
    selected = choose_wireless_interface(interfaces)
    ok(f"Ahora se administrará: {selected}")
    pause()

def get_phy(interface):
    if not interface:
        return "Desconocido"
    try:
        output = run_argv(["iw", "dev"])
        if not output:
            return "Desconocido"

        current_phy = None
        for line in output.splitlines():
            stripped = line.strip()
            if stripped.startswith("phy#"):
                current_phy = stripped.replace("phy#", "phy")
            elif stripped.startswith("Interface ") and current_phy:
                parts = stripped.split()
                if len(parts) >= 2 and parts[1] == interface:
                    return current_phy
        return "Desconocido"
    except Exception:
        return "Desconocido"

def get_mac(interface):
    if not interface:
        return "Desconocida"
    try:
        output = run_argv(["cat", f"/sys/class/net/{interface}/address"])
        return output if output else "Desconocida"
    except Exception:
        return "Desconocida"

def get_ipv4(interface):
    if not interface:
        return None
    output = run_argv(["ip", "-4", "addr", "show", "dev", interface])
    match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", output)
    return match.group(1) if match else None

def get_carrier(interface):
    if not interface:
        return "Desconocido"
    try:
        output = run_argv(["cat", f"/sys/class/net/{interface}/carrier"])
        if output == "1":
            return "OK"
        if output == "0":
            return "NO-CARRIER"
        return "Desconocido"
    except Exception:
        return "Desconocido"

def get_interface_state(interface):
    if not interface:
        return "Desconocido"
    try:
        output = run_argv(["cat", f"/sys/class/net/{interface}/operstate"])
        return output.upper() if output else "Desconocido"
    except Exception:
        return "Desconocido"

def get_current_mode(interface):
    if not interface:
        return "Desconocido"
    match = re.search(r"type\s+(\S+)", run_argv(["iw", "dev", interface, "info"]))
    return match.group(1) if match else "Desconocido"

def get_driver(interface):
    if not interface:
        return "Desconocido"
    match = re.search(r"driver:\s*(.+)", run_argv(["ethtool", "-i", interface]))
    return match.group(1).strip() if match else "Desconocido"

def get_driver_version(interface):
    if not interface:
        return "Desconocida"
    match = re.search(r"version:\s*(.+)", run_argv(["ethtool", "-i", interface]))
    return match.group(1).strip() if match else "Desconocida"

def get_firmware(interface):
    if not interface:
        return "Desconocido"
    match = re.search(r"firmware-version:\s*(.+)", run_argv(["ethtool", "-i", interface]))
    return match.group(1).strip() if match else "No disponible"

# ============================================================
# MODOS SOPORTADOS
# ============================================================

def get_supported_modes(interface):
    result = []
    phy = get_phy(interface)
    if phy == "Desconocido":
        return result
    try:
        output = run_argv(["iw", "phy", phy, "info"])
        if not output:
            return result
        reading = False
        for line in output.splitlines():
            stripped = line.strip()
            if stripped == "Supported interface modes:":
                reading = True
                continue
            if reading:
                if stripped.startswith("*"):
                    mode = stripped.replace("*", "").strip()
                    if mode and mode not in result:
                        result.append(mode)
                elif stripped and not stripped.startswith("*"):
                    break
        return result
    except Exception:
        return result

def ordered_supported_modes(interface):
    supported = get_supported_modes(interface)
    ordered = [m for m in PREFERRED_MODE_ORDER if m in supported]
    ordered += [m for m in supported if m not in PREFERRED_MODE_ORDER]
    return ordered

# ============================================================
# BANDAS Y CANALES
# ============================================================

def classify_band(frequency_mhz):
    if 2400 <= frequency_mhz <= 2500:
        return "2.4 GHz"
    if 4900 <= frequency_mhz <= 5900:
        return "5 GHz"
    if 5925 <= frequency_mhz <= 7125:
        return "6 GHz"
    return None

def get_band_information(interface):
    result = {
        "2.4 GHz": {"channels": [], "widths": []},
        "5 GHz": {"channels": [], "widths": []},
        "6 GHz": {"channels": [], "widths": []},
    }
    phy = get_phy(interface)
    if phy == "Desconocido":
        return result
    output = run_argv(["iw", "phy", phy, "info"])
    if not output:
        return result

    blocks = re.split(r"\n(?=\s*Band\s+\d+:)", output)

    for block in blocks:
        widths_in_block = []
        channels_in_block = []

        for line in block.splitlines():
            stripped = line.strip()

            if stripped.startswith("HT Capabilities"):
                if "20 MHz" not in widths_in_block:
                    widths_in_block.append("20 MHz")

            if "HT20/HT40" in stripped:
                if "40 MHz" not in widths_in_block:
                    widths_in_block.append("40 MHz")

            if stripped.startswith("VHT Capabilities"):
                if "80 MHz" not in widths_in_block:
                    widths_in_block.append("80 MHz")

            match = re.search(r"(\d{4,5}(?:\.\d+)?)\s+MHz\s+\[(\d+)\]", stripped)
            if match and "[disabled]" not in stripped:
                frequency = float(match.group(1))
                channel = int(match.group(2))
                band = classify_band(frequency)
                if band:
                    channels_in_block.append((band, channel))

        for band, channel in channels_in_block:
            if channel not in result[band]["channels"]:
                result[band]["channels"].append(channel)
            for width in widths_in_block:
                if width not in result[band]["widths"]:
                    result[band]["widths"].append(width)

    for band in result:
        result[band]["channels"].sort()

    width_order = {"20 MHz": 1, "40 MHz": 2, "80 MHz": 3, "160 MHz": 4, "80+80 MHz": 5}
    for band in result:
        result[band]["widths"].sort(key=lambda x: width_order.get(x, 99))

    return result

def get_current_channel(interface):
    if not interface:
        return "Desconocido"
    try:
        output = run_argv(["iw", "dev", interface, "link"])
        if output:
            match = re.search(r"freq:?\s*(\d+)", output)
            if match:
                try:
                    frequency = int(match.group(1))
                    if frequency == 2484: return "14"
                    if 2412 <= frequency <= 2472: return str((frequency - 2407) // 5)
                    if 5000 <= frequency <= 5900: return str((frequency - 5000) // 5)
                except (ValueError, TypeError):
                    pass
        output = run_argv(["iw", "dev", interface, "info"])
        if output:
            match = re.search(r"channel\s+(\d+)", output)
            if match: return match.group(1)
        if command_exists("nmcli"):
            output = run_argv(["nmcli", "-t", "-f", "ACTIVE,CHAN", "dev", "show", interface])
            if output:
                match = re.search(r"yes:(\d+)", output)
                if match: return match.group(1)
        return "No disponible"
    except Exception:
        return "No disponible"

# ============================================================
# MENÚS
# ============================================================

def adapter_information():
    header("INFORMACIÓN DEL ADAPTADOR")
    interface = get_wireless_interface()
    adapter = get_adapter_info()
    info("Modelo:", adapter['model'], BLUE)
    info("Chipset:", adapter['chipset'], BLUE)
    info("USB ID:", adapter['usb_id'], BLUE)
    info("Interfaz:", interface or 'No detectada', BLUE)
    if interface:
        info("MAC:", get_mac(interface), BLUE)
        info("PHY:", get_phy(interface), BLUE)
        info("Estado:", get_interface_state(interface), GREEN)
        info("Modo:", get_current_mode(interface), YELLOW)
        info("Driver:", get_driver(interface), GREEN)
        info("Versión driver:", get_driver_version(interface), YELLOW)
        info("Firmware:", get_firmware(interface), YELLOW)
    else:
        err("No se detectó una interfaz Wi-Fi.")
    pause()

def supported_modes_menu():
    header("MODOS SOPORTADOS")
    interface = get_wireless_interface()
    if not interface:
        err("No se detectó el adaptador Wi-Fi."); pause(); return
    modes = ordered_supported_modes(interface)
    if not modes:
        err("No se pudieron detectar los modos."); pause(); return
    for mode in modes:
        print(f"{GREEN}  [+]{RESET} {YELLOW}{mode}{RESET} {WHITE}-{RESET} {WHITE}{MODE_DESCRIPTIONS.get(mode, 'Modo Wi-Fi soportado por el controlador.')}{RESET}")
    pause()

def band_channel_menu():
    header("BANDAS Y CANALES")
    interface = get_wireless_interface()
    if not interface:
        err("No se detectó el adaptador Wi-Fi."); pause(); return
    info_obj = get_band_information(interface)
    bands_to_show = ["2.4 GHz", "5 GHz"]
    if info_obj["6 GHz"]["channels"]:
        bands_to_show.append("6 GHz")
    for band in bands_to_show:
        print(f"{WHITE}{band}{RESET}")
        channels = info_obj[band]["channels"]
        widths = info_obj[band]["widths"]
        print(f"  {WHITE}Canales:{RESET} {BLUE}{', '.join(map(str, channels)) if channels else f'{RED}No detectados{RESET}'}{RESET}")
        print(f"  {WHITE}Anchos:{RESET}  {YELLOW}{', '.join(widths) if widths else f'{RED}No detectados{RESET}'}{RESET}")
        print()
    separator()
    info("Canal actual:", get_current_channel(interface), GREEN)
    separator()
    pause()

def adapter_status():
    header("ESTADO DEL ADAPTADOR")
    interface = get_wireless_interface()
    if not interface:
        err("No se detectó el adaptador."); pause(); return
    info("Interfaz:", interface, BLUE)
    info("Estado:", get_interface_state(interface), GREEN)
    info("Modo:", get_current_mode(interface), YELLOW)
    info("Canal:", get_current_channel(interface), BLUE)
    print()
    link = run_argv(["iw", "dev", interface, "link"])
    print(f"{WHITE}{link}{RESET}" if link else f"{YELLOW}El adaptador no tiene un enlace Wi-Fi activo.{RESET}")
    pause()

def diagnostic():
    header("DIAGNÓSTICO")
    adapter = get_adapter_info()
    interface = get_wireless_interface()
    print(f"{WHITE}[1] USB:{RESET}     {GREEN}Detectado{RESET}" if adapter["usb_id"] != "No detectado" else f"{WHITE}[1] USB:{RESET}     {RED}No detectado{RESET}")
    info("[2] Modelo:", adapter['model'], BLUE)
    info("[3] Chipset:", adapter['chipset'], BLUE)
    info("[4] Interfaz:", interface or 'No detectada', BLUE)
    if interface:
        info("[5] PHY:", get_phy(interface), BLUE)
        info("[6] Driver:", get_driver(interface), GREEN)
        nm_state = run_argv(["systemctl", "is-active", "NetworkManager"])
        print(f"{WHITE}[7] NetMgr:{RESET}  {GREEN}Activo{RESET}" if nm_state == "active" else f"{WHITE}[7] NetMgr:{RESET}  {YELLOW}{nm_state or 'No disponible'}{RESET}")
        print(f"{WHITE}[8] Modos:{RESET}")
        modes = ordered_supported_modes(interface)
        for mode in modes if modes else []:
            print(f"    {GREEN}[+]{RESET} {YELLOW}{mode}{RESET}")
        if not modes:
            print(f"    {RED}No detectados{RESET}")
    pause()

# ============================================================
# CAMBIO DE MODO
# ============================================================

def nm_manages_interface_check(interface):
    if not interface or not command_exists("nmcli"):
        return False
    output = run_argv(["nmcli", "-t", "-f", "GENERAL.STATE", "device", "show", interface])
    if not output:
        return False
    return "unmanaged" not in output.lower()

def change_mode(target_mode):
    interface = get_wireless_interface()
    if not interface:
        err("No se detectó el adaptador."); return False

    supported = get_supported_modes(interface)
    if target_mode not in supported:
        err(f"El modo {target_mode} no está soportado."); return False

    current = get_current_mode(interface)
    info("Modo actual:", current, YELLOW)
    info("Modo solicitado:", target_mode, GREEN)

    if current == target_mode:
        ok("El adaptador ya está en este modo."); return True

    if target_mode == "AP":
        warn("El modo AP está soportado. Se necesita hostapd para AP funcional.")
    if target_mode == "AP/VLAN":
        warn("AP/VLAN es una interfaz virtual asociada a un AP y no se crea manualmente.")
        return False

    nm_manages_interface = nm_manages_interface_check(interface)
    if nm_manages_interface:
        print(f"\n{YELLOW}Preparando cambio de modo (desconectando {interface} de NetworkManager)...{RESET}")
        run_argv(["sudo", "nmcli", "device", "disconnect", interface])
        time.sleep(1)

    command = (
        f"sudo ip link set {interface} down && "
        f"sudo iw dev {interface} set type {target_mode} && "
        f"sudo ip link set {interface} up"
    )
    code, output = run_result(command)

    if code == 0:
        time.sleep(2)
        new_mode = get_current_mode(interface)

        if new_mode.lower() == target_mode.lower():
            ok(f"Modo cambiado a: {new_mode}")
            result = True
        else:
            warn(f"Se solicitó {target_mode}, pero el modo detectado es {new_mode}.")
            result = False

        if target_mode == "managed" and nm_manages_interface:
            run_argv(["sudo", "nmcli", "device", "connect", interface])

        return result

    err("El controlador rechazó el cambio de modo.")
    if output:
        print(f"{WHITE}{output}{RESET}")

    warn("Revirtiendo la interfaz a modo managed...")
    try:
        run_argv(["sudo", "iw", "dev", interface, "set", "type", "managed"])
        run_argv(["sudo", "ip", "link", "set", interface, "up"])
    except Exception:
        err("Error durante el rollback.")

    if nm_manages_interface:
        try:
            run_argv(["sudo", "nmcli", "device", "connect", interface])
        except Exception:
            err("Error al reconectar a NetworkManager.")

    return False

def mode_menu():
    while True:
        header("CAMBIAR MODO")
        interface = get_wireless_interface()
        if not interface:
            err("No se detectó el adaptador Wi-Fi."); pause(); return

        modes = ordered_supported_modes(interface)
        current = get_current_mode(interface)
        info("Interfaz:", interface, BLUE)
        info("Modo actual:", current, YELLOW)
        print()

        if not modes:
            warn("No se detectaron modos soportados por el driver.")
            print()
            print(f"{WHITE}[0] Regresar{RESET}")
            input(f"\n{YELLOW}>{RESET} {WHITE}Selecciona:{RESET} ").strip()
            return

        numbered = {}
        for idx, mode in enumerate(modes, start=1):
            numbered[str(idx)] = mode
            description = MODE_DESCRIPTIONS.get(mode, "Modo Wi-Fi soportado por el controlador.")
            print(f"{GREEN}[{idx}]{RESET} {YELLOW}{mode}{RESET}")
            print(f"    {WHITE}{description}{RESET}")
            print()

        print(f"{WHITE}[0] Regresar{RESET}")
        choice = input(f"\n{YELLOW}>{RESET} {WHITE}Selecciona:{RESET} ").strip()

        if choice == "0":
            return

        selected = numbered.get(choice)
        if selected is None:
            err("Opción inválida."); time.sleep(1); continue

        if selected == current:
            warn(f"La interfaz ya está en modo {current}."); pause(); continue

        change_mode(selected)
        pause()

# ============================================================
# RED / INTERNET
# ============================================================

def network_overview():
    header("ESTADO DE RED (TODAS LAS INTERFACES)")

    output = run_argv(["ip", "-o", "link", "show"])
    if not output:
        err("No se pudo obtener la lista de interfaces.")
        pause()
        return

    for line in output.splitlines():
        match = re.match(r"\d+:\s+(\S+):\s+<[^>]*>.*?state\s+(\S+)", line)
        if not match:
            continue

        iface = match.group(1).split("@")[0]
        if iface == "lo":
            continue

        state = match.group(2)
        ip4 = get_ipv4(iface) or "Sin IPv4"
        carrier = get_carrier(iface)

        if state == "UP" and carrier == "OK" and ip4 != "Sin IPv4":
            color = GREEN
        elif state == "UP":
            color = YELLOW
        else:
            color = RED

        print(
            f"{color}● {iface:<10}{RESET} "
            f"estado={WHITE}{state:<7}{RESET} "
            f"carrier={WHITE}{carrier:<11}{RESET} "
            f"ip={WHITE}{ip4}{RESET}"
        )

    print()
    warn("UP + NO-CARRIER en Wi-Fi = interfaz encendida pero no asociada a ninguna red.")
    warn("UP + sin IPv4 en Ethernet = cable conectado pero sin DHCP/IP asignada.")
    pause()

def reconnect_wifi():
    header("REPARAR CONEXIÓN A INTERNET (WI-FI)")

    interface = get_wireless_interface()
    if not interface:
        err("No se detectó una interfaz Wi-Fi.")
        pause()
        return

    info("Interfaz Wi-Fi:", interface, BLUE)
    print(
        f"{BLUE}Estado:{RESET} {WHITE}{get_interface_state(interface)}{RESET}  "
        f"{BLUE}Carrier:{RESET} {WHITE}{get_carrier(interface)}{RESET}  "
        f"{BLUE}IPv4:{RESET} {WHITE}{get_ipv4(interface) or 'Sin IP'}{RESET}"
    )
    print()
    warn("Esto puede reiniciar la interfaz Wi-Fi y, si hace falta, el servicio NetworkManager.")
    choice = input(f"{YELLOW}>{RESET} {WHITE}¿Continuar? (s/n):{RESET} ").strip().lower()
    if choice != "s":
        warn("Operación cancelada.")
        pause()
        return

    print(f"\n{YELLOW}[1/4] Reiniciando interfaz {interface} (reset ligero)...{RESET}")
    run_argv(["sudo", "ip", "link", "set", interface, "down"])
    time.sleep(0.5)
    code, output = run_result_argv(["sudo", "iw", "dev", interface, "set", "type", "managed"])
    if code != 0:
        err("No se pudo poner la interfaz en modo managed.")
        if output:
            print(f"{WHITE}{output}{RESET}")
    run_argv(["sudo", "ip", "link", "set", interface, "up"])
    time.sleep(1)

    if nm_manages_interface_check(interface):
        run_argv(["sudo", "nmcli", "device", "connect", interface])
    time.sleep(1)

    if get_carrier(interface) == "OK":
        ok(f"{interface} recuperó el enlace sin reiniciar NetworkManager.")
    else:
        print(f"{YELLOW}[2/4] El reset ligero no bastó; reiniciando NetworkManager...{RESET}")
        code, output = run_result_argv(["sudo", "systemctl", "restart", "NetworkManager"])
        if code == 0:
            ok("NetworkManager reiniciado.")
        else:
            err("No se pudo reiniciar NetworkManager.")
            if output:
                print(f"{WHITE}{output}{RESET}")
        time.sleep(2)

    if not command_exists("nmcli"):
        err("nmcli no está disponible; no se puede continuar automáticamente.")
        pause()
        return

    print(f"\n{YELLOW}[3/4] Buscando redes Wi-Fi disponibles...{RESET}\n")
    run_argv(["sudo", "nmcli", "dev", "wifi", "rescan"])
    time.sleep(2)

    scan_output = run_argv(["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi", "list"])
    networks = []
    seen_ssids = set()
    for line in scan_output.splitlines():
        if not line.strip():
            continue
        parts = parse_nmcli_terse_line(line)
        ssid = parts[0].strip() if parts else ""
        if ssid and ssid not in seen_ssids:
            seen_ssids.add(ssid)
            networks.append({
                "ssid": ssid,
                "signal": parts[1] if len(parts) > 1 else "?",
                "security": parts[2] if len(parts) > 2 else "",
            })

    if not networks:
        err("No se detectaron redes Wi-Fi cercanas.")
        pause()
        return

    for idx, net in enumerate(networks, start=1):
        lock = "*" if net["security"] else "  "
        print(f"{GREEN}[{idx}]{RESET} {lock} {WHITE}{net['ssid']:<25}{RESET} {WHITE}señal: {net['signal']}%{RESET}")

    print()
    choice = input(f"{YELLOW}>{RESET} {WHITE}Selecciona el número de tu red (0 para cancelar):{RESET} ").strip()

    if choice == "0" or not choice:
        warn("Operación cancelada.")
        pause()
        return

    if not choice.isdigit() or not (1 <= int(choice) <= len(networks)):
        err("Opción inválida.")
        pause()
        return

    ssid = networks[int(choice) - 1]["ssid"]
    password = input(f"{YELLOW}>{RESET} {WHITE}Contraseña para '{ssid}' (ENTER si es abierta):{RESET} ").strip()

    print(f"\n{YELLOW}[4/4] Conectando a '{ssid}'...{RESET}")
    if password:
        code, output = run_result_argv(
            ["sudo", "nmcli", "dev", "wifi", "connect", ssid, "password", password]
        )
    else:
        code, output = run_result_argv(
            ["sudo", "nmcli", "dev", "wifi", "connect", ssid]
        )

    if code == 0:
        ok(f"Conectado a '{ssid}' correctamente.")
    else:
        err(f"No se pudo conectar a '{ssid}'.")
        if output:
            print(f"{WHITE}{output}{RESET}")
        pause()
        return

    time.sleep(2)

    print()
    separator()
    print(f"{WHITE}Estado de dispositivos:{RESET}")
    status_output = run_argv(["nmcli", "device", "status"])
    if status_output:
        print(status_output)
    separator()

    print(f"\n{YELLOW}Probando conectividad a Internet (ping a 8.8.8.8)...{RESET}\n")
    code, output = run_result_argv(["ping", "-c", "4", "8.8.8.8"])
    if output:
        print(output)
    print()

    if code == 0:
        ok("¡Internet funcionando correctamente!")
    else:
        err("Sin respuesta. Revisa la contraseña ingresada o la señal de la red.")

    pause()

def get_connection_details(interface):
    try:
        link_output = run_argv(["iw", "dev", interface, "link"])
        if not link_output or "Not connected" in link_output or "Not associated" in link_output:
            return None

        details = {}

        match = re.search(r"Connected to ([0-9a-fA-F:]{17})", link_output)
        details["bssid"] = match.group(1) if match else "Desconocido"

        match = re.search(r"SSID:\s*(.+)", link_output)
        details["ssid"] = match.group(1).strip() if match else "Desconocido"

        match = re.search(r"freq:\s*(\d+)", link_output)
        details["frequency"] = f"{match.group(1)} MHz" if match else "Desconocida"

        match = re.search(r"signal:\s*(-?\d+)\s*dBm", link_output)
        details["signal"] = f"{match.group(1)} dBm" if match else "Desconocida"

        match = re.search(r"tx bitrate:\s*([^\n]+)", link_output)
        details["tx_bitrate"] = match.group(1).strip() if match else "Desconocido"

        match = re.search(r"rx bitrate:\s*([^\n]+)", link_output)
        details["rx_bitrate"] = match.group(1).strip() if match else "Desconocido"

        details["channel"] = get_current_channel(interface)
        return details
    except Exception:
        return None

def get_default_gateway(interface=None):
    output = run_argv(["ip", "route", "show", "default"])
    if interface:
        for line in output.splitlines():
            if interface in line:
                match = re.search(r"default via (\S+)", line)
                if match:
                    return match.group(1)
        return None
    match = re.search(r"default via (\S+)", output)
    return match.group(1) if match else None

def get_dns_servers():
    servers = []
    try:
        if command_exists("resolvectl"):
            output = run_argv(["resolvectl", "status"])
            if output:
                for line in output.splitlines():
                    match = re.search(r"DNS Servers:\s*(.+)", line)
                    if match:
                        servers.extend(match.group(1).split())
        if not servers:
            output = run_argv(["cat", "/etc/resolv.conf"])
            if output:
                for line in output.splitlines():
                    if line.strip().startswith("nameserver"):
                        parts = line.split()
                        if len(parts) > 1:
                            servers.append(parts[1])
        seen = set()
        unique = []
        for server in servers:
            if server not in seen:
                seen.add(server)
                unique.append(server)
        return unique
    except Exception:
        return []

def check_internet(timeout_seconds=4):
    try:
        code, _ = run_result_argv(["ping", "-c", "1", "-W", str(timeout_seconds), "8.8.8.8"])
        return code == 0
    except Exception:
        return False

def check_dns(hostname="google.com", timeout_seconds=4):
    try:
        if command_exists("getent"):
            code, _ = run_result_argv(["getent", "hosts", hostname])
            if code == 0:
                return True
        if command_exists("nslookup"):
            code, _ = run_result_argv(["timeout", str(timeout_seconds), "nslookup", hostname])
            return code == 0
        return False
    except Exception:
        return False

def current_connection_info():
    header("INFORMACIÓN DE CONEXIÓN ACTUAL")

    interface = get_wireless_interface()
    if not interface:
        err("No se detectó una interfaz Wi-Fi.")
        pause()
        return

    details = get_connection_details(interface)
    if not details:
        warn(f"{interface} no está conectada a ninguna red Wi-Fi.")
        pause()
        return

    info("SSID:", details["ssid"], WHITE)
    info("BSSID:", details["bssid"], BLUE)
    info("Frecuencia:", details["frequency"], BLUE)
    info("Canal:", details["channel"], BLUE)
    info("Señal:", details["signal"], YELLOW)
    info("RX bitrate:", details["rx_bitrate"], GREEN)
    info("TX bitrate:", details["tx_bitrate"], GREEN)
    print()

    ip4 = get_ipv4(interface) or "Sin IPv4"
    gateway = get_default_gateway(interface) or "No detectado"
    dns_servers = get_dns_servers()

    info("IPv4:", ip4, WHITE)
    info("Gateway:", gateway, WHITE)
    info("DNS:", ", ".join(dns_servers) if dns_servers else "No detectado", WHITE)

    print()
    separator()
    print(f"{WHITE}{WHITE}PRUEBAS{RESET}")
    separator()

    print(f"\n{YELLOW}Comprobando conectividad por etapas...{RESET}\n")
    internet_ok = check_internet()
    dns_ok = check_dns()

    def stage(label, passed):
        icon = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"{WHITE}{label:<16}{RESET} {icon}")

    stage("Wi-Fi", True)
    stage("IPv4", ip4 != "Sin IPv4")
    stage("Gateway", gateway != "No detectado")
    stage("DNS configurado", bool(dns_servers))
    stage("Internet (IP)", internet_ok)
    stage("Resolución DNS", dns_ok)

    print()
    if internet_ok and dns_ok:
        ok("¡Internet funcionando correctamente!")
    elif internet_ok and not dns_ok:
        warn("Hay conectividad IP, pero el DNS no resuelve nombres de dominio.")
    elif not internet_ok and gateway == "No detectado":
        err("No hay gateway configurado; probablemente el router no asignó ruta por DHCP.")
    else:
        err("Sin conectividad a Internet.")

    pause()

# ============================================================
# DRIVER
# ============================================================

def detailed_driver_info():
    header("INFORMACIÓN DEL DRIVER")
    interface = get_wireless_interface()
    if not interface:
        err("No se detectó el adaptador Wi-Fi."); pause(); return
    info("Interfaz:", interface, BLUE)
    info("Driver:", get_driver(interface), GREEN)
    info("Versión:", get_driver_version(interface), YELLOW)
    info("Firmware:", get_firmware(interface), YELLOW)
    print()
    output = run_argv(["ethtool", "-i", interface])
    if output: print(f"{WHITE}{output}{RESET}")
    pause()

def is_driver_compatible(driver, chipset):
    patterns = COMPATIBLE_DRIVER_PATTERNS.get(chipset, [])
    if not patterns or driver == "Desconocido":
        return False
    return any(re.search(pattern, driver, re.IGNORECASE) for pattern in patterns)

def verify_driver():
    header("VERIFICAR COMPATIBILIDAD")
    adapter = get_adapter_info()
    interface = get_wireless_interface()
    info("USB ID:", adapter['usb_id'], BLUE)
    info("Modelo:", adapter['model'], BLUE)
    info("Chipset:", adapter['chipset'], BLUE)

    if not interface:
        err("No hay interfaz Wi-Fi disponible.")
        pause()
        return

    driver = get_driver(interface)
    info("Driver cargado (ethtool):", driver, GREEN)

    chipset = adapter.get("chipset", "Desconocido")
    patterns = COMPATIBLE_DRIVER_PATTERNS.get(chipset, [])

    if driver == "Desconocido":
        warn("No se pudo leer el driver vía ethtool.")
    elif not patterns:
        warn(f"No hay patrones de compatibilidad registrados para el chipset {chipset}.")
        info("Revisa manualmente si", driver, YELLOW)
    elif is_driver_compatible(driver, chipset):
        ok(f"El driver cargado es compatible con el chipset {chipset}.")
    else:
        warn(f"El driver cargado no coincide con los patrones esperados para {chipset}.")
        info("Patrones esperados:", ", ".join(patterns), YELLOW)
        info("Esto no necesariamente es un error;", "revisa si el adaptador funciona bien igual.", WHITE)

    pause()

def repair_driver():
    header("REINSTALAR FIRMWARE")
    adapter = get_adapter_info()
    interface = get_wireless_interface()
    info("Modelo:", adapter['model'], BLUE)
    info("Chipset:", adapter['chipset'], BLUE)
    if interface:
        info("Driver actual:", get_driver(interface), GREEN)
    else:
        info("Driver actual:", "No detectado", RED)
    print()
    if adapter["usb_id"] not in ADAPTER_DATABASE:
        err("Adaptador no registrado en la base de datos.")
        warn("No se instalará un driver desconocido automáticamente.")
        pause(); return
    if interface:
        driver = get_driver(interface)
        chipset = adapter.get("chipset", "Desconocido")
        if is_driver_compatible(driver, chipset) or driver == adapter["driver"]:
            ok(f"El driver correcto ya está cargado: {driver}")
    print()
    info("Paquete:", adapter['package'], BLUE)
    warn("Esto reinstala el paquete de FIRMWARE, no el módulo del kernel.")
    choice = input(f"\n{YELLOW}>{RESET} {WHITE}¿Reinstalar firmware? (s/n):{RESET} ").strip().lower()
    if choice != "s":
        warn("Operación cancelada."); pause(); return
    print(f"\n{YELLOW}Actualizando paquetes...{RESET}")
    code, output = run_result_argv(["sudo", "apt", "update"])
    if code != 0:
        err("Error durante apt update.")
        if output: print(output)
        pause(); return
    print(f"\n{YELLOW}Instalando firmware...{RESET}")
    code, output = run_result_argv(["sudo", "apt", "install", "--reinstall", "-y", adapter['package']])
    if code == 0:
        ok("Firmware instalado/reinstalado correctamente.")
    else:
        err("No se pudo completar la instalación.")
        if output: print(output)
    pause()

def driver_menu():
    while True:
        header("DRIVER")
        print(f"{GREEN}[1]{RESET} Reinstalar firmware")
        print(f"{BLUE}[2]{RESET} Información detallada del driver")
        print(f"{BLUE}[3]{RESET} Verificar compatibilidad")
        print(f"{WHITE}[0] Regresar{RESET}")
        choice = input(f"\n{YELLOW}>{RESET} {WHITE}Selecciona:{RESET} ").strip()
        if choice == "1": repair_driver()
        elif choice == "2": detailed_driver_info()
        elif choice == "3": verify_driver()
        elif choice == "0": return
        else: err("Opción inválida."); time.sleep(1)

# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def main_menu():
    while True:
        interface = get_wireless_interface()
        adapter = get_adapter_info()
        clear()
        print(f"{WHITE}{BANNER}{RESET}")
        separator()
        info("Adaptador:", interface or 'No detectado', BLUE)
        info("Modelo:", adapter['model'], BLUE)
        info("Chipset:", adapter['chipset'], BLUE)
        print()
        print(f"{GREEN}[1]{RESET} Información del adaptador")
        print(f"{BLUE}[2]{RESET} Modos soportados")
        print(f"{WHITE}[3]{RESET} Bandas y canales")
        print(f"{YELLOW}[4]{RESET} Estado del adaptador")
        print(f"{RED}[5]{RESET} Diagnóstico")
        print(f"{GREEN}[6]{RESET} Cambiar modo")
        print(f"{BLUE}[7]{RESET} Driver")
        print(f"{WHITE}[8]{RESET} Estado de red (todas las interfaces)")
        print(f"{YELLOW}[9]{RESET} Reparar conexión a Internet (Wi-Fi)")
        print(f"{BLUE}[10]{RESET} Información de conexión actual")
        print(f"{WHITE}[11]{RESET} Cambiar interfaz Wi-Fi administrada")
        print()
        print(f"{WHITE}[0] Salir{RESET}")
        choice = input(f"\n{YELLOW}>{RESET} {WHITE}Selecciona una opción:{RESET} ").strip()
        if choice == "1": adapter_information()
        elif choice == "2": supported_modes_menu()
        elif choice == "3": band_channel_menu()
        elif choice == "4": adapter_status()
        elif choice == "5": diagnostic()
        elif choice == "6": mode_menu()
        elif choice == "7": driver_menu()
        elif choice == "8": network_overview()
        elif choice == "9": reconnect_wifi()
        elif choice == "10": current_connection_info()
        elif choice == "11": change_managed_interface()
        elif choice == "0": exit_program()
        else: err("Opción inválida."); time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        exit_program()
    except Exception as e:
        print()
        err(f"Error inesperado: {e}")
        pause()
