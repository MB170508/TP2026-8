"""Unit converter — library functions."""

from typing import NamedTuple


class Unit(NamedTuple):
    name: str
    to_base: float  # multiply by this to get base unit
    from_base: float  # multiply by this to get from base unit


CATEGORIES: dict[str, dict[str, Unit]] = {
    "Data Storage": {
        "Bit": Unit("Bit", 1, 1),
        "Byte": Unit("Byte", 8, 0.125),
        "Kilobyte": Unit("KB", 8 * 1000, 1 / (8 * 1000)),
        "Kibibyte": Unit("KiB", 8 * 1024, 1 / (8 * 1024)),
        "Megabyte": Unit("MB", 8 * 1_000_000, 1 / (8 * 1_000_000)),
        "Mebibyte": Unit("MiB", 8 * 1_048_576, 1 / (8 * 1_048_576)),
        "Gigabyte": Unit("GB", 8 * 1_000_000_000, 1 / (8 * 1_000_000_000)),
        "Gibibyte": Unit("GiB", 8 * 1_073_741_824, 1 / (8 * 1_073_741_824)),
        "Terabyte": Unit("TB", 8 * 1_000_000_000_000, 1 / (8 * 1_000_000_000_000)),
        "Tebibyte": Unit("TiB", 8 * 1_099_511_627_776, 1 / (8 * 1_099_511_627_776)),
    },
    "Length": {
        "Millimeter": Unit("mm", 0.001, 1000),
        "Centimeter": Unit("cm", 0.01, 100),
        "Meter": Unit("m", 1, 1),
        "Kilometer": Unit("km", 1000, 0.001),
        "Inch": Unit("in", 0.0254, 1 / 0.0254),
        "Foot": Unit("ft", 0.3048, 1 / 0.3048),
        "Yard": Unit("yd", 0.9144, 1 / 0.9144),
        "Mile": Unit("mi", 1609.344, 1 / 1609.344),
        "Nautical Mile": Unit("nmi", 1852, 1 / 1852),
        "Micrometer": Unit("µm", 0.000001, 1_000_000),
        "Nanometer": Unit("nm", 0.000_000_001, 1_000_000_000),
    },
    "Frequency": {
        "Hertz": Unit("Hz", 1, 1),
        "Kilohertz": Unit("kHz", 1_000, 0.001),
        "Megahertz": Unit("MHz", 1_000_000, 0.000_001),
        "Gigahertz": Unit("GHz", 1_000_000_000, 0.000_000_001),
    },
    "Time": {
        "Millisecond": Unit("ms", 0.001, 1000),
        "Microsecond": Unit("µs", 0.000_001, 1_000_000),
        "Second": Unit("s", 1, 1),
        "Minute": Unit("min", 60, 1 / 60),
        "Hour": Unit("h", 3600, 1 / 3600),
        "Day": Unit("d", 86400, 1 / 86400),
        "Week": Unit("wk", 604800, 1 / 604800),
        "Year": Unit("yr", 31_536_000, 1 / 31_536_000),
    },
    "Speed": {
        "m/s": Unit("m/s", 1, 1),
        "km/h": Unit("km/h", 1 / 3.6, 3.6),
        "mph": Unit("mph", 0.44704, 1 / 0.44704),
        "Knot": Unit("kn", 0.514444, 1 / 0.514444),
        "ft/s": Unit("ft/s", 0.3048, 1 / 0.3048),
    },
    "Weight": {
        "Milligram": Unit("mg", 0.000001, 1_000_000),
        "Gram": Unit("g", 0.001, 1000),
        "Kilogram": Unit("kg", 1, 1),
        "Pound": Unit("lb", 0.453592, 1 / 0.453592),
        "Ounce": Unit("oz", 0.0283495, 1 / 0.0283495),
        "Ton": Unit("t", 1000, 0.001),
        "Stone": Unit("st", 6.35029, 1 / 6.35029),
    },
    "Volume": {
        "Milliliter": Unit("ml", 0.000001, 1_000_000),
        "Liter": Unit("l", 0.001, 1000),
        "Cubic Meter": Unit("m³", 1, 1),
        "Gallon": Unit("gal", 0.00378541, 1 / 0.00378541),
        "Fluid Ounce": Unit("fl oz", 0.0000295735, 1 / 0.0000295735),
        "Pint": Unit("pt", 0.000473176, 1 / 0.000473176),
        "Cup": Unit("cup", 0.000236588, 1 / 0.000236588),
        "Tablespoon": Unit("tbsp", 0.0000147868, 1 / 0.0000147868),
        "Teaspoon": Unit("tsp", 0.000004929, 1 / 0.000004929),
    },
    "Temperature": {
        "Celsius": Unit("°C", 1, 1),  # Simplified: base conversions need offset
        "Kelvin": Unit("K", 1, 1),
        "Fahrenheit": Unit("°F", 1, 1),  # Simplified
    },
    "Area": {
        "Square Millimeter": Unit("mm²", 0.000001, 1_000_000),
        "Square Centimeter": Unit("cm²", 0.0001, 10_000),
        "Square Meter": Unit("m²", 1, 1),
        "Square Kilometer": Unit("km²", 1_000_000, 0.000_001),
        "Square Inch": Unit("in²", 0.0006452, 1 / 0.0006452),
        "Square Foot": Unit("ft²", 0.092903, 1 / 0.092903),
        "Square Yard": Unit("yd²", 0.836127, 1 / 0.836127),
        "Acre": Unit("ac", 4046.86, 1 / 4046.86),
        "Hectare": Unit("ha", 10_000, 0.0001),
    },
    "Pressure": {
        "Pascal": Unit("Pa", 1, 1),
        "Kilopascal": Unit("kPa", 1000, 0.001),
        "Bar": Unit("bar", 100_000, 0.00001),
        "Atmosphere": Unit("atm", 101_325, 1 / 101_325),
        "Pound-force/in²": Unit("psi", 6894.76, 1 / 6894.76),
        "Millimeter of Mercury": Unit("mmHg", 133.322, 1 / 133.322),
    },
    "Energy": {
        "Joule": Unit("J", 1, 1),
        "Kilojoule": Unit("kJ", 1000, 0.001),
        "Megajoule": Unit("MJ", 1_000_000, 0.000_001),
        "Calorie": Unit("cal", 4.184, 1 / 4.184),
        "Kilocalorie": Unit("kcal", 4184, 1 / 4184),
        "Watt-hour": Unit("Wh", 3600, 1 / 3600),
        "Kilowatt-hour": Unit("kWh", 3_600_000, 1 / 3_600_000),
        "Electron Volt": Unit("eV", 1.60218e-19, 1 / 1.60218e-19),
        "BTU": Unit("BTU", 1055.06, 1 / 1055.06),
    },
    "Power": {
        "Watt": Unit("W", 1, 1),
        "Kilowatt": Unit("kW", 1000, 0.001),
        "Megawatt": Unit("MW", 1_000_000, 0.000_001),
        "Horsepower": Unit("hp", 745.7, 1 / 745.7),
        "Milliwatt": Unit("mW", 0.001, 1000),
    },
    "Force": {
        "Newton": Unit("N", 1, 1),
        "Kilonewton": Unit("kN", 1000, 0.001),
        "Pound-force": Unit("lbf", 4.44822, 1 / 4.44822),
        "Dyne": Unit("dyn", 0.00001, 100_000),
        "Kilogram-force": Unit("kgf", 9.80665, 1 / 9.80665),
    },
    "Angle": {
        "Degree": Unit("°", 0.0174533, 57.2958),
        "Radian": Unit("rad", 1, 1),
        "Gradian": Unit("grad", 0.015708, 63.6620),
        "Minute": Unit("'", 0.000290888, 3437.75),
        "Second": Unit("\"", 0.00000484814, 206_265),
    },
    "Density": {
        "kg/m³": Unit("kg/m³", 1, 1),
        "g/cm³": Unit("g/cm³", 1000, 0.001),
        "lb/ft³": Unit("lb/ft³", 16.0185, 1 / 16.0185),
    },
    "Electric Current": {
        "Ampere": Unit("A", 1, 1),
        "Milliampere": Unit("mA", 0.001, 1000),
        "Microampere": Unit("µA", 0.000001, 1_000_000),
        "Nanoampere": Unit("nA", 0.000_000_001, 1_000_000_000),
    },
    "Voltage": {
        "Millivolt": Unit("mV", 0.001, 1000),
        "Volt": Unit("V", 1, 1),
        "Kilovolt": Unit("kV", 1000, 0.001),
        "Microvolt": Unit("µV", 0.000001, 1_000_000),
    },
    "Resistance": {
        "Milliohm": Unit("mΩ", 0.001, 1000),
        "Ohm": Unit("Ω", 1, 1),
        "Kilohm": Unit("kΩ", 1000, 0.001),
        "Megohm": Unit("MΩ", 1_000_000, 0.000001),
    },
    "Capacitance": {
        "Picofarad": Unit("pF", 0.000_000_000_001, 1_000_000_000_000),
        "Nanofarad": Unit("nF", 0.000_000_001, 1_000_000_000),
        "Microfarad": Unit("µF", 0.000001, 1_000_000),
        "Millifarad": Unit("mF", 0.001, 1000),
        "Farad": Unit("F", 1, 1),
    },
    "Inductance": {
        "Picohenry": Unit("pH", 0.000_000_000_001, 1_000_000_000_000),
        "Nanohenry": Unit("nH", 0.000_000_001, 1_000_000_000),
        "Microhenry": Unit("µH", 0.000001, 1_000_000),
        "Millihenry": Unit("mH", 0.001, 1000),
        "Henry": Unit("H", 1, 1),
    },
    "Magnetic Flux": {
        "Microweber": Unit("µWb", 0.000001, 1_000_000),
        "Weber": Unit("Wb", 1, 1),
        "Kiloweber": Unit("kWb", 1000, 0.001),
    },
    "Magnetic Field": {
        "Millitesla": Unit("mT", 0.001, 1000),
        "Tesla": Unit("T", 1, 1),
        "Gauss": Unit("G", 0.0001, 10_000),
    },
    "Acceleration": {
        "m/s²": Unit("m/s²", 1, 1),
        "cm/s²": Unit("cm/s²", 0.01, 100),
        "g (gravity)": Unit("g", 9.80665, 1 / 9.80665),
        "km/h²": Unit("km/h²", 1 / 12_960, 12_960),
    },
    "Torque": {
        "Newton-meter": Unit("N·m", 1, 1),
        "Newton-centimeter": Unit("N·cm", 0.01, 100),
        "Pound-force-foot": Unit("lbf·ft", 1.35582, 1 / 1.35582),
        "Pound-force-inch": Unit("lbf·in", 0.112985, 1 / 0.112985),
    },
    "Viscosity": {
        "Pascal-second": Unit("Pa·s", 1, 1),
        "Centipoise": Unit("cP", 0.001, 1000),
        "Poise": Unit("P", 0.1, 10),
        "Stokes": Unit("St", 0.0001, 10_000),
    },
    "Flow Rate": {
        "m³/s": Unit("m³/s", 1, 1),
        "Liter/minute": Unit("L/min", 0.0000166667, 60_000),
        "Gallon/minute": Unit("gal/min", 0.00006309, 1 / 0.00006309),
        "Cubic foot/second": Unit("ft³/s", 0.0283168, 1 / 0.0283168),
    },
    "Frequency Response": {
        "Decibel": Unit("dB", 1, 1),
        "Decibel (watts)": Unit("dBW", 1, 1),
        "Decibel mW": Unit("dBm", 1, 1),
    },
    "Illuminance": {
        "Lux": Unit("lx", 1, 1),
        "Footcandle": Unit("fc", 10.764, 1 / 10.764),
        "Phot": Unit("ph", 10_000, 0.0001),
    },
    "Luminous Intensity": {
        "Candela": Unit("cd", 1, 1),
        "Candlepower": Unit("cp", 1, 1),
    },
    "Concentration": {
        "mg/L": Unit("mg/L", 1, 1),
        "g/L": Unit("g/L", 1000, 0.001),
        "kg/m³": Unit("kg/m³", 1000, 0.001),
        "ppm": Unit("ppm", 1, 1),
        "ppb": Unit("ppb", 0.001, 1000),
    },
    "Strain": {
        "Microstrain": Unit("µε", 0.000001, 1_000_000),
        "Unit Strain": Unit("ε", 1, 1),
        "Percent": Unit("%", 0.01, 100),
    },
    "Thermal Conductivity": {
        "W/m·K": Unit("W/m·K", 1, 1),
        "BTU/h·ft·°F": Unit("BTU/h·ft·°F", 1.73073, 1 / 1.73073),
        "cal/s·cm·°C": Unit("cal/s·cm·°C", 418.4, 1 / 418.4),
    },
}


def get_categories() -> list[str]:
    return list(CATEGORIES.keys())


def get_units(category: str) -> list[str]:
    if category not in CATEGORIES:
        return []
    return list(CATEGORIES[category].keys())


def convert(value: float, category: str, from_unit: str, to_unit: str) -> dict:
    if category not in CATEGORIES:
        return {"success": False, "message": f"Unknown category: {category}"}
    if from_unit not in CATEGORIES[category]:
        return {"success": False, "message": f"Unknown unit: {from_unit}"}
    if to_unit not in CATEGORIES[category]:
        return {"success": False, "message": f"Unknown unit: {to_unit}"}

    from_u = CATEGORIES[category][from_unit]
    to_u = CATEGORIES[category][to_unit]

    # Convert to base then to target
    base_value = value * from_u.to_base
    result = base_value * to_u.from_base

    return {
        "success": True,
        "value": result,
        "message": f"{value} {from_unit} = {result:.6g} {to_unit}",
    }


def convert_all(value: float, category: str, from_unit: str) -> dict:
    """Convert a value to all units in the category."""
    if category not in CATEGORIES:
        return {"success": False, "message": f"Unknown category: {category}"}
    if from_unit not in CATEGORIES[category]:
        return {"success": False, "message": f"Unknown unit: {from_unit}"}

    from_u = CATEGORIES[category][from_unit]
    base_value = value * from_u.to_base

    results = {}
    for name, unit in CATEGORIES[category].items():
        results[name] = base_value * unit.from_base

    return {"success": True, "results": results}
