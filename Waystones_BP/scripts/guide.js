// The Waystones Guide: given once to every player, readable as a chaptered menu.
import { ItemStack, system } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

export const GUIDE = "wst:guide";
const GIVEN = "wst:guide_received";

// Recipe icons are font glyphs from Waystones_RP/font/glyph_E5.png (drawn by tools/render_recipes.py):
// character U+E5xx shows cell xx of that sheet. Each icon is about two lines of text tall, so grid
// rows are separated by a blank line to stop them overlapping.
const glyph = (cell) => String.fromCodePoint(0xe500 + cell);
const [_, S, A, E, O, C, B, WAYSTONE_ICON, WAYFINDER_ICON, GUIDE_ICON, ARROW, PLUS] = Array.from({ length: 12 }, (__, i) =>
  glyph(i)
);
const NAMES = { [S]: "Stone Bricks", [A]: "Amethyst Shard", [E]: "Ender Pearl", [O]: "Obsidian", [C]: "Compass", [B]: "Book" };

/** A 3×3 crafting grid with the result beside the middle row, then a key naming each ingredient. */
function recipePage(rows, result, note = "Crafting table") {
  const grid = rows.map((row, i) => row.join(" ") + (i === 1 ? `    ${ARROW}    ${result}` : "")).join("\n\n");
  return `${grid}\n\n§7${note}§r\n\n${key(rows.flat())}`;
}

function key(cells) {
  return [...new Set(cells)]
    .filter((c) => NAMES[c])
    .map((c) => `${c}  ${NAMES[c]}`)
    .join("\n\n");
}

const RECIPES = [
  { title: "Waystone", icon: "textures/blocks/wst_waystone_side", text: recipePage([[S, A, S], [S, E, S], [O, O, O]], WAYSTONE_ICON) },
  { title: "Wayfinder", icon: "textures/items/wst_wayfinder", text: recipePage([[_, A, _], [E, C, E], [_, A, _]], WAYFINDER_ICON) },
  {
    title: "Waystones Guide",
    icon: "textures/items/wst_guide",
    text: `${B} ${PLUS} ${A}    ${ARROW}    ${GUIDE_ICON}\n\n§7Crafting table, any arrangement§r\n\n${key([B, A])}`,
  },
];

const CHAPTERS = [
  {
    title: "Getting started",
    text:
      "Waystones let you travel instantly between places you've marked — any distance, in the Overworld, Nether or End.\n\n" +
      "1. Craft a §5Waystone§r and place it.\n2. Give it a name.\n3. Place another one somewhere else.\n4. Link them together (see §5Linking§r).",
  },
  {
    title: "Linking",
    text:
      "§lSneak + use§r your waystone, choose §5Manage§r, then §5Link waystones§r and tick the destinations. Links work both ways.\n\n" +
      "§lOne-to-one:§r a waystone with one link acts like a portal — just use it to travel. Sneak + use to open its menu instead.\n\n" +
      "§lOne-to-many:§r a waystone with several links shows a list to choose from.",
  },
  {
    title: "The Wayfinder",
    text:
      "Hold the §5Wayfinder§r and press use to travel to any waystone you can access, from anywhere. Nearby waystones are listed first.\n\n" +
      "There is a short recharge between trips.",
  },
  {
    title: "Privacy & safety",
    text:
      "§lPublic§r waystones can be used by anyone. §lPrivate§r ones only by you. Change this in §5Manage → Rename & privacy§r.\n\n" +
      "Keep the two blocks above a waystone clear — blocks placed there pop back into your inventory. If something still ends up there (snow, falling sand), you arrive next to the waystone instead.\n\n" +
      "If a destination waystone has been destroyed, you're sent back to where you started.\n\n" +
      "Waystones are as blast-proof as obsidian.",
  },
  { title: "Recipes", recipes: RECIPES },
];

export async function openGuide(player, chapter) {
  if (chapter === undefined) {
    const form = new ActionFormData().title("Waystones Guide").body("Choose a chapter.");
    for (const c of CHAPTERS) form.button(c.title);
    const res = await form.show(player);
    if (!res.canceled) openGuide(player, res.selection);
    return;
  }
  const { title, text, recipes } = CHAPTERS[chapter];
  if (recipes) return openRecipes(player, chapter, recipes);
  const res = await new ActionFormData().title(title).body(text).button("Back").show(player);
  if (!res.canceled) openGuide(player);
}

/** Recipes chapter: one button per recipe, each recipe on its own page. */
async function openRecipes(player, chapter, recipes, page) {
  if (page === undefined) {
    const form = new ActionFormData().title(CHAPTERS[chapter].title).body("Choose a recipe.");
    for (const r of recipes) form.button(r.title, r.icon);
    form.button("Back");
    const res = await form.show(player);
    if (res.canceled) return;
    return res.selection < recipes.length ? openRecipes(player, chapter, recipes, res.selection) : openGuide(player);
  }
  const res = await new ActionFormData().title(recipes[page].title).body(recipes[page].text).button("Back").show(player);
  if (!res.canceled) openRecipes(player, chapter, recipes);
}

/** Give the guide once per player, the first time they join with the add-on. */
// Retries until the player's inventory is ready; only marks the gift as given once it lands.
export function giveGuideOnce(player, attempt = 0) {
  if (!player.isValid || player.getDynamicProperty(GIVEN)) return;
  const container = player.getComponent("minecraft:inventory")?.container;
  if (!container) {
    if (attempt < 10) system.runTimeout(() => giveGuideOnce(player, attempt + 1), 20);
    return;
  }
  const leftover = container.addItem(new ItemStack(GUIDE, 1));
  if (leftover) player.dimension.spawnItem(leftover, player.location);
  player.setDynamicProperty(GIVEN, true);
  player.sendMessage("§dYou received the §5Waystones Guide§d — use it to learn how waystones work.");
}
