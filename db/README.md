# Database Directory (db/)

## Loot Economy Balance with Custom Content

### types_ref.xml vs types.xml

**`types_ref.xml`** contains the **vanilla DayZ loot economy** with original nominal counts as designed by Bohemia Interactive. This file serves as a reference and should **never be used directly** on a modded server.

**`types.xml`** is the **active loot table** used by the server. It contains **modified nominal counts** that are calculated to maintain proper loot economy balance when additional loot sources are added via:

- **Custom JSON files** in `/custom/` directory (static loot spawns)
- **Event-based static loot** from custom events
- **Trader inventories** and other mod-added content

### Why Nominal Counts Are Adjusted

When you add static loot spawns through custom JSON files or events, you're essentially **injecting additional items** into the server economy outside of the normal dynamic spawning system. Without adjusting the nominal counts in `types.xml`, this would result in:

- **Over-saturation** of certain items
- **Broken loot economy** balance  
- **Performance issues** from too many spawned objects
- **Unfair gameplay** advantages

### Example Scenario

If vanilla settings spawn 50 AK-74 rifles dynamically across the map, but you add 10 more AK-74s as static loot in custom locations, you now have 60 total rifles instead of the intended 50. To maintain balance, the nominal count in `types.xml` should be reduced to ~40 to compensate for the 10 static spawns.

## Workflow for Adding Custom Content

When adding new custom JSON files or events with static loot:

1. **Analyze the loot** - Count how many of each item type you're adding statically
2. **Adjust nominal counts** - Reduce the corresponding nominal values in `types.xml`
3. **Test balance** - Monitor server performance and loot distribution
4. **Document changes** - Keep track of modifications for future reference

## Best Practices

- **Always backup** `types.xml` before making changes
- **Use `types_ref.xml`** as your baseline for calculations  
- **Track custom additions** to know how much to reduce nominal counts
- **Test incrementally** - Make small adjustments and monitor results
- **Consider item rarity** - High-tier items need more careful balancing

---

**⚠️ Warning**: Using `types_ref.xml` directly on a server with custom content will result in loot economy imbalance and potential performance issues.