from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SystemCommand:
    name: str
    command: str
    requires_sudo: bool = False
    timeout: int = 30


class SystemCommands:
    """Definitions of system commands used by the tool."""

    # USB commands
    LSUSB = SystemCommand("lsusb", "lsusb")
    LSUSB_VERBOSE = SystemCommand("lsusb_verbose", "lsusb -v")
    USB_DEVICES = SystemCommand("usb_devices", "usb-devices")

    # Driver commands
    ETHTOOL_INFO = SystemCommand("ethtool_info", "ethtool -i {}")
    LSMOD = SystemCommand("lsmod", "lsmod")
    MODINFO = SystemCommand("modinfo", "modinfo {}")

    # Interface commands
    IW_DEV = SystemCommand("iw_dev", "iw dev")
    IW_DEV_INFO = SystemCommand("iw_dev_info", "iw dev {} info")
    IP_LINK_SHOW = SystemCommand("ip_link_show", "ip link show {}")
    IP_ADDR_SHOW = SystemCommand("ip_addr_show", "ip addr show {}")

    # PHY commands
    IW_PHY_INFO = SystemCommand("iw_phy_info", "iw phy {} info")
    IW_LIST = SystemCommand("iw_list", "iw list")

    # Connection commands
    IW_DEV_LINK = SystemCommand("iw_dev_link", "iw dev {} link")

    # NetworkManager commands
    NMCLI_DEVICE_STATUS = SystemCommand("nmcli_device_status", "nmcli device status")
    NMCLI_DEVICE_SHOW = SystemCommand("nmcli_device_show", "nmcli device show {}")
    NMCLI_CONNECTION_SHOW = SystemCommand("nmcli_connection_show", "nmcli connection show")
    NMCLI_DEVICE_WIFI = SystemCommand("nmcli_device_wifi", "nmcli device wifi")
    NMCLI_DEVICE_DISCONNECT = SystemCommand("nmcli_device_disconnect", "nmcli device disconnect {}", requires_sudo=False)
    NMCLI_CONNECTION_UP = SystemCommand("nmcli_connection_up", "nmcli connection up {}", requires_sudo=False)
    NMCLI_DEVICE_WIFI_RESCAN = SystemCommand("nmcli_device_wifi_rescan", "nmcli device wifi rescan {}", requires_sudo=False)

    # Recovery commands
    IP_LINK_SET_UP = SystemCommand("ip_link_set_up", "ip link set {} up", requires_sudo=True)
    IP_LINK_SET_DOWN = SystemCommand("ip_link_set_down", "ip link set {} down", requires_sudo=True)
    RFKILL_LIST = SystemCommand("rfkill_list", "rfkill list")
    RFKILL_UNBLOCK_WIFI = SystemCommand("rfkill_unblock_wifi", "rfkill unblock wifi", requires_sudo=True)
    RFKILL_UNBLOCK_INDEX = SystemCommand("rfkill_unblock_index", "rfkill unblock {}", requires_sudo=True)
    MODPROBE = SystemCommand("modprobe", "modprobe {}", requires_sudo=True)
    MODPROBE_REMOVE = SystemCommand("modprobe_remove", "modprobe -r {}", requires_sudo=True)

    # Mode commands
    IW_DEV_SET_TYPE = SystemCommand("iw_dev_set_type", "iw dev {} set type {}", requires_sudo=True)

    # Logs commands
    DMESG = SystemCommand("dmesg", "dmesg")
    DMESG_T = SystemCommand("dmesg_t", "dmesg -T")
    JOURNALCTL_K = SystemCommand("journalctl_k", "journalctl -k")
    JOURNALCTL_NM = SystemCommand("journalctl_nm", "journalctl -u NetworkManager")

    # Route commands
    IP_ROUTE_SHOW = SystemCommand("ip_route_show", "ip route show")

    # System commands
    WHICH = SystemCommand("which", "which {}")
