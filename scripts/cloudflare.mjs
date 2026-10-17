import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

// Keep this project's new account separate from the machine's existing Wrangler login.
const child = spawn(
  process.execPath,
  [
    fileURLToPath(
      new URL("../node_modules/wrangler/bin/wrangler.js", import.meta.url),
    ),
    ...process.argv.slice(2),
  ],
  {
    stdio: "inherit",
    env: {
      ...process.env,
      XDG_CONFIG_HOME: fileURLToPath(
        new URL("../.wrangler/account", import.meta.url),
      ),
      WRANGLER_SEND_METRICS: "false",
    },
  },
);
for (const signal of ["SIGINT", "SIGTERM"])
  process.on(signal, () => child.kill(signal));
child.on("error", (error) => {
  console.error(error.message);
  process.exitCode = 1;
});
child.on("exit", (code) => {
  process.exitCode = code ?? 1;
});
