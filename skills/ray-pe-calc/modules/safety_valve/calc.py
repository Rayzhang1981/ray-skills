#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safety relief valve orifice sizing per API 520 Part I (2014).
Supports gas/vapor, steam, and liquid service.

安全阀喉径计算器 - API 520 Part I
"""

import argparse
import math
import sys

# ============================================================
# Constants
# ============================================================
Patm = 101.325          # kPa
Kd_default = 0.975
Kb_default = 1.0
Kc_default = 1.0

# API 526 Standard Orifice Designations (mm^2)
ORIFICES = {
    "D": 71,    "E": 126,   "F": 198,   "G": 325,
    "H": 506,   "J": 830,   "K": 1186,  "L": 1841,
    "M": 2323,  "N": 2800,  "P": 4116,  "Q": 7129,
    "R": 10323, "T": 16774,
}

ORIFICE_ORDER = ["D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "T"]

# Typical inlet/outlet sizing recommendations
INLET_OUTLET = {
    "D":  "1\" x 2\" (DN25 x 50)",
    "E":  "1\" x 2\" (DN25 x 50)",
    "F":  "1.5\" x 3\" (DN40 x 80)",
    "G":  "1.5\" x 3\" (DN40 x 80)",
    "H":  "1.5\" x 3\" (DN40 x 80)",
    "J":  "2\" x 3\"  or  3\" x 4\"",
    "K":  "2\" x 3\"  or  3\" x 4\"",
    "L":  "2\" x 3\"  or  3\" x 4\"",
    "M":  "3\" x 4\"  or  4\" x 6\"",
    "N":  "3\" x 4\"  or  4\" x 6\"",
    "P":  "4\" x 6\"  or  6\" x 8\"",
    "Q":  "4\" x 6\"  or  6\" x 8\"",
    "R":  "4\" x 6\"  or  6\" x 8\"",
    "T":  "4\" x 6\"  or  6\" x 8\"",
}


def compute_C(k):
    """Compute the C coefficient for gas/vapor flow."""
    return 520 * math.sqrt(
        k * (2 / (k + 1)) ** ((k + 1) / (k - 1))
    )


def compute_P_cf(P1, k):
    """Compute critical flow pressure (kPa abs)."""
    return P1 * (2 / (k + 1)) ** (k / (k - 1))


def compute_F2(k, r):
    """Compute F2 coefficient for subcritical flow.
    r = P2/P1 (back pressure ratio)
    """
    if r >= 1.0:
        raise ValueError("Back pressure ratio P2/P1 >= 1.0, subcritical flow impossible")
    term = (k / (k - 1)) * (r ** (2 / k)) * ((1 - r ** ((k - 1) / k)) / (1 - r))
    if term <= 0:
        raise ValueError("F2 coefficient calculation error, check input parameters")
    return math.sqrt(term)


def calc_area_gas_critical(W, C, Kd, P1, Kb, Kc, Z, T_K, M_kgkmol):
    """Critical flow orifice area for gas/vapor (mm^2).
    API 520 Part I SI formula with unit conversion factor.
    """
    SI_FACTOR = 13160  # Converts USC formula to SI (W:kg/h, P1:kPa, T:K, M:kg/kmol -> A:mm^2)
    return SI_FACTOR * W / (C * Kd * P1 * Kb * Kc) * math.sqrt(Z * T_K / M_kgkmol)


def calc_area_gas_subcritical(W, F2, Kd, Kc, Z, T_K, M_kgkmol, P1, P2):
    """Subcritical flow orifice area for gas/vapor (mm^2)."""
    return W / (735 * F2 * Kd * Kc) * math.sqrt(Z * T_K / (M_kgkmol * P1 * (P1 - P2)))


def calc_area_steam(W, Kd, P1, Kb, Kc, Kn, Ksh):
    """Orifice area for steam (mm^2).
    API 520 Part I, saturated steam, SI units."""
    return 190.4 * W / (Kd * P1 * Kb * Kc * Kn * Ksh)


def calc_area_liquid(Q, Kd, Kw, Kc, Kv, rho, P1, P2):
    """Orifice area for liquid (mm^2).
    API 520 Part I, Q in m^3/h, P in kPa, rho in kg/m^3."""
    return 196.3 * Q / (38 * Kd * Kw * Kc * Kv) * math.sqrt(rho / (P1 - P2))


def select_orifice(area_mm2):
    """Select API standard orifice designation.
    Returns (designation, area_mm2, margin_percent, recommended).
    recommended may differ from designation if margin < 20%.
    """
    selected = None
    selected_area = None
    for desig in ORIFICE_ORDER:
        if ORIFICES[desig] >= area_mm2:
            selected = desig
            selected_area = ORIFICES[desig]
            break

    if selected is None:
        return "T", ORIFICES["T"], 0.0, "T"

    margin = (selected_area - area_mm2) / selected_area * 100

    if margin < 20:
        idx = ORIFICE_ORDER.index(selected)
        if idx + 1 < len(ORIFICE_ORDER):
            next_desig = ORIFICE_ORDER[idx + 1]
            return selected, selected_area, margin, next_desig

    return selected, selected_area, margin, selected


def format_float(val, decimals=2):
    return f"{val:.{decimals}f}"


def print_banner():
    print("=" * 70)
    print("Safety Valve Orifice Sizing (API 520 Part I)")
    print("=" * 70)


def print_footer():
    print("=" * 70)
    print("[!] Sizing notes:")
    print("  1. Preliminary calculation - verify with manufacturer data")
    print("  2. Inlet pressure drop <= 3% of set pressure (GB/T 150.1)")
    print("  3. Outlet back pressure <= 10% of set pressure (conventional PRV)")
    print("=" * 70)


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Safety Valve Orifice Sizing - API 520 Part I (2014)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Gas critical flow
  python calc.py --fluid gas --rate 5000 --unit kg/h --mw 92.14 --k 1.1 --T 200 --pset 500

  # Gas subcritical flow (high back pressure)
  python calc.py --fluid gas --rate 5000 --unit kg/h --mw 28 --k 1.4 --T 100 --pset 500 --pbp 300

  # Steam
  python calc.py --fluid steam --rate 10000 --unit kg/h --T 200 --pset 1000

  # Liquid
  python calc.py --fluid liquid --rate 50 --unit m3/h --rho 1000 --pset 500
        """,
    )

    parser.add_argument("--fluid", type=str, required=True,
                        choices=["gas", "steam", "liquid"],
                        help="Fluid type: gas, steam, liquid")

    parser.add_argument("--rate", type=float, required=True,
                        help="Relieving rate")
    parser.add_argument("--unit", type=str, default="kg/h",
                        choices=["kg/h", "m3/h"],
                        help="Rate unit (default: kg/h; liquid uses m3/h)")

    # Gas-only
    parser.add_argument("--mw", type=float, default=None,
                        help="Molecular weight, g/mol (gas/vapor)")
    parser.add_argument("--k", type=float, default=None,
                        help="Specific heat ratio Cp/Cv (gas)")
    parser.add_argument("--T", type=float, default=None,
                        help="Relieving temperature, deg C (gas/steam)")
    parser.add_argument("--Z", type=float, default=1.0,
                        help="Compressibility factor (gas, default 1.0)")

    # Pressure
    parser.add_argument("--pset", type=float, required=True,
                        help="Set pressure, kPaG")
    parser.add_argument("--pbp", type=float, default=0.0,
                        help="Back pressure, kPaG (default 0)")
    parser.add_argument("--ovp", type=float, default=10.0,
                        help="Overpressure, %% (default 10)")

    # Coefficients
    parser.add_argument("--kd", type=float, default=Kd_default,
                        help="Discharge coefficient (default %.3f)" % Kd_default)
    parser.add_argument("--kb", type=float, default=Kb_default,
                        help="Back pressure correction factor (default %.1f)" % Kb_default)
    parser.add_argument("--kc", type=float, default=Kc_default,
                        help="Bursting disc combination factor (default %.1f)" % Kc_default)

    # Steam
    parser.add_argument("--Ksh", type=float, default=1.0,
                        help="Superheat correction (steam, default 1.0)")
    parser.add_argument("--Kn", type=float, default=1.0,
                        help="Napier correction (steam, default 1.0)")

    # Liquid
    parser.add_argument("--rho", type=float, default=None,
                        help="Density, kg/m3 (liquid)")
    parser.add_argument("--viscosity", type=float, default=1.0,
                        help="Viscosity, cP (liquid, default 1.0)")
    parser.add_argument("--kw", type=float, default=1.0,
                        help="Liquid back pressure correction (default 1.0)")
    parser.add_argument("--kv", type=float, default=1.0,
                        help="Liquid viscosity correction (default 1.0)")

    args = parser.parse_args()

    # ========================
    # Validate required params
    # ========================
    if args.fluid == "gas":
        if args.mw is None:
            print("[ERROR] Gas calculation requires --mw (molecular weight, g/mol)")
            sys.exit(1)
        if args.k is None:
            print("[ERROR] Gas calculation requires --k (specific heat ratio Cp/Cv)")
            print()
            print("Common specific heat ratios (k = Cp/Cv):")
            print("  Air:            1.40")
            print("  Steam:          1.33")
            print("  Methane (CH4):  1.31")
            print("  Ethane (C2H6):  1.19")
            print("  Propane (C3H8): 1.13")
            print("  Toluene (C7H8): 1.09")
            print("  Benzene (C6H6): 1.12")
            sys.exit(1)
        if args.T is None:
            print("[ERROR] Gas calculation requires --T (relieving temperature, deg C)")
            sys.exit(1)

    if args.fluid == "steam" and args.T is None:
        print("[ERROR] Steam calculation requires --T (relieving temperature, deg C)")
        sys.exit(1)

    if args.fluid == "liquid" and args.rho is None:
        print("[ERROR] Liquid calculation requires --rho (density, kg/m3)")
        sys.exit(1)

    # ========================
    # Compute
    # ========================
    print_banner()
    print("[Input Parameters]")

    # Gauge to absolute pressure conversion
    P1 = (args.pset * (100 + args.ovp) / 100) + Patm   # kPa abs
    P2 = args.pbp + Patm                                 # kPa abs

    if args.fluid == "gas":
        print("  Fluid type: Gas/Vapor")
        print("  Molecular weight: %.2f g/mol" % args.mw)
        print("  Specific heat ratio k: %.2f" % args.k)
        print("  Relieving temperature: %.1f deg C" % args.T)
        print("  Compressibility Z: %.2f" % args.Z)
    elif args.fluid == "steam":
        print("  Fluid type: Steam")
        print("  Relieving temperature: %.1f deg C" % args.T)
    elif args.fluid == "liquid":
        print("  Fluid type: Liquid")
        print("  Density: %.1f kg/m3" % args.rho)
        print("  Viscosity: %.1f cP" % args.viscosity)

    print("  Set pressure: %.1f kPaG" % args.pset)
    print("  Back pressure: %.1f kPaG" % args.pbp)
    print("  Overpressure: %.1f%%" % args.ovp)
    print("  Relieving rate: %.1f %s" % (args.rate, args.unit))
    print("  Discharge coeff Kd: %.3f" % args.kd)

    print()
    print("[Results]")
    print("  Relieving pressure P1: %s kPa(a)" % format_float(P1))
    print("  Back pressure P2: %s kPa(a)" % format_float(P2))

    area_mm2 = 0.0
    flow_regime = ""

    if args.fluid == "gas":
        k = args.k
        T_K = args.T + 273.15
        M_kgkmol = args.mw  # g/mol == kg/kmol (same numerical value)
        W = args.rate

        C = compute_C(k)
        P_cf = compute_P_cf(P1, k)

        print("  C coefficient: %s" % format_float(C))
        print("  Critical pressure P_cf: %s kPa(a)" % format_float(P_cf))

        if P2 <= P_cf:
            flow_regime = "Critical flow (P_back <= P_cf)"
            area_mm2 = calc_area_gas_critical(W, C, args.kd, P1, args.kb, args.kc,
                                              args.Z, T_K, M_kgkmol)
        else:
            flow_regime = "Subcritical flow (P_back > P_cf)"
            r = P2 / P1
            F2 = compute_F2(k, r)
            print("  Back pressure ratio r = P2/P1: %s" % format_float(r, 4))
            print("  F2 coefficient: %s" % format_float(F2, 4))
            area_mm2 = calc_area_gas_subcritical(W, F2, args.kd, args.kc,
                                                  args.Z, T_K, M_kgkmol, P1, P2)

        print("  Flow regime: %s" % flow_regime)

    elif args.fluid == "steam":
        W = args.rate
        area_mm2 = calc_area_steam(W, args.kd, P1, args.kb, args.kc, args.Kn, args.Ksh)

    elif args.fluid == "liquid":
        Q = args.rate
        rho = args.rho
        area_mm2 = calc_area_liquid(Q, args.kd, args.kw, args.kc, args.kv, rho, P1, P2)

    print("  Required orifice area: %s mm^2" % format_float(area_mm2, 1))

    # ========================
    # Orifice Selection
    # ========================
    print()
    print("[Orifice Selection]")
    selected, sel_area, margin, recommended = select_orifice(area_mm2)

    if recommended != selected:
        rec_area = ORIFICES[recommended]
        rec_margin = (rec_area - area_mm2) / rec_area * 100
        print("  Nearest orifice: %s  (area %d mm^2, margin %s%%)" % (
            selected, sel_area, format_float(margin, 1)))
        print("  [!] Tight margin (<20%), recommend one size up")
        print("  Recommended orifice: %s  (area %d mm^2)" % (recommended, rec_area))
        print("  Margin: %s%%" % format_float(rec_margin, 1))
        final_orifice = recommended
        final_area = rec_area
    else:
        print("  Recommended orifice: %s  (area %d mm^2)" % (selected, sel_area))
        print("  Margin: %s%%" % format_float(margin, 1))
        final_orifice = selected
        final_area = sel_area

    nozzle_sizes = INLET_OUTLET.get(final_orifice, "Consult valve manufacturer")
    print("  Recommended nozzle size: %s" % nozzle_sizes)

    print_footer()


if __name__ == "__main__":
    main()
