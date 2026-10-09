# Material Microstructure Dataset (MMD)

A curated catalog of **3D microstructure and defect reconstructions of structural materials**
(X-ray CT, micro-CT, synchrotron CT, diffraction contrast tomography, HEDM/3DXRD, 3D EBSD and
serial sectioning). Each record links the 3D data to the material's **chemistry**, **processing
parameters**, **mechanical properties** and, where measured, **fatigue behaviour and fatigue crack
initiation sites**.

The catalog comes with a static web gallery for browsing, filtering and inspecting the records.

## Current contents

| | |
|---|---|
| Datasets (after de-duplication) | 134 |
| With downloadable (or partially downloadable) 3D data | 68 |
| Fatigue tested | 78 |
| Crack initiation site tracked in the 3D data | 61 |
| Rated *High* relevance for fatigue-initiation prediction | 56 |

Material classes: Ti alloys (33), Al alloys (25), Ni superalloys (24), fibre composites / MMC / CMC (23),
steels (19), Mg alloys (4), cast iron (2), Co alloys (2), Zr alloy (1), other (1).

Techniques: synchrotron CT, lab X-ray / micro-CT, phase-contrast CT, nano-CT, laminography, DCT
(synchrotron and lab), near- and far-field HEDM / 3DXRD, dark-field X-ray microscopy, 3D EBSD
(FIB, plasma FIB, TriBeam) and mechanical serial sectioning (Robo-Met.3D).

Notable public datasets include:

- **NIST AM Bench 2025-03**: L-PBF Ti-6Al-4V rotating-bending fatigue. XCT covers the full gauge section, and the pore that started each failure is identified ([10.18434/mds2-3734](https://doi.org/10.18434/mds2-3734)).
- **NIST L-PBF Ti-6Al-4V**: 15 HIP/heat treatments, with XCT and S-N data ([10.18434/mds2-3402](https://doi.org/10.18434/mds2-3402)).
- **NIST L-PBF IN718**: contour-pass surfaces with fatigue ([10.18434/mds2-3044](https://doi.org/10.18434/mds2-3044)), and a 25-parameter-set process–structure–property study ([10.18434/mds2-3083](https://doi.org/10.18434/mds2-3083)).
- **AM Bench 2022 IN718**: XCT spatially registered with serial-sectioning 3D EBSD ([10.18434/mds2-2767](https://doi.org/10.18434/mds2-2767)).
- **TomoBank Al 7075**: 4D synchrotron CT of corrosion-fatigue cracks growing from pits ([10.17038/XSD/1373575](https://doi.org/10.17038/XSD/1373575)).
- **IN718 TriBeam 3D EBSD**: with high-resolution DIC strain maps, on Dryad ([10.5061/dryad.83bk3j9sj](https://doi.org/10.5061/dryad.83bk3j9sj)).
- **DTU fatigue CT of glass-fibre composites**: on Zenodo.
- **AFRL HEDM and serial-sectioning challenge data**: on the Materials Data Facility.

## Repository layout

```
schema/record.schema.md   Record schema (fields, vocabularies, rules)
data/records/*.json       Source records, one file per research theme
  am_metals_ct.json         Additively manufactured metals – CT porosity & fatigue
  diffraction_3d.json       DCT / HEDM / 3DXRD grain-resolved studies
  ebsd_3d.json              3D EBSD and serial sectioning
  conventional_ct.json      Cast / wrought metals – CT & in-situ fatigue
  composites_ct.json        Fibre-reinforced polymers, CMCs, MMCs
  repository_sweep.json     Datasets found by sweeping data repositories
data/mmd.json             Merged, de-duplicated catalog (generated)
data/mmd.csv              Flat summary table (generated)
scripts/build.py          Validates and merges records, generates the site
site/gallery.template.html  Gallery source
site/index.html           Gallery page (generated; loads site/data/mmd.js)
site/mmd-gallery.html     Single-file gallery with data inlined (generated)
```

## Building and browsing

```bash
python3 scripts/build.py          # add --strict to fail on validation warnings
open site/index.html              # or serve the site/ folder, e.g. via GitHub Pages
```

### GitHub Pages

`.github/workflows/pages.yml` rebuilds the catalog and deploys the gallery to GitHub Pages on every
push to `main` (it can also be run manually from the Actions tab). One-time setup: in the repository's
**Settings → Pages**, set **Source** to **GitHub Actions**. The site is then served at
`https://danishabbir.github.io/MMD/`, with the catalog downloadable at `data/mmd.json` and `data/mmd.csv`.

The gallery offers:

- **Filters:** material class, technique, processing route and fatigue-initiation relevance; free-text search; and toggles for downloadable data, fatigue tested, initiation tracked in 3D, and in-situ loading.
- **Views:** a card view and a sortable table.
- **Record detail:** a panel for each record covering chemistry, processing, acquisition, defect statistics, mechanical and fatigue properties, data links and references.

Card thumbnails are schematic renderings (grain maps for diffraction/EBSD records, CT-like slices with pores for CT records). They are not the actual data.

## Adding records

1. Add objects that follow `schema/record.schema.md` to a file in `data/records/`.
2. Run `python3 scripts/build.py`. The build checks required fields and the class vocabulary. It merges duplicates that share a dataset DOI, or failing that the first paper DOI, filling gaps without overwriting.
3. Commit the source records together with the regenerated `data/` and `site/` outputs.

## Data quality notes

- Every value was taken from a source the curator opened: a paper, abstract, dataset landing page or repository API. Unknown values are `null`. Values that could not be confirmed are marked `(unverified)`.
- Many publisher full texts were paywalled. Those records rest on abstracts and metadata only, so their acquisition or loading details may be incomplete. Check the original paper before using any number.
- "Paper only (figures)" means no public 3D volume was found. The authors may still share data on request.
- Some ESRF sessions are listed as public but contain raw projections only and may require a portal login. Two promising ESRF fatigue-DCT datasets are under embargo until 2027–2029 and are not yet included: superalloy crack nucleation [10.15151/esrf-es-1915452043](https://doi.org/10.15151/esrf-es-1915452043), and multiaxial fatigue of AM IN625 [10.15151/esrf-es-2488108750](https://doi.org/10.15151/esrf-es-2488108750).

## Known gaps / next steps

- No public in-situ synchrotron fatigue CT volumes were found for AM metals. The in-situ AM studies are paper-only.
- Little coverage of 17-4PH, IN625 fatigue, Hastelloy X, maraging steel, welds and friction-stir welds, dual-phase and rail steels, HEAs, and Cu alloys.
- Grain-resolved fatigue studies (DCT/HEDM/3D EBSD) with crack initiation tracked in 3D are almost all paper-only. Requesting their data from the authors would add the most value for crack-initiation modelling.
