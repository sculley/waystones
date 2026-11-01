// Waystones — entry point. Wires custom components and events to the store and menus.
import { system, world } from "@minecraft/server";
import * as store from "./store.js";
import { WAYSTONE } from "./teleport.js";
import { editWaystone, openWayfinder, openWaystone } from "./ui.js";
import { giveGuideOnce, openGuide } from "./guide.js";

// Holding the use button fires repeatedly; ignore repeats within a few ticks.
const lastUse = new Map();
function isRepeat(player) {
  const now = system.currentTick;
  const repeat = now - (lastUse.get(player.id) ?? -100) < 10;
  lastUse.set(player.id, now);
  return repeat;
}

system.beforeEvents.startup.subscribe(({ blockComponentRegistry, itemComponentRegistry }) => {
  blockComponentRegistry.registerCustomComponent("wst:waystone", {
    // Players arrive standing on top, so the two blocks above must be free.
    beforeOnPlayerPlace(event) {
      let clear = true;
      try {
        clear = [event.block.above(1), event.block.above(2)].every(isFree);
      } catch {} // at the top of the world: nothing above to check
      if (clear) return;
      event.cancel = true;
      event.player?.onScreenDisplay.setActionBar("§cA waystone needs two clear blocks above it.");
    },
    onPlayerInteract({ player, block }) {
      if (!player || isRepeat(player)) return;
      // Adopt waystones that exist without a record (e.g. placed with /setblock).
      const ws = store.get(store.idOf(block)) ?? store.create(block, player);
      openWaystone(player, ws);
    },
    onPlayerBreak({ block }) {
      store.remove(store.idOf(block));
    },
  });

  itemComponentRegistry.registerCustomComponent("wst:wayfinder", {
    onUse({ source }) {
      if (!isRepeat(source)) openWayfinder(source);
    },
  });

  itemComponentRegistry.registerCustomComponent("wst:guide", {
    onUse({ source }) {
      if (!isRepeat(source)) openGuide(source);
    },
  });
});

world.afterEvents.playerPlaceBlock.subscribe(({ block, player }) => {
  if (isAboveWaystone(block)) return undo(block, player);
  if (block.typeId !== WAYSTONE) return;
  editWaystone(player, store.create(block, player), "Name your waystone");
});

// Keep the space above waystones clear. The stable API can't cancel a placement before it
// happens, so a block placed there is removed straight after and handed back to the player.
const isFree = (b) => !b || b.isAir || b.isLiquid;

function isAboveWaystone(block) {
  try {
    return block.below(1)?.typeId === WAYSTONE || block.below(2)?.typeId === WAYSTONE;
  } catch {
    return false; // below the world floor
  }
}

function undo(block, player) {
  const item = block.permutation.getItemStack(1);
  block.setType("minecraft:air");
  player.onScreenDisplay.setActionBar("§cKeep the two blocks above a waystone clear.");
  if (!item || String(player.getGameMode()).toLowerCase() === "creative") return;
  const leftover = player.getComponent("minecraft:inventory")?.container?.addItem(item);
  if (leftover) player.dimension.spawnItem(leftover, player.location);
}

// Give the guide a moment after joining — in a brand-new world the inventory isn't ready at spawn.
world.afterEvents.playerSpawn.subscribe(({ player, initialSpawn }) => {
  if (initialSpawn) system.runTimeout(() => giveGuideOnce(player), 40);
});
// Catch the host, whose spawn can happen before scripts finish loading.
world.afterEvents.worldLoad.subscribe(() => {
  system.runTimeout(() => world.getAllPlayers().forEach((p) => giveGuideOnce(p)), 40);
});
