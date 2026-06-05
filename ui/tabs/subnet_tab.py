"""IPv4 Subnet Calculator Tab."""

import flet as ft
from managers.IPv4Subnetting import SubnetCalculator
from utilities.validators import validate_ipv4_network, validate_positive_integer
from ..constants import ERROR_COLOR, BLUE_COLOR, CARD_BACKGROUND
from ..helpers import btn, section, sub, set_error


def create_subnet_tab(page: ft.Page) -> ft.Column:
    """Create IPv4 Subnet Calculator tab.

    Args:
        page: Flet page reference

    Returns:
        Column containing subnet calculator UI
    """
    subnet_calculator = SubnetCalculator()
    subnet_display = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    subnet_error = ft.Text("", size=12, color=ERROR_COLOR)
    subnet_result_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    network_input = ft.TextField(label="Network (e.g. 192.168.10.0/24)", width=280, content_padding=8)
    segment_input = ft.TextField(label="Users", width=100, keyboard_type=ft.KeyboardType.NUMBER, content_padding=8)

    def validate_network_field(e):
        """Real-time validation for network CIDR input."""
        if not e.control.value:
            subnet_error.value = ""
        else:
            is_valid, error_msg = validate_ipv4_network(e.control.value)
            subnet_error.value = error_msg if not is_valid else ""
        page.update()

    def validate_segment_field(e):
        """Real-time validation for user count input."""
        if not e.control.value:
            subnet_error.value = ""
        else:
            is_valid, error_msg = validate_positive_integer(e.control.value, max_val=1000)
            subnet_error.value = error_msg if not is_valid else ""
        page.update()

    network_input.on_change = validate_network_field
    segment_input.on_change = validate_segment_field

    def build_segments():
        subnet_display.controls.clear()
        segments = subnet_calculator.get_segments()["segments"]
        for i, u in enumerate(segments):
            subnet_display.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.ROUTER, size=14, color=BLUE_COLOR),
                    ft.Text(f"Segment {i+1}: {u} users", size=13),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=14,
                        on_click=lambda e, idx=i: remove_segment(idx),
                    ),
                ], spacing=8)
            )

    def add_segment(e):
        subnet_error.value = ""
        result = subnet_calculator.add_segment(segment_input.value)
        if result["success"]:
            segment_input.value = ""
            build_segments()
            subnet_result_col.controls.clear()
        else:
            subnet_error.value = result["message"]
        page.update()

    def remove_segment(idx):
        result = subnet_calculator.remove_segment(idx)
        if result["success"]:
            build_segments()
            subnet_result_col.controls.clear()
        else:
            subnet_error.value = result["message"]
        page.update()

    def calc_subnet(e):
        subnet_result_col.controls.clear()
        result = subnet_calculator.calculate_subnets(network_input.value)
        if not result["success"]:
            subnet_result_col.controls.append(ft.Text(result["message"], size=13, color=ERROR_COLOR))
            page.update()
            return

        subnet_result_col.controls.append(
            ft.Text(f"Base: {result['base_address']}  |  Total IPs: {result['total_ips']}",
                    size=13, weight=ft.FontWeight.W_600)
        )
        for i, s in enumerate(result["subnets"], 1):
            range_str = f"{s['FirstUsable']} - {s['LastUsable']}" if s['usable'] > 0 else "N/A"
            subnet_result_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Seg {i} — {s['users']} users", size=13, weight=ft.FontWeight.W_600),
                        ft.Text(f"Network: {s['network']}/{s['cidr']}  |  Mask: {s['mask']}", size=12),
                        ft.Text(f"Usable: {range_str} ({s['usable']} hosts)", size=12),
                    ], spacing=2),
                    padding=8,
                    border_radius=6,
                    bgcolor=CARD_BACKGROUND,
                )
            )
        page.update()

    def reset_subnet(e):
        result = subnet_calculator.reset()
        build_segments()
        subnet_result_col.controls.clear()
        network_input.value = ""
        segment_input.value = ""
        subnet_error.value = ""
        page.update()

    build_segments()

    return ft.Column([
        section("IPv4 Subnet Calculator"),
        sub("VLSM subnetting with custom segment requirements."),
        network_input,
        ft.Row([segment_input, btn("Add Segment", add_segment)]),
        subnet_error,
        ft.Container(content=subnet_display, expand=True),
        ft.Row([btn("Calculate", calc_subnet, primary=True), btn("Reset", reset_subnet)]),
        subnet_result_col,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)
