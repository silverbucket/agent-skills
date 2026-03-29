# Sockethub Platform Reference

## IRC Platform (`irc`)

**Type:** Persistent
**Package:** `@sockethub/platform-irc`

### Credentials

```javascript
sc.socket.emit('credentials', {
  '@context': [
    'https://www.w3.org/ns/activitystreams',
    'https://sockethub.org/ns/context/v1.jsonld',
    'https://sockethub.org/ns/context/platform/irc/v1.jsonld'
  ],
  type: 'credentials',
  actor: { id: 'mynick@irc.libera.chat' },
  object: {
    type: 'credentials',
    nick: 'mynick',           // Required: IRC nickname
    server: 'irc.libera.chat', // Required: IRC server hostname
    port: 6697,               // Optional: default 6667 (or 6697 for TLS)
    secure: true,             // Optional: use TLS (default: false)
    password: '',             // Optional: server password
    sasl: false               // Optional: use SASL authentication
  }
});
```

### Supported Actions

| Action | Description | Requires Target |
|--------|-------------|-----------------|
| `connect` | Connect to IRC server using stored credentials | No |
| `join` | Join a channel | Yes (room) |
| `leave` | Leave a channel | Yes (room) |
| `send` | Send a message to a channel or user | Yes (room or person) |
| `update` | Update nick or topic | Depends on update type |
| `query` | Query channel or user information | Yes |
| `disconnect` | Disconnect from IRC server | No |

### IRC-Specific Behavior

- Actor IDs follow the pattern `nick@server` (e.g., `mynick@irc.libera.chat`)
- Channel targets use `#channel@server` (e.g., `#sockethub@irc.libera.chat`)
- Incoming messages are converted via `@sockethub/irc2as` translator
- Nick changes emit `update` messages with `object.type: 'address'`
- Topic changes emit `update` messages with `object.type: 'topic'`
- User join/leave events emit corresponding `join`/`leave` messages
- Presence changes (away, back) emit messages with `object.type: 'presence'`
- Channel user lists come as `attendance` type objects

### Example: Send a channel message

```javascript
sc.socket.emit('message', {
  '@context': [
    'https://www.w3.org/ns/activitystreams',
    'https://sockethub.org/ns/context/v1.jsonld',
    'https://sockethub.org/ns/context/platform/irc/v1.jsonld'
  ],
  type: 'send',
  actor: { id: 'mynick@irc.libera.chat', type: 'person' },
  target: { id: '#sockethub@irc.libera.chat', type: 'room' },
  object: { type: 'message', content: 'Hello channel!' }
});
```

---

## XMPP Platform (`xmpp`)

**Type:** Persistent
**Package:** `@sockethub/platform-xmpp`

### Credentials

```javascript
sc.socket.emit('credentials', {
  '@context': [
    'https://www.w3.org/ns/activitystreams',
    'https://sockethub.org/ns/context/v1.jsonld',
    'https://sockethub.org/ns/context/platform/xmpp/v1.jsonld'
  ],
  type: 'credentials',
  actor: { id: 'user@jabber.org' },
  object: {
    type: 'credentials',
    userAddress: 'user@jabber.org',  // Required: full JID
    password: 'secret',              // Required: account password
    resource: 'web'                  // Optional: resource identifier
  }
});
```

### Supported Actions

| Action | Description | Requires Target |
|--------|-------------|-----------------|
| `connect` | Connect to XMPP server | No |
| `join` | Join a MUC (multi-user chat) room | Yes (room) |
| `leave` | Leave a MUC room | Yes (room) |
| `send` | Send a message | Yes (person or room) |
| `update` | Update presence or status | No |
| `request-friend` | Send a roster subscription request | Yes (person) |
| `make-friend` | Accept a roster subscription | Yes (person) |
| `remove-friend` | Remove a roster subscription | Yes (person) |
| `query` | Query roster or room info | Optional |
| `disconnect` | Disconnect from XMPP server | No |

### Example: Send a direct message

```javascript
sc.socket.emit('message', {
  '@context': [
    'https://www.w3.org/ns/activitystreams',
    'https://sockethub.org/ns/context/v1.jsonld',
    'https://sockethub.org/ns/context/platform/xmpp/v1.jsonld'
  ],
  type: 'send',
  actor: { id: 'user@jabber.org', type: 'person' },
  target: { id: 'friend@jabber.org', type: 'person' },
  object: { type: 'message', content: 'Hello!' }
});
```

---

## Feeds Platform (`feeds`)

**Type:** Stateless
**Package:** `@sockethub/platform-feeds`

### Supported Actions

| Action | Description |
|--------|-------------|
| `fetch` | Fetch and parse an RSS/Atom feed URL |

Supports RSS 2.0, Atom 1.0, and RSS 1.0/RDF formats. Uses `podparse` for parsing.

### Example: Fetch a feed

```javascript
sc.socket.emit('message', {
  '@context': [
    'https://www.w3.org/ns/activitystreams',
    'https://sockethub.org/ns/context/v1.jsonld',
    'https://sockethub.org/ns/context/platform/feeds/v1.jsonld'
  ],
  type: 'fetch',
  actor: { id: 'https://blog.example.com/feed.xml' }
});
```

### Response Format

The response is a Collection of Create activities:

```javascript
{
  '@context': [...],
  type: 'fetch',
  actor: { id: 'https://blog.example.com/feed.xml' },
  object: {
    type: 'collection',
    items: [
      {
        type: 'create',
        object: {
          type: 'message',
          title: 'Article Title',
          url: 'https://blog.example.com/article',
          content: 'Article summary...',
          published: '2026-03-15T10:00:00Z'
        }
      }
    ]
  }
}
```

---

## Metadata Platform (`metadata`)

**Type:** Stateless
**Package:** `@sockethub/platform-metadata`

### Supported Actions

| Action | Description |
|--------|-------------|
| `fetch` | Extract Open Graph and page metadata from a URL |

Uses `open-graph-scraper` to extract OG tags, page titles, descriptions, and images.

### Example: Fetch page metadata

```javascript
sc.socket.emit('message', {
  '@context': [
    'https://www.w3.org/ns/activitystreams',
    'https://sockethub.org/ns/context/v1.jsonld',
    'https://sockethub.org/ns/context/platform/metadata/v1.jsonld'
  ],
  type: 'fetch',
  actor: { id: 'https://example.com/article' }
});
```

### Response Format

```javascript
{
  '@context': [...],
  type: 'fetch',
  actor: { id: 'https://example.com/article' },
  object: {
    type: 'message',
    title: 'Page Title',
    description: 'Page description from OG tags',
    image: 'https://example.com/og-image.jpg',
    url: 'https://example.com/article'
  }
}
```

---

## Dummy Platform (`dummy`)

**Type:** Stateless
**Package:** `@sockethub/platform-dummy`

An echo/testing platform for development and integration testing. Echoes back
any message sent to it. Useful for verifying Sockethub server setup without
needing external services.

```javascript
sc.socket.emit('message', {
  '@context': [
    'https://www.w3.org/ns/activitystreams',
    'https://sockethub.org/ns/context/v1.jsonld',
    'https://sockethub.org/ns/context/platform/dummy/v1.jsonld'
  ],
  type: 'send',
  actor: { id: 'test-user' },
  object: { type: 'message', content: 'echo test' }
});
```
