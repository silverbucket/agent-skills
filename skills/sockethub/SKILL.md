---
name: sockethub
description: Use when building with Sockethub, ActivityStreams messaging, browser-to-IRC/XMPP gateways, RSS/Atom fetching, metadata previews, or multi-protocol chat clients. Also use whenever the user mentions Sockethub directly, wants browser JavaScript to talk to IRC or XMPP, or needs protocol-specific auth hidden behind one consistent message format.
license: LGPL-3.0
metadata:
  author: sockethub
---

# Sockethub

Sockethub is a protocol gateway for the web. It lets browser or server-side
JavaScript talk to IRC, XMPP, feeds, and metadata endpoints through one
ActivityStreams-based API.

Use this skill to give guidance that matches the current `master` branch of
`sockethub/sockethub`, not older wiki-era examples.

## Core Guidance

- Prefer `sc.contextFor(platform)` over hand-writing context arrays unless the
  user explicitly needs the raw URLs.
- Prefer `await sc.ready()` before sending anything important. The client can
  queue messages before readiness, but ready-first is easier to reason about.
- Treat credentials as runtime secrets. Never tell the user to hardcode,
  commit, paste into logs, or echo back real passwords or tokens.
- Use placeholders or environment-backed variables in examples such as
  `process.env.SOCKETHUB_IRC_TOKEN` or `process.env.SOCKETHUB_XMPP_SECRET`.
- Prefer tokens over passwords when the platform supports them.
- Be precise about platform differences. IRC supports an explicit `token`
  field. XMPP does not; it accepts a `password` field, and some deployments may
  allow a token string in that field as a compatibility mode.

## Secret Handling Rules

Follow these rules whenever auth is part of the answer:

- Do not ask the user to share a private password or token in chat unless the
  task is explicitly about wiring a local secret value and there is no safer
  alternative.
- If the user already pasted a real secret, redact it in any echoed examples or
  summaries.
- Keep code samples secret-free. Show placeholders, env vars, or secret-manager
  lookups.
- Use neutral wording like "secret" or "credential value" in prose. Use the
  literal field names `password` or `token` only when describing the Sockethub
  schema.
- When both password and token are possible, recommend the token path first.

## When to Use

Invoke this skill when you need to:

- Build a browser or Node client on top of Sockethub
- Connect web apps to IRC or XMPP through Socket.IO
- Fetch RSS or Atom feeds through Sockethub
- Generate URL metadata or link previews
- Explain Sockethub credential flows, connection lifecycle, or ActivityStreams
  message shapes
- Design a protocol-agnostic messaging app that hides IRC/XMPP specifics behind
  one API

## Recommended Flow

When answering Sockethub questions, structure the guidance in this order:

1. Start the server and Redis.
2. Create the client and wait for `ready()`.
3. Choose the platform with `sc.contextFor(...)`.
4. For persistent platforms, send a `credentials` event first.
5. Send the `connect` message.
6. Send follow-up verbs such as `join`, `send`, or `query`.
7. Handle callback errors and `failed` events.
8. Clear credentials on logout or when changing accounts.

If the user is building a new integration, prefer a complete vertical slice over
isolated snippets.

## Quick Start

### Server

For packaged usage:

```bash
npm install -g sockethub
sockethub --examples
```

For current `master` or local development:

```bash
git clone https://github.com/sockethub/sockethub.git
cd sockethub
bun install
bun run dev
```

Sockethub listens on `http://localhost:10550` by default and requires Redis.

### Client

```javascript
import SockethubClient from '@sockethub/client';
import { io } from 'socket.io-client';

const socket = io('http://localhost:10550', { path: '/sockethub' });
const sc = new SockethubClient(socket, { initTimeoutMs: 5000 });

await sc.ready();

sc.socket.on('message', (msg) => {
  console.log('Sockethub message:', msg);
});

sc.socket.on('failed', (msg) => {
  console.error('Sockethub failure:', msg);
});
```

## Platform Auth Matrix

### IRC

- Supports anonymous or credentialed sessions.
- Prefer `token` over `password` when the IRC network offers personal access
  tokens or OAuth-style flows.
- `password` and `token` are mutually exclusive.
- `saslMechanism` may be `PLAIN` or `OAUTHBEARER`.
- A non-empty `password` or `token` makes the session shareable across sockets.
  Username-only anonymous sessions are not shareable.

### XMPP

- Requires a `password` field in the credentials schema.
- Prefer a deployment-issued token over a long-lived account password when the
  deployment explicitly accepts that token in the SASL PLAIN password slot.
- Do not claim that dedicated token SASL mechanisms are implemented. Upstream
  documents only `SCRAM-SHA-1`, `PLAIN`, and `ANONYMOUS` via the bundled
  `@xmpp/client`.
- In examples and prose, call the runtime value an "XMPP secret" and explain
  that the value may be either a password or a compatible token string.

### Feeds and Metadata

- No credentials required.
- These are stateless platforms; there is no `connect` step.

## Example: IRC With Preferred Token Flow

```javascript
const ircToken = process.env.SOCKETHUB_IRC_TOKEN;

sc.socket.emit('credentials', {
  '@context': sc.contextFor('irc'),
  type: 'credentials',
  actor: { id: 'mynick@irc.libera.chat', type: 'person' },
  object: {
    type: 'credentials',
    nick: 'mynick',
    server: 'irc.libera.chat',
    token: ircToken,
    port: 6697,
    secure: true
  }
}, (result) => {
  if (result?.error) {
    console.error('IRC credentials failed:', result.error);
  }
});

sc.socket.emit('message', {
  '@context': sc.contextFor('irc'),
  type: 'connect',
  actor: { id: 'mynick@irc.libera.chat', type: 'person' }
}, (result) => {
  if (result?.error) {
    console.error('IRC connect failed:', result.error);
  }
});

// Join channel. Pass an ack callback to learn the outcome;
// treat any payload with an `error` property as a failure.
sc.socket.emit('message', {
  '@context': sc.contextFor('irc'),
  type: 'join',
  actor: { id: 'mynick@irc.libera.chat', type: 'person' },
  target: { id: '#sockethub@irc.libera.chat', type: 'room' }
}, (result) => {
  if (result?.error) {
    console.error('Join failed:', result.error);
    return;
  }
  // Channel is joined; safe to query attendance, render UI, etc.
});

sc.socket.emit('message', {
  '@context': sc.contextFor('irc'),
  type: 'send',
  actor: { id: 'mynick@irc.libera.chat', type: 'person' },
  target: { id: '#sockethub@irc.libera.chat', type: 'room' },
  object: { type: 'message', content: 'Hello from Sockethub.' }
});
```

## Example: XMPP With Secret Slot

```javascript
const xmppSecret = process.env.SOCKETHUB_XMPP_SECRET;

sc.socket.emit('credentials', {
  '@context': sc.contextFor('xmpp'),
  type: 'credentials',
  actor: { id: 'user@jabber.net', type: 'person' },
  object: {
    type: 'credentials',
    userAddress: 'user@jabber.net',
    password: xmppSecret,
    resource: 'web'
  }
}, (result) => {
  if (result?.error) {
    console.error('XMPP credentials failed:', result.error);
  }
});

sc.socket.emit('message', {
  '@context': sc.contextFor('xmpp'),
  type: 'connect',
  actor: { id: 'user@jabber.net', type: 'person' }
});

sc.socket.emit('message', {
  '@context': sc.contextFor('xmpp'),
  type: 'send',
  actor: { id: 'user@jabber.net', type: 'person' },
  target: { id: 'friend@jabber.net', type: 'person' },
  object: { type: 'message', content: 'Hello from Sockethub.' }
});
```

When explaining this example, say explicitly:

- `password` is the schema field name for XMPP.
- The runtime value can be either the real XMPP password or a deployment-issued
  token string when that deployment accepts token-in-password-slot auth.
- Prefer the token path when the deployment supports it.

## Example: Fetch a Feed

```javascript
sc.socket.emit('message', {
  '@context': sc.contextFor('feeds'),
  type: 'fetch',
  actor: { id: 'https://example.com/feed.xml' }
}, (result) => {
  if (result?.error) {
    console.error('Feed fetch failed:', result.error);
  }
});
```

## Example: Fetch Metadata

```javascript
sc.socket.emit('message', {
  '@context': sc.contextFor('metadata'),
  type: 'fetch',
  actor: { id: 'https://example.com/article' }
});
```

## Error Handling and Session Behavior

- Always show the callback form of `socket.emit(...)` when the user is wiring
  connect or credentials flows. Sockethub returns callback payloads containing
  `error` for rejected actions.
- Also mention the `failed` event for asynchronous failures.
- For anonymous IRC credentials, a second socket using the same actor may get
  `username already in use`.
- Sockethub may allow a narrow reconnect exception for anonymous credentials
  when the stale session and reconnect share the same client IP.
- Call `sc.clearCredentials()` when switching users or performing explicit
  logout so the client does not replay stale credentials on reconnect.

## ActivityStreams Shape

Use this shape for message examples:

```javascript
{
  '@context': sc.contextFor('irc'),
  type: 'send',
  actor: { id: 'user@example', type: 'person' },
  target: { id: '#room@example', type: 'room' },
  object: { type: 'message', content: 'Hello.' }
}
```

Valid object types commonly seen in Sockethub answers:

- `message`
- `me`
- `credentials`
- `attendance`
- `presence`
- `topic`
- `address`
- Server responses may also include ActivityStreams core types such as
  `collection` and `create`

## What to Avoid

- Do not present Sockethub as a direct browser-to-IRC/XMPP library. It is a
  server-side protocol gateway with a Socket.IO client API.
- Do not recommend committing credentials to config files or code samples.
- Do not imply XMPP supports a first-class `token` field. Upstream does not.
- Do not lead with raw context URLs when `sc.contextFor(...)` is enough.
- Do not omit Redis when explaining server startup.
- Do not ignore callback or `failed`-event error paths.

## Useful References

### SockethubClient

```javascript
import SockethubClient from '@sockethub/client';

// Constructor options
const sc = new SockethubClient(socket, {
  initTimeoutMs: 5000,      // Schema registry load timeout
  maxQueuedOutbound: 100,   // Max queued messages before ready()
  maxQueuedAgeMs: 30000     // Max age for queued messages
});

// Initialize -- recommended to await before sending messages
// Messages sent before ready() are queued (up to the above limits) and flushed afterward
await sc.ready();

// Properties
sc.socket           // Underlying Socket.IO instance
sc.ActivityStreams   // ActivityStreams helper library

// Methods
sc.clearCredentials()  // Remove stored credentials

// Events
sc.socket.on('message', handler)         // Incoming platform messages
sc.socket.on('connect', handler)         // Socket.IO transport connected
sc.socket.on('connect_error', handler)   // Socket.IO connection failed
sc.socket.on('disconnect', handler)      // Socket.IO transport disconnected
sc.socket.on('ready', handler)           // Schema registry loaded; client is ready
sc.socket.on('init_error', handler)      // Client initialization failed
sc.socket.on('client_error', handler)    // Client-side validation error
sc.socket.emit('message', activity, cb)  // Send ActivityStreams message; cb(result) on response
sc.socket.emit('credentials', creds, cb) // Set platform credentials; cb(result) on response
```

**Responses and async events.** For client-initiated actions (`message`,
`credentials`, etc.), pass an ack callback to `emit`:

```javascript
sc.socket.emit('message', activity, (result) => {
  if (result?.error) { /* failed */ return; }
  /* succeeded */
});
```

Treat any callback payload containing an `error` property as failure.

Not every inbound message is a direct response to your last request.
Platforms also push messages asynchronously (e.g. incoming IRC `PRIVMSG`,
XMPP presence updates) via the `message` event — handle them on
`sc.socket.on('message', ...)`.

### IRC Credentials

```javascript
{
  type: 'credentials',
  nick: 'nickname',
  server: 'irc.libera.chat',
  port: 6697,
  secure: true,
  password: 'optional',
  sasl: false
}
```

### XMPP Credentials

```javascript
{
  type: 'credentials',
  userAddress: 'user@domain',
  password: 'secret',
  resource: 'device-identifier'
}
```

## Requirements

- Bun >= 1.2.4 (or Node.js 18+)
- Redis >= 6.0

## Related Packages

- `@sockethub/client` - Browser/Node client library
- `@sockethub/server` - Core server implementation
- `@sockethub/schemas` - Schema registry and validation
- `@sockethub/activity-streams` - ActivityStreams utilities
- `@sockethub/crypto` - Session credential encryption
- `@sockethub/data-layer` - Redis/BullMQ data abstraction
- `@sockethub/logger` - Structured Winston logging
- `@sockethub/platform-irc` - IRC platform
- `@sockethub/platform-xmpp` - XMPP platform
- `@sockethub/platform-feeds` - RSS/Atom platform
- `@sockethub/irc2as` - IRC-to-ActivityStreams translator

- `references/platforms.md` for per-platform verbs and credential details
- `references/schema-validation.md` for message and credential validation
- `references/architecture.md` for process model, encryption, and sharing rules
