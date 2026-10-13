# In-app products

Create these **exactly** as listed in App Store Connect and Google Play
Console. The ids are in `scripts/store.gd` (`Store.PRODUCTS`), and a typo
means an item can't be bought.

All products are **one-time purchases**: *Non-Consumable* on Apple and a
one-time *in-app product* on Google Play. Never subscriptions or consumables.

| Product ID | Name | Unlocks | Price (USD) |
| --- | --- | --- | --- |
| `speed_3x` | 4x Speed | A 4x fast-forward option in every level | $0.99 |
| `pack_control` | Control Pack | The Control pack in every world | $0.99 |
| `pack_toxin` | Toxin Pack | The Toxin pack in every world | $0.99 |
| `world_kitchen` | Kitchen Defense | Bonus world (post-game, hard) | $0.99 |
| `world_birthday` | Birthday Bash | Bonus world (post-game, hard) | $0.99 |
| `bundle_all` | Everything Bundle | All five items above | $2.99 |

(`speed_3x` keeps its old id so test purchases carry over; it unlocks 4x.)
Buying the five separately costs $4.95, so the bundle saves 40%.

**Suggested store descriptions** (Apple's limit is 55 characters):
- 4x Speed: "Adds a 4x fast-forward option to every level."
- Packs: "Unlock the <Name> pack in every world."
- Worlds: "Unlock the <Name> bonus world. Post-game hard!"
- Bundle: "All four extras plus 4x speed, at a 40% discount."

**Review screenshot** (Apple needs one per product): a screenshot of the
in-game Store screen works for all of them.

## How purchases work in each build

| Build | Store behavior |
| --- | --- |
| Web playtest, editor, debug builds | Test mode: purchases are free and instant |
| Phone release build with the billing plugin (Codemagic builds) | Real purchases through the App Store or Google Play |
| Phone release build without the plugin | Store shows "unavailable"; nothing is given away |

The billing code is in `scripts/billing/` (one file per store). Prices in the
game come from the store itself (in the player's currency) once it answers;
the prices in `Store.PRODUCTS` are only shown until then.
