---
name: figma
description: Convert Figma designs to code. Use when user shares a Figma URL, mentions Figma, asks to implement a design/mockup/wireframe, needs design tokens, or wants to analyze design structure.
---

# Figma

Convert Figma designs to React+Tailwind code.

## Commands

Run via `scripts/figma`:

```bash
scripts/figma design-context              # Get code for selected node
scripts/figma design-context --node-id=1:2  # Get code for specific node
scripts/figma design-context --raw        # Full JSON output

scripts/figma screenshot                  # Save screenshot of selected node
scripts/figma screenshot --node-id=1:2

scripts/figma variables                   # Get design tokens (colors, fonts)
scripts/figma metadata                    # Get XML structure of selected node
scripts/figma metadata --node-id=0:1      # List top-level page sections
```

## Workflow

1. Run `scripts/figma design-context` to get React+Tailwind code
2. Run `scripts/figma screenshot` for visual reference
3. Adapt the code to match existing project patterns

## Node ID from URL

Extract node ID from Figma URLs: `node-id=1-2` → `--node-id=1:2`

## Codebase Patterns

Adapt generated code to match these patterns:

**Stack**: React + TypeScript, Tailwind CSS, React Query

**Data fetching**: `useQuery` from React Query
```tsx
const { data, refetch } = useQuery({
  queryKey: ['key', id],
  queryFn: () => api.fetch(id),
});
```

**State**: Context API for view-level state, `useState` for local UI state

**Icons**: Lucide React (`import { IconName } from 'lucide-react'`)

**Naming**:
- Handlers: `handleAction`, `onAction`
- State: `const [value, setValue] = useState()`
- Components: PascalCase files and exports

**UI Components**: MUI `Popover` for modals, Tippy for tooltips, `dayjs` for dates

## Requirements

- Figma Desktop must be running with a file open
- Script communicates with Figma's local MCP server on port 3845
