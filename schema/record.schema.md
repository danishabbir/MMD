# MMD record schema (one JSON object per dataset)

```json
{
  "id": "kebab-case-unique-id",
  "title": "Short descriptive title",
  "material_class": "one of: Ti alloy | Ni superalloy | Steel | Al alloy | Mg alloy | Cu alloy | Co alloy | Zr alloy | Cast iron | HEA/MPEA | Composite | Other",
  "material": "Alloy designation, e.g. Ti-6Al-4V (Grade 5)",
  "chemistry": {"basis": "wt% | at% | nominal", "composition": {"Al": 6.1, "V": 4.0, "Ti": "bal."}, "notes": ""},
  "processing": {
    "route": "e.g. L-PBF | EBM | DED | Wrought | Cast | Forged | Rolled | Weld | HIP | Powder metallurgy",
    "parameters": "free text: laser power, scan speed, hatch, layer thickness, build orientation, casting/rolling details",
    "heat_treatment": "free text",
    "surface_condition": "as-built / machined / polished ..."
  },
  "techniques": ["X-ray CT", "Micro-CT", "Synchrotron CT", "DCT", "HEDM/3DXRD", "3D EBSD", "Serial sectioning", "Laminography", "Phase-contrast CT", "Nano-CT", "PCT"],
  "acquisition": {
    "facility": "e.g. ESRF ID11, APS 1-ID, lab Zeiss Xradia 520",
    "voxel_size_um": 0.0,
    "volume_dimensions": "e.g. 2048x2048x1500 voxels or 1x1x1 mm",
    "in_situ": true,
    "notes": ""
  },
  "microstructure": {
    "features_resolved": ["grains", "orientations", "pores", "lack-of-fusion", "inclusions", "cracks", "twins", "phases", "precipitates"],
    "grain_size_um": "",
    "texture": "",
    "phases": ""
  },
  "defects": {
    "types": ["gas pores", "lack-of-fusion", "inclusions", "keyhole pores", "cracks", "surface roughness"],
    "statistics": "porosity %, max/mean defect size, sqrt(area), number density, sphericity, etc."
  },
  "mechanical_properties": {
    "yield_strength_MPa": null,
    "uts_MPa": null,
    "elongation_pct": null,
    "hardness": null,
    "modulus_GPa": null,
    "other": ""
  },
  "fatigue": {
    "tested": true,
    "test_type": "HCF | LCF | VHCF | crack growth | ultrasonic | four-point bending | in-situ",
    "loading": "axial/bending/torsion, R ratio, frequency, stress amplitude(s)",
    "results": "S-N data, cycles to failure, fatigue strength, da/dN",
    "crack_initiation": "where/why cracks initiated: pore, LOF defect, surface, inclusion, grain boundary, twin boundary, slip band; was the initiation site tracked in the 3D data?",
    "initiation_tracked_in_3d": true
  },
  "data_availability": {
    "status": "Public download | On request | Paper only (figures) | Partially public",
    "repository": "e.g. Zenodo, Materials Data Facility, NIST, Materials Commons, ESRF, Mendeley Data",
    "url": "direct dataset URL or DOI link",
    "doi": "dataset DOI if any",
    "size": "e.g. 120 GB",
    "format": "TIFF stack, HDF5, DREAM.3D (.dream3d), raw, ANG/CTF",
    "license": "CC-BY 4.0 etc."
  },
  "references": [{"citation": "Authors, Title, Journal Year", "doi": "10.xxxx/...", "url": "https://..."}],
  "tags": ["fatigue-initiation", "additive-manufacturing", "in-situ", "grain-scale", "porosity", "machine-learning-ready"],
  "fatigue_initiation_relevance": "High | Medium | Low",
  "notes": "anything else useful; mark uncertain values with (approx.) or (unverified)"
}
```

Rules: use `null` for unknown numbers; never invent values — if a value could not be verified from a source, omit it or mark it "(unverified)". Prefer datasets with downloadable 3D volumes.
