// Waystone storage: one world dynamic property per waystone, keyed by its position.
import { world } from "@minecraft/server";

const PREFIX = "wst:ws:";
const DIM_CODES = { "minecraft:overworld": "o", "minecraft:nether": "n", "minecraft:the_end": "e" };

export const DIMENSIONS = {
  "minecraft:overworld": { label: "Overworld", icon: "textures/blocks/grass_side_carried" },
  "minecraft:nether": { label: "Nether", icon: "textures/blocks/netherrack" },
  "minecraft:the_end": { label: "The End", icon: "textures/blocks/end_stone" },
};

/** Stable id for the waystone at a block's position. */
export function idOf(block) {
  const { x, y, z } = block.location;
  return `${DIM_CODES[block.dimension.id] ?? block.dimension.id}_${x}_${y}_${z}`;
}

export function get(id) {
  const raw = world.getDynamicProperty(PREFIX + id);
  return typeof raw === "string" ? JSON.parse(raw) : undefined;
}

export function getAll() {
  const list = [];
  for (const key of world.getDynamicPropertyIds()) {
    if (!key.startsWith(PREFIX)) continue;
    const ws = get(key.slice(PREFIX.length));
    if (ws) list.push(ws);
  }
  return list;
}

export function save(ws) {
  world.setDynamicProperty(PREFIX + ws.id, JSON.stringify(ws));
}

export function create(block, player) {
  const { x, y, z } = block.location;
  const ws = {
    id: idOf(block),
    name: `Waystone ${getAll().length + 1}`,
    dim: block.dimension.id,
    x, y, z,
    owner: player.id,
    ownerName: player.name,
    public: true,
    links: [],
  };
  save(ws);
  return ws;
}

/** Delete a waystone and unlink it from everything it was linked to. */
export function remove(id) {
  const ws = get(id);
  if (!ws) return;
  for (const linkId of ws.links) {
    const other = get(linkId);
    if (!other) continue;
    other.links = other.links.filter((l) => l !== id);
    save(other);
  }
  world.setDynamicProperty(PREFIX + id, undefined);
}

/** Links are two-way: linking A→B also links B→A. */
export function setLinked(a, b, linked) {
  for (const [self, other] of [[a, b], [b, a]]) {
    const links = new Set(self.links);
    if (linked) links.add(other.id);
    else links.delete(other.id);
    self.links = [...links];
    save(self);
  }
}

export const canUse = (ws, player) => ws.public || ws.owner === player.id;
