from typing import Dict, Any
import pandas as pd

def create_nested_structure(current_dict: Dict[str, Any], parts: list) -> Dict[str, Any]:
    """Crea una estructura anidada en el diccionario de propiedades."""
    for part in parts[:-1]:
        if part not in current_dict:
            current_dict[part] = {
                "type": "object",
                "properties": {},
                "required": []
            }
        current_dict = current_dict[part]["properties"]
    return current_dict

def add_required_field(section_properties: Dict[str, Any], parts: list) -> None:
    """Añade el campo como 'required'."""
    parent_dict = section_properties
    for part in parts[:-1]:
        parent_dict = parent_dict[part]
        if parts[-1] not in parent_dict.get("required", []):
            parent_dict.setdefault("required", []).append(parts[-1])

def process_field(row: pd.Series, section_properties: Dict[str, Any], section_required: list) -> None:
    """Procesa un solo campo del DataFrame."""
    field_name = row['field_name']
    field_type = row['field_type'].lower() if isinstance(row['field_type'], str) else 'string'
    question = row['question']
    is_required = str(row['required']).lower() in ['true', 'yes']

    field_schema = {"type": field_type, "description": question}

    if '.' in field_name:
        parts = field_name.split('.')
        current_dict = create_nested_structure(section_properties, parts)
        current_dict[parts[-1]] = field_schema
        if is_required:
            add_required_field(section_properties, parts)
    else:
        section_properties[field_name] = field_schema
        if is_required:
            section_required.append(field_name)

def generate_json_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """Genera un esquema JSON a partir de un DataFrame."""
    properties = {}
    required = []

    for section in df['section'].unique():
        section_df = df[df['section'] == section]
        section_properties = {}
        section_required = []

        for _, row in section_df.iterrows():
            process_field(row, section_properties, section_required)

        section_key = section.lower().replace(' ', '_')
        properties[section_key] = {
            "type": "object",
            "properties": section_properties
        }

        if section_required:
            properties[section_key]["required"] = section_required

        required.append(section_key)

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }
