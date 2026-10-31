// The Waystones Guide: given once to every player, readable as a chaptered menu.
import { ItemStack, system } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

export const GUIDE = "wst:guide";
const GIVEN = "wst:guide_received";

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
      "If a destination waystone has been destroyed, or the two blocks above it are blocked, you're sent back to where you started.\n\n" +
      "Waystones are as blast-proof as obsidian.",
  },
  {
    title: "Recipes",
    text:
      "§5Waystone§r (crafting table)\n Stone Bricks · Amethyst Shard · Stone Bricks\n Stone Bricks · Ender Pearl · Stone Bricks\n Obsidian · Obsidian · Obsidian\n\n" +
      "§5Wayfinder§r (crafting table)\n  —  · Amethyst Shard ·  — \n Ender Pearl · Compass · Ender Pearl\n  —  · Amethyst Shard ·  — \n\n" +
      "§5Waystones Guide§r\n Book + Amethyst Shard (any shape)",
  },
];

export async function openGuide(player, chapter) {
  if (chapter === undefined) {
    const form = new ActionFormData().title("Waystones Guide").body("Choose a chapter.");
    for (const c of CHAPTERS) form.button(c.title);
    const res = await form.show(player);
    if (!res.canceled) openGuide(player, res.selection);
    return;
  }
  const res = await new ActionFormData()
    .title(CHAPTERS[chapter].title)
    .body(CHAPTERS[chapter].text)
    .button("Back")
    .show(player);
  if (!res.canceled) openGuide(player);
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
