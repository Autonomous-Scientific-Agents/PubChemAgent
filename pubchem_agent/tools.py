"""
PubChem Tools for LangChain Agent
Wraps pubchempy functions for use with LangGraph agents
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional, Union

from langchain.tools import tool
from pydantic import BaseModel, Field

# Add the external directory to the path to import pubchempy
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'external'))
import pubchempy as pcp


class CompoundSearchInput(BaseModel):
    """Input for compound search tool"""
    identifier: str = Field(description="The compound identifier (name, CID, SMILES, InChI, etc.)")
    namespace: str = Field(default="name", description="The type of identifier: name, cid, smiles, inchi, inchikey, or formula")
    search_type: Optional[str] = Field(default=None, description="Advanced search type: substructure, superstructure, or similarity")


class PropertiesInput(BaseModel):
    """Input for properties retrieval tool"""
    properties: List[str] = Field(description="List of properties to retrieve")
    identifier: str = Field(description="The compound identifier")
    namespace: str = Field(default="name", description="The type of identifier")


class SynonymsInput(BaseModel):
    """Input for synonyms tool"""
    identifier: str = Field(description="The compound identifier")
    namespace: str = Field(default="name", description="The type of identifier")


@tool("search_compounds", args_schema=CompoundSearchInput)
def search_compounds(identifier: str, namespace: str = "name", search_type: Optional[str] = None) -> str:
    """
    Search for chemical compounds in PubChem database.
    
    Args:
        identifier: The compound identifier (name, CID, SMILES, InChI, etc.)
        namespace: The type of identifier (name, cid, smiles, inchi, inchikey, formula)
        search_type: Advanced search type (substructure, superstructure, similarity)
    
    Returns:
        JSON string containing compound information
    """
    try:
        compounds = pcp.get_compounds(identifier, namespace=namespace, searchtype=search_type)
        
        if not compounds:
            return f"No compounds found for '{identifier}' with namespace '{namespace}'"
        
        results = []
        for compound in compounds[:5]:  # Limit to first 5 results
            result = {
                "cid": compound.cid,
                "molecular_formula": compound.molecular_formula,
                "molecular_weight": compound.molecular_weight,
                "canonical_smiles": compound.canonical_smiles,
                "iupac_name": compound.iupac_name,
                "synonyms": compound.synonyms[:5] if compound.synonyms else []  # First 5 synonyms
            }
            results.append(result)
        
        return json.dumps(results, indent=2)
    
    except Exception as e:
        return f"Error searching for compounds: {str(e)}"


@tool("get_compound_properties", args_schema=PropertiesInput)
def get_compound_properties(properties: List[str], identifier: str, namespace: str = "name") -> str:
    """
    Get specific properties for a compound.
    
    Args:
        properties: List of properties to retrieve (molecular_weight, xlogp, tpsa, etc.)
        identifier: The compound identifier
        namespace: The type of identifier
    
    Returns:
        JSON string containing the requested properties
    """
    try:
        # Map common property names to PubChem property names
        property_map = {
            "molecular_weight": "MolecularWeight",
            "molecular_formula": "MolecularFormula",
            "smiles": "SMILES",
            "inchi": "InChI",
            "inchikey": "InChIKey",
            "iupac_name": "IUPACName",
            "xlogp": "XLogP",
            "tpsa": "TPSA",
            "complexity": "Complexity",
            "h_bond_donor_count": "HBondDonorCount",
            "h_bond_acceptor_count": "HBondAcceptorCount",
            "rotatable_bond_count": "RotatableBondCount",
            "heavy_atom_count": "HeavyAtomCount"
        }
        
        # Map requested properties
        mapped_properties = []
        for prop in properties:
            mapped_prop = property_map.get(prop.lower(), prop)
            mapped_properties.append(mapped_prop)
        
        result = pcp.get_properties(mapped_properties, identifier, namespace=namespace)
        
        if not result:
            return f"No properties found for '{identifier}' with namespace '{namespace}'"
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error retrieving properties: {str(e)}"


@tool("get_compound_synonyms", args_schema=SynonymsInput)
def get_compound_synonyms(identifier: str, namespace: str = "name") -> str:
    """
    Get synonyms (alternative names) for a compound.
    
    Args:
        identifier: The compound identifier
        namespace: The type of identifier
    
    Returns:
        JSON string containing synonyms
    """
    try:
        synonyms = pcp.get_synonyms(identifier, namespace=namespace)
        
        if not synonyms:
            return f"No synonyms found for '{identifier}' with namespace '{namespace}'"
        
        # Extract synonyms from the result
        result = []
        for item in synonyms:
            if 'Synonym' in item:
                result.extend(item['Synonym'][:10])  # First 10 synonyms per item
        
        return json.dumps({"synonyms": result[:20]}, indent=2)  # Total limit of 20 synonyms
    
    except Exception as e:
        return f"Error retrieving synonyms: {str(e)}"


@tool("get_compound_structure")
def get_compound_structure(identifier: str, namespace: str = "name") -> str:
    """
    Get structural information for a compound including SMILES, InChI, and molecular formula.
    
    Args:
        identifier: The compound identifier
        namespace: The type of identifier
    
    Returns:
        JSON string containing structural information
    """
    try:
        compounds = pcp.get_compounds(identifier, namespace=namespace)
        
        if not compounds:
            return f"No compound found for '{identifier}' with namespace '{namespace}'"
        
        compound = compounds[0]
        structure_info = {
            "cid": compound.cid,
            "molecular_formula": compound.molecular_formula,
            "canonical_smiles": compound.canonical_smiles,
            "isomeric_smiles": compound.isomeric_smiles,
            "inchi": compound.inchi,
            "inchikey": compound.inchikey,
            "molecular_weight": compound.molecular_weight,
            "exact_mass": compound.exact_mass,
            "heavy_atom_count": compound.heavy_atom_count,
            "atom_stereo_count": compound.atom_stereo_count,
            "bond_stereo_count": compound.bond_stereo_count
        }
        
        return json.dumps(structure_info, indent=2)
    
    except Exception as e:
        return f"Error retrieving structure: {str(e)}"


@tool("get_compound_properties_detailed")
def get_compound_properties_detailed(identifier: str, namespace: str = "name") -> str:
    """
    Get detailed physicochemical properties for a compound.
    
    Args:
        identifier: The compound identifier
        namespace: The type of identifier
    
    Returns:
        JSON string containing detailed properties
    """
    try:
        compounds = pcp.get_compounds(identifier, namespace=namespace)
        
        if not compounds:
            return f"No compound found for '{identifier}' with namespace '{namespace}'"
        
        compound = compounds[0]
        properties = {
            "basic_info": {
                "cid": compound.cid,
                "molecular_formula": compound.molecular_formula,
                "molecular_weight": compound.molecular_weight,
                "exact_mass": compound.exact_mass,
                "charge": compound.charge
            },
            "structure": {
                "canonical_smiles": compound.canonical_smiles,
                "isomeric_smiles": compound.isomeric_smiles,
                "inchi": compound.inchi,
                "inchikey": compound.inchikey
            },
            "physicochemical": {
                "xlogp": compound.xlogp,
                "tpsa": compound.tpsa,
                "complexity": compound.complexity,
                "h_bond_donor_count": compound.h_bond_donor_count,
                "h_bond_acceptor_count": compound.h_bond_acceptor_count,
                "rotatable_bond_count": compound.rotatable_bond_count
            },
            "counts": {
                "heavy_atom_count": compound.heavy_atom_count,
                "atom_stereo_count": compound.atom_stereo_count,
                "bond_stereo_count": compound.bond_stereo_count,
                "covalent_unit_count": compound.covalent_unit_count
            }
        }
        
        return json.dumps(properties, indent=2)
    
    except Exception as e:
        return f"Error retrieving detailed properties: {str(e)}"


@tool("convert_identifier")
def convert_identifier(identifier: str, from_namespace: str, to_namespace: str) -> str:
    """
    Convert between different types of chemical identifiers.
    
    Args:
        identifier: The input identifier
        from_namespace: Source identifier type (name, cid, smiles, inchi, inchikey)
        to_namespace: Target identifier type (name, cid, smiles, inchi, inchikey)
    
    Returns:
        JSON string containing the converted identifier
    """
    try:
        compounds = pcp.get_compounds(identifier, namespace=from_namespace)
        
        if not compounds:
            return f"No compound found for '{identifier}' with namespace '{from_namespace}'"
        
        compound = compounds[0]
        
        # Get the requested identifier type
        if to_namespace == "cid":
            result = compound.cid
        elif to_namespace == "name":
            result = compound.synonyms[0] if compound.synonyms else "No name available"
        elif to_namespace == "smiles":
            result = compound.canonical_smiles
        elif to_namespace == "inchi":
            result = compound.inchi
        elif to_namespace == "inchikey":
            result = compound.inchikey
        elif to_namespace == "formula":
            result = compound.molecular_formula
        else:
            return f"Unsupported target namespace: {to_namespace}"
        
        return json.dumps({
            "input": identifier,
            "from": from_namespace,
            "to": to_namespace,
            "result": result
        }, indent=2)
    
    except Exception as e:
        return f"Error converting identifier: {str(e)}"


# List of all available tools
PUBCHEM_TOOLS = [
    search_compounds,
    get_compound_properties,
    get_compound_synonyms,
    get_compound_structure,
    get_compound_properties_detailed,
    convert_identifier
] 