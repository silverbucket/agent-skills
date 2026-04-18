# Sockethub Schema and Validation Reference

Use this file when the user needs exact payload shape, validation behavior, or
the difference between `credentials` and `message`.

## Schema Registry

The client loads the schema registry during `await sc.ready()`. That registry
contains:

- enabled platform IDs
- supported verbs
- platform credential schemas
- ActivityStreams validation rules

## Context Handling

Prefer:

```javascript
sc.contextFor('irc')
```

Instead of hand-writing:

```javascript
[
  'https://www.w3.org/ns/activitystreams',
  'https://sockethub.org/ns/context/v1.jsonld',
  'https://sockethub.org/ns/context/platform/irc/v1.jsonld'
]
```

Use raw arrays only when the user specifically needs the canonical URLs.

## Event Types

- Use the `credentials` Socket.IO event for credential payloads.
- Use the `message` Socket.IO event for verbs like `connect`, `join`, `send`,
  `fetch`, `query`, and `disconnect`.

This distinction matters. A valid credential payload sent on the wrong event is
still the wrong API usage.

## Common ActivityStreams Shape

```javascript
{
  '@context': sc.contextFor('irc'),
  type: 'send',
  actor: { id: 'user@example', type: 'person' },
  target: { id: '#room@example', type: 'room' },
  object: { type: 'message', content: 'Hello.' }
}
```

## Credential Shape

```javascript
{
  '@context': sc.contextFor('irc'),
  type: 'credentials',
  actor: { id: 'user@example', type: 'person' },
  object: {
    type: 'credentials',
    // platform-specific fields
  }
}
```

## Secret-Sensitive Fields

Treat these fields as secrets in examples and responses:

- `password`
- `token`

Guidance:

- Keep example values in env vars or placeholders.
- Never echo real secret values back to the user.
- If comparing schemas, distinguish between the schema field name and the
  recommended runtime source of the value.

## Validation Flow

1. Sockethub resolves the platform from `@context`.
2. It validates the outer ActivityStreams envelope.
3. It validates the verb against the selected platform.
4. It validates the object payload against the platform schema.
5. Failures surface through callback errors and `failed` events.

## Common Validation Notes

- `type: 'credentials'` is required both at the top level and inside
  `object.type` for credential payloads.
- IRC credentials may include either `password` or `token`, but not both.
- XMPP credentials use the `password` schema field even when the runtime value
  is a deployment-issued token string.
- Server responses may include ActivityStreams core types such as `collection`
  and `create`, especially for feeds.
