import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { Generator } from "@wfcd/relics";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const dataDir = path.join(rootDir, "data");

await mkdir(dataDir, { recursive: true });

const generator = new Generator();
const relics = await generator.generate();

await generator.writeData(dataDir, "Relics", false);

console.log(`Generated ${relics.length} relics into ${dataDir}`);
