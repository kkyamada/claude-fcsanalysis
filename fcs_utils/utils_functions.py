"""
Utility functions for FCS analysis
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from lxml import etree

import flowkit as fk
from flowkit._models.gating_strategy import GatingStrategy
from flowkit._models.gates._gml_gates import GMLQuadrantGate, GMLBooleanGate
from flowkit._utils.xml_utils import (
    _construct_gates,
    _construct_transforms,
    _construct_matrices,
)
from flowkit._utils.xml_common import find_attribute_value
import networkx as nx


# GatingML 2.0 namespaces
NS_GATING = "http://www.isac-net.org/std/Gating-ML/v2.0/gating"
NS_DATATYPE = "http://www.isac-net.org/std/Gating-ML/v2.0/datatypes"
NS_TRANSFORMS = "http://www.isac-net.org/std/Gating-ML/v2.0/transformations"

# Register namespaces to preserve prefixes on output
ET.register_namespace("gating", NS_GATING)
ET.register_namespace("data-type", NS_DATATYPE)
ET.register_namespace("transforms", NS_TRANSFORMS)


def parse_gating_xml_relaxed(xml_file_or_path) -> GatingStrategy:
    """
    Parse a GatingML 2.0 document without strict schema validation.

    This is a patched version of flowkit's parse_gating_xml that:
    1. Skips strict schema validation (allows non-standard attributes)
    2. Supports both FlowKit's parent_id attribute and standard <gating:parent> element

    Args:
        xml_file_or_path: file handle or file path to a GatingML 2.0 document

    Returns:
        GatingStrategy instance
    """
    xml_document = etree.parse(xml_file_or_path)
    root = xml_document.getroot()

    # Find namespaces
    gating_ns = None
    data_type_ns = None
    transform_ns = None

    for ns, url in root.nsmap.items():
        if url == 'http://www.isac-net.org/std/Gating-ML/v2.0/gating':
            gating_ns = ns
        elif url == 'http://www.isac-net.org/std/Gating-ML/v2.0/datatypes':
            data_type_ns = ns
        elif url == 'http://www.isac-net.org/std/Gating-ML/v2.0/transformations':
            transform_ns = ns

    if gating_ns is None:
        raise ValueError("GatingML namespace reference is missing from GatingML file")

    gating_strategy = GatingStrategy()

    gates = _construct_gates(root, gating_ns, data_type_ns)
    transformations = _construct_transforms(root, transform_ns, data_type_ns)
    comp_matrices = _construct_matrices(root, transform_ns, data_type_ns)

    # Patch: Also check for standard <gating:parent> element
    _patch_parent_references(root, gates, gating_ns)

    for c_id, c in comp_matrices.items():
        gating_strategy.add_comp_matrix(c_id, c)
    for t_id, t in transformations.items():
        gating_strategy.add_transform(t_id, t)

    deps = []
    quadrants = []

    for g_id, gate in gates.items():
        if gate.parent is None:
            parent = 'root'
        else:
            parent = gate.parent

        deps.append((parent, g_id))

        if isinstance(gate, GMLQuadrantGate):
            for q_id in gate.quadrants:
                deps.append((g_id, q_id))
                quadrants.append(q_id)

        if isinstance(gate, GMLBooleanGate):
            for g_ref in gate.gate_refs:
                deps.append((g_ref['ref'], g_id))

    dag = nx.DiGraph(deps)

    sorted_gate_ids = list(nx.topological_sort(dag))

    for g_id in sorted_gate_ids:
        # Skip 'root' node
        if g_id == 'root':
            continue

        if g_id in quadrants:
            continue

        gate = gates[g_id]

        # Get the full gate path from root to this gate's parent
        gate_path = tuple(nx.shortest_path(dag, 'root', g_id))[:-1]

        # Convert GML gate to regular gate and add to strategy
        gating_strategy.add_gate(gate.convert_to_parent_class(), gate_path)

    return gating_strategy


def _patch_parent_references(root, gates, gating_ns):
    """
    Patch gate parent references by checking for standard <gating:parent> elements.

    FlowKit's parser only looks for parent_id attribute. This function also checks
    for the GatingML 2.0 standard <gating:parent><gating:gateReference ref="..."/> element.
    """
    gate_types = [
        "RectangleGate",
        "PolygonGate",
        "EllipsoidGate",
        "QuadrantGate",
        "BooleanGate",
    ]

    for gate_type in gate_types:
        for gate_el in root.findall(f'{gating_ns}:{gate_type}', namespaces=root.nsmap):
            gate_id = find_attribute_value(gate_el, gating_ns, 'id')

            if gate_id not in gates:
                continue

            gate = gates[gate_id]

            # If parent already set via parent_id attribute, skip
            if gate.parent is not None:
                continue

            # Check for standard <gating:parent> element
            parent_el = gate_el.find(f'{gating_ns}:parent', namespaces=root.nsmap)
            if parent_el is not None:
                gate_ref_el = parent_el.find(f'{gating_ns}:gateReference', namespaces=root.nsmap)
                if gate_ref_el is not None:
                    parent_ref = find_attribute_value(gate_ref_el, gating_ns, 'ref')
                    if parent_ref:
                        gate.parent = parent_ref


def _sanitize_xml_id(name: str) -> str:
    """
    Sanitize a string to be a valid XML NCName (for xs:ID type).

    XML NCName rules:
    - Must start with letter or underscore
    - Can contain letters, digits, hyphens, underscores, periods
    - Cannot contain: +, spaces, colons, etc.
    """
    # Common replacements for flow cytometry naming conventions
    replacements = {
        '+': '_pos',
        '-': '_neg',  # Only replace standalone minus, not in ranges
        ' ': '_',
        ':': '_',
        '/': '_',
        '(': '_',
        ')': '_',
    }

    result = name
    for old, new in replacements.items():
        # Special handling for '-': only replace if it looks like a marker (e.g., "CD4-")
        # but not if it's part of a channel name (e.g., "FSC-A")
        if old == '-':
            # Replace trailing minus (marker negative) but not channel separators
            if result.endswith('-'):
                result = result[:-1] + '_neg'
        else:
            result = result.replace(old, new)

    # Ensure starts with letter or underscore
    if result and not (result[0].isalpha() or result[0] == '_'):
        result = '_' + result

    return result


def convert_gml_to_standard(
    input_path: str | Path,
    output_path: str | Path | None = None,
) -> None:
    """
    Convert FlowKit GatingML export to schema-compliant format.

    Fixes:
    1. Sanitizes gate IDs to be valid XML NCNames (xs:ID type)
    2. Updates parent_id references to match sanitized names

    Args:
        input_path: Path to the input GML file (FlowKit format)
        output_path: Path to save the converted GML file. If None, overwrites input file.
    """
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path
    else:
        output_path = Path(output_path)

    # Parse the XML
    tree = ET.parse(input_path)
    root = tree.getroot()

    # Gate types defined in GatingML 2.0
    gate_types = [
        "RectangleGate",
        "PolygonGate",
        "EllipsoidGate",
        "QuadrantGate",
        "BooleanGate",
    ]

    id_attr = f"{{{NS_GATING}}}id"
    parent_id_attr = f"{{{NS_GATING}}}parent_id"

    # Build mapping of old IDs to sanitized IDs
    id_mapping = {}
    for gate_type in gate_types:
        for gate_el in root.findall(f"{{{NS_GATING}}}{gate_type}"):
            if id_attr in gate_el.attrib:
                old_id = gate_el.attrib[id_attr]
                new_id = _sanitize_xml_id(old_id)
                if old_id != new_id:
                    id_mapping[old_id] = new_id

    # Apply sanitized IDs
    for gate_type in gate_types:
        for gate_el in root.findall(f"{{{NS_GATING}}}{gate_type}"):
            # Update gate ID
            if id_attr in gate_el.attrib:
                old_id = gate_el.attrib[id_attr]
                if old_id in id_mapping:
                    gate_el.attrib[id_attr] = id_mapping[old_id]

            # Update parent_id reference
            if parent_id_attr in gate_el.attrib:
                old_parent = gate_el.attrib[parent_id_attr]
                if old_parent in id_mapping:
                    gate_el.attrib[parent_id_attr] = id_mapping[old_parent]

    # Write the converted XML
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)
