# Fix Strategies

## Decision Flowchart

```
Shared entity/DTO needed by both?
  YES → Strategy 1: Extract Shared Module
  NO ↓
Cross-module workflow (A calls B, B calls A)?
  YES → Strategy 2: Orchestrator Module
  NO ↓
Fire-and-forget side effect (notification, cascade)?
  YES → Strategy 3: Events (EventEmitter2 or @nestjs/cqrs)
  NO ↓
Service A needs 1-2 methods from Service B?
  YES → Strategy 4: DIP with Abstract Class
  NO ↓
Too many exports creating coupling surface?
  YES → Strategy 5: Facade
  NO ↓
Urgent unblock, real fix planned?
  YES → Strategy 6: forwardRef() + tech debt ticket
```

---

## Strategy 1: Extract Shared Module

```
BEFORE: OrdersModule <-> UsersModule (both need UserEntity)
AFTER:  SharedUsersModule (exports UserEntity)
        OrdersModule -> SharedUsersModule
        UsersModule -> SharedUsersModule
```

Keep extracted module small — entities, DTOs, value objects only.
In DDD: this is the Shared Kernel. Cap at ~5 exports.

## Strategy 2: Orchestrator Module

```typescript
@Module({
  imports: [AuthorsModule, BooksModule],
  providers: [PublishingService],
})
export class PublishingModule {}
```

Orchestrator represents a **use case**, not a data model. Neither
AuthorsModule nor BooksModule knows it exists.

## Strategy 3: Event-Based Decoupling

```typescript
// Emitter (orders) — no import of inventory
this.eventEmitter.emit('order.created', new OrderCreatedEvent(order));

// Listener (inventory) — no import of orders
@OnEvent('order.created')
handleOrderCreated(event: OrderCreatedEvent) { ... }
```

Use typed event classes. Not suitable when caller needs a return value.
For structured event flows, use `@nestjs/cqrs` CommandBus/EventBus.

## Strategy 4: DIP with Abstract Class

```typescript
// Consumer defines the contract (in orders module)
export abstract class UserLookup {
  abstract findById(id: string): Promise<UserDto>;
}

// Provider implements it (in users module)
@Module({
  providers: [UsersService, { provide: UserLookup, useExisting: UsersService }],
  exports: [UserLookup],
})
export class UsersModule {}
```

Abstract class survives TS transpilation → works as injection token.
Dependency flows one way: Orders → Users.

## Strategy 5: Facade

```typescript
@Module({
  providers: [OrderFacade, OrderFactory, OrderValidator /* internal */],
  exports: [OrderFacade],  // single public API
})
export class OrderModule {}
```

Fewer exports = fewer reasons for other modules to create back-dependencies.

## Strategy 6: forwardRef() (last resort)

```typescript
@Module({ imports: [forwardRef(() => UsersModule)] })
export class OrdersModule {}
```

Always add: `// TODO: remove forwardRef — extract shared module (ticket #XXX)`

---

## Multi-Cycle Projects

1. Map all cycles before fixing any — one fix may resolve several.
2. Fix smallest cycles first (2-module), then transitive chains.
3. If module A appears in multiple cycles → A has too many responsibilities. Split it.

## Coupling Type Quick Reference

| Signal | Coupling | Best Strategy |
|--------|----------|---------------|
| Same Entity used by both | Data | Extract Shared Module |
| Service A triggers side effect in B | Temporal | Events |
| Service A needs 1 method from B | Interface | DIP Abstract Class |
| Both services need each other for workflow | Orchestration | Orchestrator Module |
| Module uses `@Global()` to skip imports | Hidden | Restructure layers |
| Barrel file creates indirect cycle | Accidental | Fix barrel, use direct imports |
