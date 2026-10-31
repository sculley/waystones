// Menus for waystones and the Wayfinder.
import { system } from "@minecraft/server";
import { ActionFormData, FormCancelationReason, ModalFormData } from "@minecraft/server-ui";
import * as store from "./store.js";
import { travel } from "./teleport.js";

const ICON = "textures/items/wst_wayfinder";

/** Show a form, retrying while the player has another screen open. Returns undefined if closed. */
async function show(player, form) {
  for (let tries = 0; tries < 20; tries++) {
    const res = await form.show(player);
    if (res.cancelationReason !== FormCancelationReason.UserBusy) return res.canceled ? undefined : res;
    await system.waitTicks(5);
  }
}

function describe(ws, player) {
  const dim = store.DIMENSIONS[ws.dim]?.label ?? ws.dim;
  if (ws.dim !== player.dimension.id) return `§8${dim}`;
  const { x, y, z } = player.location;
  return `§8${dim} · ${Math.round(Math.hypot(ws.x - x, ws.y - y, ws.z - z))}m`;
}

/** Nearest first in the player's dimension, then everything else by name. */
function sortFor(player, list) {
  const here = player.dimension.id;
  const { x, z } = player.location;
  const dist = (ws) => (ws.dim === here ? Math.hypot(ws.x - x, ws.z - z) : Infinity);
  return list.sort((a, b) => dist(a) - dist(b) || a.name.localeCompare(b.name));
}

async function pickDestination(player, title, body, list, extraButtons = []) {
  const form = new ActionFormData().title(title).body(body);
  for (const ws of list) form.button(`${ws.name}\n${describe(ws, player)}`, store.DIMENSIONS[ws.dim]?.icon);
  for (const label of extraButtons) form.button(label, ICON);
  return (await show(player, form))?.selection;
}

export async function openWaystone(player, ws) {
  if (!store.canUse(ws, player)) return player.onScreenDisplay.setActionBar("§cThis waystone is private.");
  const isOwner = ws.owner === player.id;
  if (isOwner && player.isSneaking) return manage(player, ws);

  const links = sortFor(player, ws.links.map((id) => store.get(id)).filter((o) => o && store.canUse(o, player)));

  // One-to-one link: behave like a portal pair. Sneak to open the menu instead.
  if (links.length === 1 && !player.isSneaking) return travel(player, links[0]);

  const body = links.length
    ? "Choose a destination."
    : isOwner
      ? "Not linked yet. Open §5Manage§r to link it to other waystones."
      : "This waystone isn't linked anywhere yet.";
  const choice = await pickDestination(player, ws.name, body, links, isOwner ? ["§5Manage"] : []);
  if (choice === undefined) return;
  if (choice < links.length) travel(player, links[choice]);
  else manage(player, ws);
}

async function manage(player, ws) {
  const form = new ActionFormData()
    .title(`Manage ${ws.name}`)
    .body(`${ws.links.length} link(s) · ${ws.public ? "Public" : "Private"}`)
    .button("Link waystones", ICON)
    .button("Rename & privacy")
    .button("Done");
  const selection = (await show(player, form))?.selection;
  if (selection === 0) return linkMenu(player, ws);
  if (selection === 1) return editWaystone(player, ws);
}

async function linkMenu(player, ws) {
  const others = sortFor(player, store.getAll().filter((o) => o.id !== ws.id && store.canUse(o, player)));
  if (!others.length) return player.sendMessage("§7Place another waystone first, then link them here.");

  const form = new ModalFormData().title(`Link ${ws.name}`).submitButton("Save links");
  for (const o of others) form.toggle(`${o.name}  ${describe(o, player)}`, { defaultValue: ws.links.includes(o.id) });
  const res = await show(player, form);
  if (!res) return;

  const self = store.get(ws.id);
  if (!self) return;
  res.formValues.forEach((linked, i) => {
    const other = store.get(others[i].id);
    if (other && linked !== self.links.includes(other.id)) store.setLinked(self, other, linked);
  });
  player.onScreenDisplay.setActionBar(`§d${self.name}§r linked to ${self.links.length} waystone(s)`);
}

export async function editWaystone(player, ws, title = `Edit ${ws.name}`) {
  const form = new ModalFormData()
    .title(title)
    .textField("Name", "My Base", { defaultValue: ws.name })
    .toggle("Public (anyone can travel here)", { defaultValue: ws.public })
    .submitButton("Save");
  const res = await show(player, form);
  if (!res) return;

  const fresh = store.get(ws.id);
  if (!fresh) return;
  const [name, isPublic] = res.formValues;
  fresh.name = String(name).trim().slice(0, 32) || fresh.name;
  fresh.public = Boolean(isPublic);
  store.save(fresh);
}

export async function openWayfinder(player) {
  const list = sortFor(player, store.getAll().filter((ws) => store.canUse(ws, player)));
  if (!list.length) return player.onScreenDisplay.setActionBar("§7No waystones yet — place one first.");
  const choice = await pickDestination(player, "Wayfinder", "Travel to any waystone.", list);
  if (choice !== undefined) travel(player, list[choice]);
}
