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
  if (block.typeId !== WAYSTONE) return;
  editWaystone(player, store.create(block, player), "Name your waystone");
});

// Give the guide a moment after joining — in a brand-new world the inventory isn't ready at spawn.
world.afterEvents.playerSpawn.subscribe(({ player, initialSpawn }) => {
  if (initialSpawn) system.runTimeout(() => giveGuideOnce(player), 40);
});
// Catch the host, whose spawn can happen before scripts finish loading.
world.afterEvents.worldLoad.subscribe(() => {
  system.runTimeout(() => world.getAllPlayers().forEach((p) => giveGuideOnce(p)), 40);
});
