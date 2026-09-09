# -*- coding: utf-8 -*-
"""PubChem PUG-REST / PUG-View 公共抓取工具（无第三方依赖，仅 urllib）。

供 ray-chem-property 各脚本共享：名称/CAS 解析、结构化物性、GHS/NFPA/毒性/接触限值。

设计约定：
- 所有函数返回 dict，失败抛 RuntimeError 或返回 None（由调用方决定兜底）。
- 网络超时默认 20s，自动重试 2 次。
- 输出统一为 JSON 可序列化结构。
"""
import json
import time
import urllib.parse
import urllib.request

BASE = "https://pubchem.ncbi.nlm.nih.gov/rest"


def _get_json(url, retries=2, timeout=20):
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ray-chem-property/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < retries:
                time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"PubChem request failed: {url}\n{last}")


def name_to_cid(name):
    """名称/CAS/SMILES → CID。返回 int 或 None。"""
    q = urllib.parse.quote(name.strip())
    try:
        data = _get_json(f"{BASE}/pug/compound/name/{q}/cids/JSON")
        cids = data.get("IdentifierList", {}).get("CID", [])
        return int(cids[0]) if cids else None
    except RuntimeError:
        return None


def get_properties(cid, props):
    """按 CID 取结构化物性。props 为逗号分隔字符串。返回 dict 或 None。"""
    try:
        data = _get_json(
            f"{BASE}/pug/compound/cid/{cid}/property/{props}/JSON"
        )
        table = data.get("PropertyTable", {}).get("Properties", [])
        return table[0] if table else None
    except RuntimeError:
        return None


def get_pugview(cid, heading=None):
    """PUG-View 完整数据树。heading 可选，例如 'GHS Classification'。"""
    url = f"{BASE}/pug_view/data/compound/{cid}/JSON"
    if heading:
        url += "?heading=" + urllib.parse.quote(heading)
    try:
        return _get_json(url)
    except RuntimeError:
        return None


# ---- 常用物性集合 ----
IDENTIFIER_PROPS = "IUPACName,MolecularFormula,MolecularWeight,CanonicalSMILES,InChIKey,IsomericSMILES"

# PUG-REST 支持的实验物性（返回带单位字符串，需解析）
PHYSICAL_PROPS = ",".join([
    "MeltingPoint", "BoilingPoint", "Density", "VaporPressure",
    "FlashPoint", "AutoignitionTemp", "HeatOfVaporization",
    "HeatOfCombustion", "RefractiveIndex", "Solubility",
    "pH", "Viscosity", "Odor", "XLogP"
])
