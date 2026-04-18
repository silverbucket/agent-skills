# Sockethub Platform Reference

Use this file when the user needs platform-specific verbs, credentials, or
behavior. Keep the main answer focused on one platform at a time unless the
user is explicitly comparing them.

## Secret Handling

- Never include a real password or token in examples.
- Prefer placeholders or environment variables.
- Prefer tokens over passwords when the platform supports them.
- Use the literal schema field names only when describing the payload shape.

## IRC Platform (`irc`)

**Type:** Persistent  
**Package:** `@sockethub/platform-irc`

### Credentials

Preferred token-based example:

```javascript
sc.socket.emit('credentials', {
  '@context': sc.contextFor('irc'),
  type: 'credentials',
  actor: { id: 'mynick@irc.libera.chat', type: 'person' },
  object: {
    type: 'credentials',
    nick: 'mynick',
    server: 'irc.libera.chat',
    token: process.env.SOCKETHUB_IRC_TOKEN,
    port: 6697,
    secure: true
  }
});
```

Supported credential fields:

| Field | Required | Notes |
|---|---|---|
| `type` | yes | Must be `"credentials"`. |
| `nick` | yes | IRC nickname. |
| `server` | yes | IRC server hostname. |
| `port` | no | Defaults depend on server and TLS usage. |
| `secure` | no | Enables TLS. |
| `username` | no | Optional alternate username. |
| `password` | no | Traditional SASL/server password. |
| `token` | no | Preferred when the network supports PAT or bearer-style auth. |
| `sasl` | no | Enables SASL handling. |
| `saslMechanism` | no | `PLAIN` or `OAUTHBEARER`. |

Rules:

- `password` and `token` are mutually exclusive.
- If `saslMechanism` is `OAUTHBEARER`, a `token` is required.
- If the network supports PAT-style auth, prefer `token` over `password`.
- Non-empty `password` or `token` credentials are shareable across sockets.
- Username-only credentials are treated as anonymous and may collide with
  `username already in use`.

### Supported Actions

| Action | Description | Requires Target |
|---|---|---|
| `connect` | Connect to the IRC server using stored credentials | No |
| `join` | Join a channel | Yes |
| `leave` | Leave a channel | Yes |
| `send` | Send a channel or direct message | Yes |
| `update` | Update nick, topic, or presence-like state | Depends |
| `query` | Query channel or user information | Yes |
| `disconnect` | Disconnect from the IRC server | No |

### IRC-Specific Behavior

- Actor IDs are typically expressed as `nick@server`.
- Channel targets use `#channel@server`.
- Incoming events are translated through `@sockethub/irc2as`.
- Topic, nick, and attendance changes arrive as normal ActivityStreams objects.

## XMPP Platform (`xmpp`)

**Type:** Persistent  
**Package:** `@sockethub/platform-xmpp`

### Credentials

```javascript
sc.socket.emit('credentials', {
  '@context': sc.contextFor('xmpp'),
  type: 'credentials',
  actor: { id: 'user@jabber.net', type: 'person' },
  object: {
    type: 'credentials',
    userAddress: 'user@jabber.net',
    password: process.env.SOCKETHUB_XMPP_SECRET,
    resource: 'web'
  }
});
```

Supported credential fields:

| Field | Required | Notes |
|---|---|---|
| `type` | yes | Must be `"credentials"`. |
| `userAddress` | yes | Bare JID such as `user@jabber.net`. |
| `resource` | yes | Resource identifier such as `"web"` or `"phone"`. |
| `password` | yes | The XMPP secret slot. Use a password or a compatible deployment-issued token string. |
| `server` | no | Optional hostname override. |
| `port` | no | Optional port override. |

Rules:

- Upstream XMPP credentials expose only the `password` field name.
- If the deployment accepts a bearer-style token in the SASL PLAIN password
  slot, pass the token string as `password`.
- Prefer the token path when the deployment explicitly supports it.
- Do not claim first-class support for dedicated token SASL mechanisms such as
  `OAUTHBEARER`, `X-OAUTH2`, `X-TOKEN`, or FAST in the bundled client.

### Supported Actions

| Action | Description | Requires Target |
|---|---|---|
| `connect` | Connect to the XMPP server | No |
| `join` | Join a MUC room | Yes |
| `leave` | Leave a MUC room | Yes |
| `send` | Send a direct or room message | Yes |
| `update` | Update presence or status | No |
| `request-friend` | Send a roster subscription request | Yes |
| `make-friend` | Accept a roster subscription | Yes |
| `remove-friend` | Remove a roster subscription | Yes |
| `query` | Query roster or room information | Optional |
| `disconnect` | Disconnect from the server | No |

### XMPP-Specific Behavior

- Failed auth with either a password or a token-in-password-slot usually
  surfaces as `SASLError: not-authorized`.
- Sockethub keeps the credentials schema small and delegates most SASL behavior
  to the bundled `@xmpp/client`.

## Feeds Platform (`feeds`)

**Type:** Stateless  
**Package:** `@sockethub/platform-feeds`

### Supported Actions

| Action | Description |
|---|---|
| `fetch` | Fetch and parse an RSS or Atom feed URL |

Example:

```javascript
sc.socket.emit('message', {
  '@context': sc.contextFor('feeds'),
  type: 'fetch',
  actor: { id: 'https://blog.example.com/feed.xml' }
});
```

Response patterns:

- Feed responses commonly come back as a `collection`.
- Individual items often appear as `create` activities whose `object` contains
  the entry content.

## Metadata Platform (`metadata`)

**Type:** Stateless  
**Package:** `@sockethub/platform-metadata`

### Supported Actions

| Action | Description |
|---|---|
| `fetch` | Extract Open Graph and page metadata from a URL |

Example:

```javascript
sc.socket.emit('message', {
  '@context': sc.contextFor('metadata'),
  type: 'fetch',
  actor: { id: 'https://example.com/article' }
});
```

Typical response fields:

- `title`
- `description`
- `image`
- `url`

## Dummy Platform (`dummy`)

**Type:** Stateless  
**Package:** `@sockethub/platform-dummy`

Use this platform first when the user wants to verify local Sockethub wiring
before introducing external credentials or network dependencies.

```javascript
sc.socket.emit('message', {
  '@context': sc.contextFor('dummy'),
  type: 'send',
  actor: { id: 'test-user', type: 'person' },
  object: { type: 'message', content: 'echo test' }
});
```
