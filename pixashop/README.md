## Current free-access candidate — 0.20.5

The production Pixa account service now grants free early access without a card or scheduled account expiration. This candidate updates the activation-screen wording and bundled manual to match. Sign-in, explicit device approval, short monotonic security leases and existing access guards remain in place. No billing endpoint, paid-service subscription, published installer or release setting is changed here. Build artifacts remain unsigned testing candidates until separate platform acceptance and signing. Historical release notes below describe earlier candidates and may refer to the former paid trial.

# PixaShop by AIWebDesignFirm

PixaShop is an independent branded desktop image editor based on PhotoCraft. The product overlay is reproducible: the upstream image engine remains intact and internal Cargo crate names remain `photocraft-*` for compatibility. The app's display name, publisher, executable packaging, icons, website links, account activation and release channel use PixaShop.

## Current status

Early-access installers are published at https://aiwebdesignfirm.com/pixashop. Native builds and access-module tests passed on Mac, Windows and Linux. Interactive desktop testing is incomplete. The published 0.20.1 Mac app was Developer ID signed and Apple notarized. New CI builds are ad-hoc testing builds until the publisher signs and notarizes them; Windows builds are unsigned. Preserve the newer live Vercel website source: GitHub website main remains stale.

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

On macOS, install `dmgbuild==1.6.7` with pip for the drag-to-Applications disk image layout. Add Rust targets `aarch64-apple-darwin` and `x86_64-apple-darwin`, then build both with `MACOSX_DEPLOYMENT_TARGET=11.0` before packaging. The package script creates unsigned/testing builds (macOS is ad-hoc signed), not notarized customer releases. Configure AIWebDesignFirm's own Apple Developer ID/notarization and Windows signing credentials for production. Never use upstream's certificates. HEIF support remains optional and is not enabled by these commands.

## Trial and account access

The app asks the production `/api/pixashop/device` endpoint for a short-lived pairing code. The customer signs in in their system browser at `/pixashop/activate`, confirms the code, and receives free Pixa early access without a card or scheduled account expiration. No password, card data, images or documents are sent by the desktop app. Only a random device token is stored locally; the server stores its SHA-256 digest. Pending pairing expires in ten minutes; activated devices expire in 90 days and can be revoked by the account owner. Access leases are capped at five minutes and use monotonic time. The app checks approximately every four minutes and requires an internet connection. A failed check never deletes local documents.

This is an application access gate, not tamper-proof DRM. The underlying engine/CLI is not a secure boundary against a local developer. The desktop control server is disabled. Standalone engine/CLI and web access need separate entitlement enforcement before they are sold as gated features. Test revocation, expired security leases, outages and saving unsaved work before release. The desktop does not create a billing trial. The production account service grants free early access; short security leases and explicit device approval remain enforced.

## Updates

Startup and Help → Check for Updates query only `lukeybird/pixashop` releases. They never install upstream PhotoCraft binaries. The Mac update flow offers **Install and restart**. It stages the publisher’s versioned universal DMG in a private Applications sibling folder, checks the release SHA-256 digest, verifies Developer ID team `945M5X4DY3`, bundle identity `com.aiwebdesignfirm.pixashop`, hardened runtime, expected version, and Gatekeeper assessment, then waits for a normal exit before replacing the app. Unsaved work blocks installation/restart. A failed move or launch restores the previous bundle. Updates require a writable Applications folder; no administrator password is collected. Windows and Linux retain the website download flow. This source change needs a newly signed/notarized Mac release before it reaches users. Versioning uses the workspace version. Increment it before each independent release, build all supported platforms, verify activation and publish only after testing. The website currently pins the explicitly labeled early-access `v0.20.1` prerelease using `PIXASHOP_RELEASE_TAG`. Without a pin it follows the latest stable release. Draft releases are never offered.

## Branding and notices

The icon is an original pixel-grid S from `pixashop/icons.py`; build-time generated icons replace the upstream app icons. Required upstream notices and third-party licenses remain in the package's `Licenses` folder (inside `PixaShop.app/Contents/Resources` on Mac). Upstream contributor credits are preserved. The overlay must not promote the modified app as an ArtCraft product.

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

## Publish the 0.20.2 Mac update

After native builds and desktop QA pass, download the Mac testing DMG and run on the publisher’s Mac:

```sh
bash pixashop/sign_update_macos.sh /path/to/pixashop-0.20.2-macos-universal.dmg
```

The script uses the existing Developer ID identity and `PixaShop-Notary` Keychain profile, signs/notarizes the app and final DMG, preserves the drag-to-Applications layout, and writes the verified release under Documents. It never exports a private key or password. Publish that verified DMG as `pixashop-0.20.2-macos-universal.dmg` on a stable `v0.20.2` release only after testing activation, editing, save/reopen and the real update/restart flow. Keep website release pin unchanged until signing and QA pass. Existing 0.20.1 customers need a one-time manual install to obtain the updater. Future Mac releases use Install and restart.

## PixaShop user manual

The current online manual is https://aiwebdesignfirm.com/pixashop/manual, also linked from the PixaShop download page. Installed 0.20.2 users can reach it through Help → PixaShop Website → User manual without reinstalling.

The next desktop version, 0.20.3, adds Help → PixaShop User Manual. Its searchable chapter window embeds `pixashop/manual/guide.json` in the binary and does not fetch the guide over the network. The window also links to the online manual. Account access checks still require internet access. The Markdown edition is `pixashop/manual/PixaShop-User-Manual.md`.

The 0.20.3 source must pass native checks, then its Mac app and DMG must be signed and notarized before publishing a new update. Do not replace the signed 0.20.2 release assets with a rebuilt binary using the same version number.

### Quick tool tour (0.20.3)

Help → Quick Tool Tour opens a read-only coaching bubble for every registered toolbox tool (currently 68), in actual toolbar order. Each step describes the tool, a short usage instruction, and the current keyboard shortcut if assigned. Back, Next/Done, Skip, a tool picker, and a Manual button provide navigation. The tour outlines the tool's toolbar group and scrolls the toolbox when needed. Grouped tools are explained individually; a note explains how to open the flyout. No tour navigation invokes a tool-selection or image-editing command, creates a document, or changes panel preferences. The current image and selected tool are preserved. The guide and tour are bundled in the same next signed 0.20.3 build.

## Branding audit candidate 0.20.4

See root PIXA_SHOP_BRANDING_AUDIT.json for exact source checks and remaining installed-app acceptance. The product overlay removes upstream promotional translation entries and Linux metadata destinations while preserving credits/notices. Packaging writes a `.build.json` source-commit and digest receipt. New release tags must resolve to the product source used by the build; never move old published tags or replace 0.20.3 assets. The new S icon and these changes require a rebuilt, tested, signed/notarized release before they reach installed users.
