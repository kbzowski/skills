# Context Patterns for Props Drilling Elimination

## Standard Context Pattern

```tsx
// contexts/event-form-context.tsx
import { createContext, useContext, type ReactNode } from 'react'

type EventFormContextValue = {
  formData: EventFormData
  setFormData: (data: EventFormData) => void
  errors: Record<string, string>
}

const EventFormContext = createContext<EventFormContextValue | null>(null)

export function useEventFormContext() {
  const ctx = useContext(EventFormContext)
  if (!ctx) throw new Error('useEventFormContext must be used within EventFormProvider')
  return ctx
}

export function EventFormProvider({ children, ...value }: EventFormContextValue & { children: ReactNode }) {
  return <EventFormContext.Provider value={value}>{children}</EventFormContext.Provider>
}
```

## When to split Context

Split into separate Contexts when:
- Part of the state changes frequently but other parts are stable (prevents unnecessary re-renders)
- Consumers only need a subset of the data

```tsx
// Split: frequently changing value vs stable config
const FilterValueContext = createContext<string>('')     // changes on every keystroke
const FilterConfigContext = createContext<FilterConfig | null>(null) // changes rarely
```

## When NOT to use Context

- Prop passes through only 1 intermediate level - just pass the prop
- Data is used by a single child - prop is fine
- Component composition (children/render props) solves the problem more simply

## Composition alternative

Before reaching for Context, check if component composition eliminates the drilling:

```tsx
// BEFORE: drilling onClick through 3 levels
<Page onClick={handleClick}>      // passes down
  <Section onClick={onClick}>     // passes down
    <Button onClick={onClick} />  // actually uses it

// AFTER: composition - no drilling
<Page>
  <Section>
    <Button onClick={handleClick} />  // direct
```

Prefer composition when:
- The intermediate components don't use the prop at all
- The tree structure allows restructuring without breaking layout
