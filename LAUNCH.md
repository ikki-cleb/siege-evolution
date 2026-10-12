# Launch checklist

Everything from creating store accounts to submitting Siege Evolution to the
App Store and Google Play. The game side is ready: icon, splash, export
presets, billing code, store text, screenshots and the Codemagic cloud builds.
What's left happens in web dashboards. No Mac, Xcode or Android Studio needed:
**Codemagic** builds both phone versions in the cloud.

Reference files:
- [`store/listing.md`](store/listing.md): store text, keywords, screenshot captions (`python3 tools/check_listing.py` checks the lengths)
- [`store/in-app-products.md`](store/in-app-products.md): product ids and prices
- [`store/age-rating.md`](store/age-rating.md): age rating, App Privacy and Data safety answers
- [`store/screenshots/`](store/screenshots): ready-to-upload images (`ios-6.9/`, `android/`, `feature-graphic.png`) and [`store/play-icon-512.png`](store/play-icon-512.png)
- [`docs/`](docs): privacy, support and home pages for GitHub Pages
- [`codemagic.yaml`](codemagic.yaml) and [`tools/ci/`](tools/ci): the cloud builds

## 1. Accounts (allow 1–3 weeks for verification)

- [ ] **Apple Developer Program:** $99/year at developer.apple.com/programs.
  - Individual enrollment shows your legal name as the seller.
  - Enrolling as a company needs a D-U-N-S number.
- [ ] **Google Play Console:** $25 one time at play.google.com/console. Identity verification can take several days.
- [ ] **Codemagic:** free account at codemagic.io, signed in with GitHub. The free plan includes 500 build minutes a month (an iOS build takes roughly 10–20).

## 2. Fill in the placeholders

- [ ] Replace `[PUBLISHER]`, `[SUPPORT_EMAIL]` and `[DATE]` in `docs/*.html` and `store/*.md` (search for `[`).
- [ ] Use a support email you're happy to make public. It appears on both store pages.

## 3. Publish the privacy and support pages

- [ ] Merge this branch to `main`.
- [ ] In the GitHub repo, open **Settings → Pages → Build and deployment → Deploy from a branch**, then select `main` and `/docs`.
  - GitHub Pages needs a public repo on the free plan (`docs/` also holds the art prompt files, which would become public too).
  - If the repo stays private, either upgrade GitHub or host the three HTML files (plus `style.css` and `icon.png`) anywhere else, such as Netlify or Cloudflare Pages.
- [ ] Open `https://<github-user>.github.io/siege-evolution/privacy.html` and check that it loads. Both stores require this URL.

## 4. Connect Codemagic

- [ ] In Codemagic: **Add application → GitHub → siege-evolution**, and choose the **codemagic.yaml** setup. It picks up the two workflows in `codemagic.yaml`.
- [ ] **Version numbers:** the build number counts up by itself on every Codemagic build. Change the version name (`1.0.0` → `1.0.1`…) in `export_presets.cfg` (`version/name` and `application/short_version`) and `project.godot` (`config/version`) for each store release.

## 5. Apple

1. [ ] **App Store Connect → Business:** sign the **Paid Apps** agreement and complete tax and banking. In-app purchases don't work until this is done.
2. [ ] **Certificates, Identifiers & Profiles → Identifiers → +:** register the App ID `com.siegeevolution.app` (In-App Purchase is on by default).
3. [ ] **App Store Connect → Apps → +:** create the app.
   - Name: Siege Evolution
   - Bundle ID: `com.siegeevolution.app`
   - SKU: `siegeevolution`
4. [ ] Create the 6 **non-consumable** in-app purchases from `store/in-app-products.md`, with the same ids. Each needs a display name, description, price and a review screenshot (the in-game Store screen works).
5. [ ] **Users and Access → Integrations → App Store Connect API:** create a key with the **App Manager** role and download the `.p8` file (you can only download it once).
6. [ ] In Codemagic: **Team settings → Integrations → Developer Portal / App Store Connect:** add that key and name it **`siege_asc_key`**.
7. [ ] In Codemagic: **Environment variables:** make a group named **`apple`** with `APPLE_TEAM_ID` = your 10-character team id (Apple Developer → Membership).
8. [ ] Run the **iOS release (TestFlight)** workflow. It installs Godot, adds the StoreKit plugin, exports the Xcode project, signs it, and uploads it to TestFlight.
   - The first run is the one most likely to need a fix (plugin download names, Xcode settings). Its log says which step failed.
9. [ ] **TestFlight:** install the build and buy an item with a Sandbox tester account (Settings → Developer on the phone). Then delete and reinstall the game and use **Store → Restore Purchases**.
10. [ ] Fill in the version page:
    - Screenshots from `store/screenshots/ios-6.9/` and the copy from `listing.md`.
    - The age rating and App Privacy answers from `age-rating.md`.
    - The privacy policy URL and support URL.
    - **Attach all 6 in-app purchases to this version.** Apple only reviews new IAPs alongside an app version.
11. [ ] Review notes: "No login required. Optional purchases can be tested with a sandbox account. Restore Purchases is on the Store screen."
12. [ ] Submit for review. It usually takes 1–3 days.

## 6. Google Play

1. [ ] **Play Console → Create app:** name *Siege Evolution: Tower Defense*, Game, Free.
2. [ ] Set up a **payments profile / merchant account**. It's needed before you can sell in-app products.
3. [ ] **Make an upload key** (the key that signs your uploads; keep it safe forever, and back it up):
   ```bash
   keytool -genkeypair -v -keystore siege-upload.jks -alias siege -keyalg RSA -keysize 2048 -validity 10000
   ```
   Never commit it to the repo. Google Play App Signing holds the real app key; this one only proves uploads come from you, and Google can reset it if it's lost.
4. [ ] In Codemagic: **Team settings → Code signing identities → Android keystores:** upload `siege-upload.jks` with its passwords and alias, reference name **`siege_upload_key`**.
5. [ ] Run the **Android release (Google Play)** workflow, then download the `.aab` from the build's artifacts.
   - The first time, the automatic upload step fails (Google doesn't accept API uploads yet). That's expected.
6. [ ] **Upload that first `.aab` by hand** in Testing → Internal testing. Google requires that before the API (and so Codemagic) can upload builds.
7. [ ] **Monetize → Products → In-app products:** create the 6 products from `store/in-app-products.md`. This menu only appears after a build with the billing permission is uploaded.
8. [ ] Create a Google Cloud **service account** with Play Console access (Users and permissions → Invite → the service account email, with release permissions), download its JSON key, and add it in Codemagic as `GCLOUD_SERVICE_ACCOUNT_CREDENTIALS` in a variable group named **`google_play`**. From then on, every Android build uploads to the internal track as a draft.
9. [ ] **Closed testing:** new *personal* developer accounts must run a closed test with at least **12 testers opted in for 14 days in a row** before they can apply for production. Recruit testers early (friends, family, a Discord).
10. [ ] Fill in:
    - **Store listing:** copy, `store/screenshots/android/`, `store/screenshots/feature-graphic.png`, `store/play-icon-512.png`.
    - **App content:** privacy policy, ads = No, Data safety, content rating (IARC), target audience 13+. The answers are in `age-rating.md`.
    - **Target API level:** Google requires recent Android versions every August. If the Console warns about it, raise `gradle_build/target_sdk` in `export_presets.cfg`.
11. [ ] Apply for production access, then promote the tested build to production in the Console.

## 7. Before every release

```bash
godot --headless --fixed-fps 60 --script tests/sim_test.gd -- rules
python3 tools/check_listing.py
```

- [ ] Bump the version name (see section 4).
- [ ] Update "What's new" in `store/listing.md`.
- [ ] Re-capture screenshots if the game changed: `bash tools/screenshots/make_screenshots.sh`.
- [ ] Regenerate icons if the art changed: `python3 tools/draw_icon.py`.

## How the phone builds work

- **Purchases:** `scripts/store.gd` sells the items. On phones it hands purchases to `scripts/billing/google_play_billing.gd` (Android) or `scripts/billing/app_store_billing.gd` (iPhone), which wrap Godot's official billing plugins. The plugins aren't in the repo: `tools/ci/fetch_plugins.sh` downloads them during each Codemagic build. If a plugin release renames its download, set `BILLING_PLUGIN_URL` / `IOS_PLUGINS_URL` in Codemagic to the exact file.
- **Test mode:** web, editor and debug builds keep free, instant test purchases. Release phone builds never do.
- **Notches:** `Look.safe_top` moves the game below a phone's notch or camera hole.
- **Not supported yet:** iPad (iPhone only, so no iPad screenshots are needed), cloud saves, and tablets in landscape.
