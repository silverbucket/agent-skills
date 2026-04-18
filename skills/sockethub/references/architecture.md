# Sockethub Architecture

Use this file when the user needs process-model or lifecycle detail. Do not lead
with internals if the task is simply "how do I send a message".

## Multi-Process Model

Sockethub runs as cooperating processes:

```text
Web client <-> Sockethub server <-> Redis/BullMQ <-> platform workers
```

Main pieces:

- **Sockethub server**: Socket.IO entrypoint, validation, routing, credential
  storage, and platform orchestration
- **Platform workers**: One process per platform such as IRC, XMPP, Feeds, or
  Metadata
- **Redis + BullMQ**: Encrypted job queue plus credential/state storage
- **IPC**: Fast worker-to-server event path for inbound protocol messages

## Request Lifecycle

1. Client connects over Socket.IO.
2. Client calls `await sc.ready()` and receives the schema registry.
3. Client sends `credentials` for persistent platforms.
4. Server validates and encrypts credentials before storing them in Redis.
5. Client sends `connect`, `join`, `send`, or other ActivityStreams messages.
6. Server validates the message and enqueues work for the target platform.
7. Platform worker processes the job and emits translated ActivityStreams back
   to the client.

## Credential Storage

- Each socket session gets its own encryption secret.
- Credentials are encrypted before they are stored in Redis.
- Platform workers decrypt credentials only when they need to process jobs.
- Keys are not persisted across a server restart.

## Persistent vs Stateless Platforms

### Persistent

IRC and XMPP keep long-lived remote connections and track actor-specific state.

Important behavior:

- Sockethub can attach multiple sockets to one running platform instance when
  they target the same actor and the credentials pass share validation.
- Share is allowed only when credentials include a non-empty `password` or
  `token`.
- Username-only anonymous credentials are not shareable and may return
  `username already in use`.
- Sockethub allows a narrow reconnect exception for stale anonymous sessions
  when the reconnect comes from the same client IP.

### Stateless

- Queue naming: `sockethub:{parentId}:data-layer:queue:{platformId}`
- Each platform has its own dedicated queue
- Jobs are encrypted before enqueuing
- BullMQ fires internal `completed` / `failed` events when a job finishes;
  the server consumes them and delivers the result to the originating
  client either by invoking the per-emit ack callback stored for that job
  or, for broadcasts and peers, as a `message` Socket.IO event. The client
  does **not** receive `completed` / `failed` as Socket.IO events directly.

Feeds and Metadata process each request independently:

- no credential storage
- no `connect` step
- no long-lived remote session to reuse

## Failure Isolation

- A crashing platform worker does not take down the whole server.
- Failed jobs surface back to the client through callbacks or `failed` events.
- Platform heartbeat and timeout settings determine when workers are considered
  unhealthy and respawned.

## Practical Implications for Answers

- Mention Redis whenever explaining Sockethub deployment.
- Mention credential replay and `sc.clearCredentials()` whenever the user is
  asking about reconnects, logout, or account switching.
- Mention session sharing only for persistent platforms.
