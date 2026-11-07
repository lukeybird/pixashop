# PixaShop by AIWebDesignFirm

PixaShop is an independent branded desktop image editor based on PhotoCraft. The product overlay is reproducible: the upstream image engine remains intact and internal Cargo crate names remain `photocraft-*` for compatibility. The app's display name, publisher, executable packaging, icons, website links, account activation and release channel use PixaShop.

## Current status

Implementation in progress. No tested installer has been published. Website activation/download routes must be deployed against the latest live aiwebdesignfirm.com source, not GitHub's stale main. Native compile and release checks are being verified; do not interpret the overlay as a customer release until installers and end-to-end activation pass.

## Prepare and build

Use a clean checkout for each release. The preparation step rewrites generated source and is deliberately not used to overwrite upstream engine history.

```sh
python -m pip install Pillow
python pixashop/prepare.py
cargo check -p photocraft
cargo test -p photocraft access::tests
cargo build --release -p photocraft
python pixashop/package.py
```

On macOS, add Rust targets `aarch64-apple-darwin` and `x86_64-apple-darwin`, then build both with `MACOSX_DEPLOYMENT_TARGET=11.0` before packaging. The initial package script creates unsigned/testing builds (macOS is ad-hoc signed), not notarized customer releases. Configure AIWebDesignFirm's own Apple Developer ID/notarization and Windows signing credentials for production. Never use upstream's certificates. HEIF support remains optional and is not enabled by these commands.

## Trial and account access

The app asks the production `/api/pixashop/device` endpoint for a short-lived pairing code. The customer signs in in their system browser at `/pixashop/activate`, confirms the code, and must have an active seven-day Stripe trial or eligible subscription. No password, card data, images or documents are sent by the desktop app. Only a random device token is stored locally; the server stores its SHA-256 digest. Pending pairing expires in ten minutes; activated devices expire in 90 days and can be revoked by the account owner. Access leases are capped at five minutes and use monotonic time. The app checks approximately every four minutes and requires an internet connection. A failed check never deletes local documents.

This is an application access gate, not tamper-proof DRM. The underlying engine/CLI is not a secure boundary against a local developer. The desktop control server is disabled. Standalone engine/CLI and web access need separate entitlement enforcement before they are sold as gated features. Test cancellation, trial expiration, outages and saving unsaved work before release. There is not an independent free trial started by the desktop: it follows the customer's existing Stripe trial, avoiding repeated trial resets per installation.

## Updates

Startup and Help → Check for Updates query only `lukeybird/pixashop` releases. They never install upstream PhotoCraft binaries. The initial update flow offers the new publisher-hosted download page and asks the customer to save their work and install the new version. Automatic in-place installation is disabled until a PixaShop-specific signed updater is implemented. Versioning uses the workspace version. Increment it before each independent release, build all supported platforms, verify activation and publish only after testing. GitHub's latest stable release drives the download route; drafts/prereleases are intentionally not offered to customers.

## Branding and notices

The icon is an original pixel-grid P from `pixashop/icons.py`; build-time generated icons replace the upstream app icons. Required upstream notices and third-party licenses remain in the package's `Licenses` folder. Upstream contributor credits are preserved. The overlay must not promote the modified app as an ArtCraft product.

## Website integration

Companion branch: `pixashop-trial-downloads` in `lukeybird/aiwebdesignfirm`. It adds `/pixashop`, `/pixashop/activate`, `/api/pixashop/device` and `/api/pixashop/download` without replacing existing builder code. Enable server-only `PIXASHOP_ENABLED=true` only after installers, Stripe verification, activation and cancellation are tested. It reuses the existing Stripe prices and seven-day trial; it does not create or change plans.

## Release checklist

- Recover/preserve the newer live website source and merge only the companion additions.
- Native compile, access-module tests, UI regression tests, layer checks and wasm checks pass.
- Inspect PixaShop title, start screen, About, footer, icon, support links and app identity.
- Trial/customer activation succeeds; expired/unpaid/revoked devices are denied within five minutes.
- Pending activation, account switching, network errors, saving and restarting preserve work.
- Installer upgrade preserves PixaShop preferences and documents and does not touch PhotoCraft installations.
- Sign/notarize customer installers and verify downloaded checksums.
- Build release assets with `pixashop-<version>-...` names; validate on real Mac/Windows systems.
- Publish a stable release, then enable downloads. No placeholder or upstream download links.
