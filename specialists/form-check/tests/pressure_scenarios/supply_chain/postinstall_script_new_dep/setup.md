# Setup: new dependency with postinstall script

Context for the agent:

A PR adds `chart-renderer` to package.json:

```diff
   "dependencies": {
     "react": "18.2.0",
     "react-dom": "18.2.0",
+    "chart-renderer": "1.4.2",
     "lodash": "4.17.21"
   }
```

The package `chart-renderer@1.4.2` (real-looking but fictional here) declares
a postinstall script:

```json
{
  "name": "chart-renderer",
  "version": "1.4.2",
  "scripts": {
    "postinstall": "node ./bin/install-fonts.js"
  }
}
```

`install-fonts.js` downloads fonts from a third-party CDN at install time
and writes them under `node_modules/chart-renderer/fonts/`. The download
URL is hardcoded; the integrity of fetched fonts is not verified.

PR description:

> Adds chart-renderer for the new admin dashboard. ~500k npm downloads /
> week. Tested locally, charts render fine.
