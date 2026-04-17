# remoteStorage.js API Reference

Method signatures for the `RemoteStorage` instance and the `BaseClient` returned
from `rs.scope()`. For usage patterns, examples, and the event system see
[SKILL.md](../SKILL.md).

## Constructor options

`cache` (default: `true`), `logging` (`false`), `changeEvents` (object with
`local`, `window`, `remote`, `conflict` booleans), `cordovaRedirectUri`, `modules`.

## RemoteStorage methods

```javascript
rs.connect(userAddress)          // WebFinger + OAuth flow
rs.connect(userAddress, token)   // Connect with pre-acquired token (Node.js)
rs.disconnect()                  // Disconnect and clear cache
rs.reconnect()                   // Re-authorize (e.g. after 401)
rs.setApiKeys({ dropbox, googledrive })  // Enable third-party backends
rs.startSync()                           // Trigger manual check for remote changes
rs.stopSync()                            // Pause the periodic sync cycle
rs.setSyncInterval(10000)                // Foreground interval (ms)
rs.setBackgroundSyncInterval(60000)      // Background interval (ms)
```

> **Note:** Local writes (`storeObject`, `storeFile`, `remove`) are automatically
> queued for sync. Do not call `startSync()` after writing — it is only needed to
> manually request remote changes (e.g. on `visibilitychange` or a "sync now" button).

## BaseClient — data operations

Paths are relative to the client's scope. Paths ending in `/` denote folders.
`maxAge` (ms) controls cache freshness — pass `false` to skip network check.

```javascript
// Read
client.getListing(path?)               // → { 'file': true, 'dir/': true }
client.getObject(path, maxAge?)        // → object | null
client.getFile(path, maxAge?)          // → { data, contentType, revision }
client.getAll(path?, maxAge?)          // → { 'key': object, ... }

// Write
client.storeObject(typeAlias, path, obj)  // JSON with schema validation
client.storeFile(contentType, path, body) // Raw data (string, ArrayBuffer)
client.remove(path)                       // Delete

// Utility
client.scope(path)                     // New client scoped to subpath
client.declareType(alias, schema)      // Register JSON Schema type
client.validate(object)               // Validate against declared schemas
client.getItemURL(path)                // Public URL (if in /public/)
```
