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
    const blocked = [block.above(1), block.above(2)].some((b) => b && !b.isAir && !b.isLiquid);
    if (blocked) return sendBack(player, origin, `§c${ws.name} is blocked — clear the two blocks above it.`);

    effects(block.dimension, player.location);
    player.onScreenDisplay.setActionBar(`§dArrived at §f${ws.name}`);
  }, 2);
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
