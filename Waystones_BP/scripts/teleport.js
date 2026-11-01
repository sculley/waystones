// Cross-dimension, any-distance travel with a safety check on arrival.
import { system, world } from "@minecraft/server";
import * as store from "./store.js";

export const WAYSTONE = "wst:waystone";
const COOLDOWN_TICKS = 60; // 3 seconds
const lastTravel = new Map();

export function travel(player, target) {
  const ws = store.get(target.id);
  if (!ws) return player.sendMessage("§cThat waystone no longer exists.");

  const wait = COOLDOWN_TICKS - (system.currentTick - (lastTravel.get(player.id) ?? -COOLDOWN_TICKS));
  if (wait > 0) return player.onScreenDisplay.setActionBar(`§7Recharging… ${Math.ceil(wait / 20)}s`);
  lastTravel.set(player.id, system.currentTick);

  const origin = { dimension: player.dimension, location: player.location, rotation: player.getRotation() };
  effects(player.dimension, player.location);

  // teleport() loads the destination chunk, so distance and dimension don't matter.
  player.addEffect("slow_falling", 10, { showParticles: false });
  player.teleport(
    { x: ws.x + 0.5, y: ws.y + 1, z: ws.z + 0.5 },
    { dimension: world.getDimension(ws.dim), rotation: origin.rotation, keepVelocity: false }
  );
  verifyArrival(player, ws, origin, 0);
}

// Once the chunk is loaded, make sure the waystone still exists and isn't buried.
function verifyArrival(player, ws, origin, attempt) {
  system.runTimeout(() => {
    if (!player.isValid) return;
    let block;
    try {
      block = world.getDimension(ws.dim).getBlock(ws);
    } catch {}
    if (!block) {
      if (attempt < 20) verifyArrival(player, ws, origin, attempt + 1);
      return;
    }
    if (block.typeId !== WAYSTONE) {
      store.remove(ws.id);
      return sendBack(player, origin, `§c${ws.name} was destroyed, so it has been removed.`);
    }
    if (!isClear(block.above(1)) || !isClear(block.above(2))) {
      // Something got on top anyway (snow, falling sand, an enderman): land beside it instead.
      const spot = besideWaystone(block);
      if (!spot) return sendBack(player, origin, `§c${ws.name} is blocked — clear the two blocks above it.`);
      player.teleport(spot, { dimension: block.dimension, rotation: origin.rotation, keepVelocity: false });
      effects(block.dimension, spot);
      return player.sendMessage(`§e${ws.name} is blocked, so you've arrived next to it. Clear the two blocks above it.`);
    }

    effects(block.dimension, player.location);
    player.onScreenDisplay.setActionBar(`§dArrived at §f${ws.name}`);
  }, 2);
}

/** Space a player can stand in on top of a waystone. */
const isClear = (b) => !b || b.isAir || b.isLiquid;

/** Nearest spot around the waystone with two air blocks over solid ground, or undefined. */
function besideWaystone(block) {
  const around = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]];
  for (const dy of [0, 1, -1]) {
    for (const [dx, dz] of around) {
      const { x, y, z } = block.location;
      const at = { x: x + dx, y: y + dy, z: z + dz };
      try {
        const feet = block.dimension.getBlock(at);
        const head = feet?.above(1);
        const ground = feet?.below(1);
        if (feet?.isAir && head?.isAir && ground && !ground.isAir && !ground.isLiquid) {
          return { x: at.x + 0.5, y: at.y, z: at.z + 0.5 };
        }
      } catch {}
    }
  }
}

function sendBack(player, origin, message) {
  player.teleport(origin.location, { dimension: origin.dimension, rotation: origin.rotation });
  lastTravel.delete(player.id);
  player.sendMessage(message);
}

function effects(dimension, { x, y, z }) {
  try {
    dimension.playSound("mob.endermen.portal", { x, y, z });
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2;
      dimension.spawnParticle("minecraft:endrod", { x: x + Math.cos(a) * 0.8, y: y + 1, z: z + Math.sin(a) * 0.8 });
    }
  } catch {}
}
