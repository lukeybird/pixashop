# PixaShop

**by AIWebDesignFirm**

A native desktop image editor with layers, masks, brushes, selections, RAW support and familiar document workflows. PixaShop adds its own visual identity, trial-account activation, desktop packaging and release channel to the PhotoCraft image engine.

## Product implementation

See [pixashop/README.md](pixashop/README.md) for build instructions, activation protocol, release checks and current limitations.

The product overlay is applied at build time using `python pixashop/prepare.py`; the underlying Rust workspace keeps its existing package identifiers and file compatibility. Only builds from this fork are PixaShop builds. Never relabel a downloaded upstream executable.

**Status:** development. Customer installers and production website activation have not been published or verified yet. Initial CI packages are testing builds. Updates currently prompt customers to download a new installer; automatic installation is not enabled.

## Upstream

Based on [PhotoCraft](https://github.com/storytold/photocraft). Existing licenses, attribution and contributor notices are retained. See LICENSE-MIT, LICENSE-APACHE, NOTICE and ATTRIBUTION.md.
