def IPtoINT(ip):
    parts = ip.split(".")
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])


def INTtoIP(num):
    return f"{(num >> 24) & 255}.{(num >> 16) & 255}.{(num >> 8) & 255}.{num & 255}"


def calculate_subnets(network: str, segments: list[int]) -> dict:
    """Calculate VLSM subnets for given network and segment user counts.

    Args:
        network: Network in CIDR notation (e.g., "192.168.10.0/24").
        segments: List of user counts per segment.

    Returns:
        dict with success status, base_address, total_ips, and subnets list.
    """
    if not segments:
        return {"success": False, "message": "At least one segment is required."}

    try:
        ip_part, cidr_part = network.split("/")
        cidr = int(cidr_part)
    except (ValueError, AttributeError):
        return {"success": False, "message": "Invalid network format. Use x.x.x.x/xx"}

    if cidr < 0 or cidr > 32:
        return {"success": False, "message": "CIDR must be between 0 and 32."}

    ip_parts = ip_part.split(".")
    if len(ip_parts) != 4:
        return {"success": False, "message": "Invalid IP address format."}

    try:
        for part in ip_parts:
            p = int(part)
            if p < 0 or p > 255:
                raise ValueError
    except ValueError:
        return {"success": False, "message": "IP octets must be between 0 and 255."}

    ip_int = IPtoINT(ip_part)
    mask = ((1 << 32) - 1) << (32 - cidr)
    network_int = ip_int & mask
    broadcast_int = network_int + (1 << (32 - cidr)) - 1

    def calc_subnet_info(users):
        total_needed = users + 2
        subnet_size = 1
        while subnet_size < total_needed:
            subnet_size *= 2
        sub_cidr = 32
        size = subnet_size
        while size > 1:
            size >>= 1
            sub_cidr -= 1
        if users == 2 and sub_cidr != 30:
            sub_cidr = 30
            subnet_size = 4
        sub_mask = ((1 << 32) - 1) << (32 - sub_cidr)
        mask_octets = [
            (sub_mask >> 24) & 255,
            (sub_mask >> 16) & 255,
            (sub_mask >> 8) & 255,
            sub_mask & 255,
        ]
        return {
            "size": subnet_size,
            "cidr": sub_cidr,
            "mask": f"{mask_octets[0]}.{mask_octets[1]}.{mask_octets[2]}.{mask_octets[3]}",
            "usable": subnet_size - 2,
        }

    segs_with_indexes = [(i, users) for i, users in enumerate(segments)]
    segs_sorted = sorted(segs_with_indexes, key=lambda x: x[1], reverse=True)

    subnets = []
    current_ip = network_int
    max_ip = broadcast_int

    for og_index, users in segs_sorted:
        info = calc_subnet_info(users)
        if users <= 2 and info["size"] < 4:
            info["size"] = 4
            info["cidr"] = 30
            info["usable"] = 2

        if current_ip + info["size"] - 1 > max_ip:
            return {
                "success": False,
                "message": f"Not enough IP space for segment with {users} users. "
                           f"Need {info['size']} IPs but only {max_ip - current_ip + 1} remaining.",
            }

        subnet_net = current_ip
        subnet_broadcast = current_ip + info["size"] - 1
        first_usable = subnet_net + 1 if info["size"] > 2 else None
        last_usable = subnet_broadcast - 1 if info["size"] > 2 else None

        subnets.append({
            "OgIndex": og_index,
            "users": users,
            "network": INTtoIP(subnet_net),
            "broadcast": INTtoIP(subnet_broadcast),
            "cidr": info["cidr"],
            "mask": info["mask"],
            "size": info["size"],
            "usable": info["usable"],
            "FirstUsable": INTtoIP(first_usable) if first_usable else "N/A",
            "LastUsable": INTtoIP(last_usable) if last_usable else "N/A",
        })
        current_ip += info["size"]

    subnets.sort(key=lambda x: x["OgIndex"])

    return {
        "success": True,
        "base_address": INTtoIP(network_int),
        "total_ips": broadcast_int - network_int + 1,
        "subnets": subnets,
    }


# ── Exported aliases ────────────────────────────────────────
def ip_to_int(ip: str) -> int:
    return IPtoINT(ip)


def int_to_ip(num: int) -> str:
    return INTtoIP(num)


def parse_network(network: str) -> dict | None:
    try:
        ip_part, cidr_part = network.split("/")
        cidr = int(cidr_part)
    except (ValueError, AttributeError):
        return None

    if cidr < 0 or cidr > 32:
        return None

    ip_parts = ip_part.split(".")
    if len(ip_parts) != 4:
        return None

    try:
        for part in ip_parts:
            p = int(part)
            if p < 0 or p > 255:
                return None
    except ValueError:
        return None

    ip_int = IPtoINT(ip_part)
    mask = ((1 << 32) - 1) << (32 - cidr)
    network_int = ip_int & mask
    broadcast_int = network_int + (1 << (32 - cidr)) - 1

    return {
        "address": INTtoIP(network_int),
        "cidr": cidr,
        "NetworkInt": network_int,
        "BroadcastInt": broadcast_int,
    }


def calc_subnet_info(users: int) -> dict:
    total_needed = users + 2
    subnet_size = 1
    while subnet_size < total_needed:
        subnet_size *= 2
    sub_cidr = 32
    size = subnet_size
    while size > 1:
        size >>= 1
        sub_cidr -= 1
    if users == 2 and sub_cidr != 30:
        sub_cidr = 30
        subnet_size = 4
    sub_mask = ((1 << 32) - 1) << (32 - sub_cidr)
    mask_octets = [
        (sub_mask >> 24) & 255,
        (sub_mask >> 16) & 255,
        (sub_mask >> 8) & 255,
        sub_mask & 255,
    ]
    return {
        "size": subnet_size,
        "cidr": sub_cidr,
        "mask": f"{mask_octets[0]}.{mask_octets[1]}.{mask_octets[2]}.{mask_octets[3]}",
        "usable": subnet_size - 2,
    }


def allocate_subnets(base_network: dict, segments: list[int]) -> list[dict] | None:
    segs_with_indexes = [(i, users) for i, users in enumerate(segments)]
    segs_sorted = sorted(segs_with_indexes, key=lambda x: x[1], reverse=True)

    subnets = []
    current_ip = base_network["NetworkInt"]
    max_ip = base_network["BroadcastInt"]

    for og_index, users in segs_sorted:
        info = calc_subnet_info(users)
        if users <= 2 and info["size"] < 4:
            info["size"] = 4
            info["cidr"] = 30
            info["usable"] = 2

        if current_ip + info["size"] - 1 > max_ip:
            return None

        subnet_net = current_ip
        subnet_broadcast = current_ip + info["size"] - 1
        first_usable = subnet_net + 1 if info["size"] > 2 else None
        last_usable = subnet_broadcast - 1 if info["size"] > 2 else None

        subnets.append({
            "OgIndex": og_index,
            "users": users,
            "network": INTtoIP(subnet_net),
            "broadcast": INTtoIP(subnet_broadcast),
            "cidr": info["cidr"],
            "mask": info["mask"],
            "size": info["size"],
            "usable": info["usable"],
            "FirstUsable": INTtoIP(first_usable) if first_usable else "N/A",
            "LastUsable": INTtoIP(last_usable) if last_usable else "N/A",
        })
        current_ip += info["size"]

    subnets.sort(key=lambda x: x["OgIndex"])
    return subnets
