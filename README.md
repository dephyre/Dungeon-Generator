```markdown
# Procedural Dungeon Map Generator

A Python script for generating text-based dungeon maps for roguelike games. Uses procedural generation to create unique, random dungeons every time you play.

## Features

- **Procedural Generation** - Every dungeon is uniquely generated
- **Room & Corridor System** - Classic roguelike room layout with connecting corridors
- **Random Features** - Treasures, traps, and enemies scattered throughout
- **Configurable Size** - Set dungeon dimensions via command line
- **Guaranteed Connectivity** - All rooms are reachable from the entrance
- **No Dependencies** - Pure Python, uses only the standard library

## Requirements

- Python 3.6+
- No external dependencies required

## Installation

No installation needed - just clone or download the script:

```bash
git clone <your-repo-url>
cd dungeon
```

## Usage

### Basic Usage

```bash
python3 test.py [width] [height]
```

### Examples

Generate a standard 30x15 dungeon:
```bash
python3 test.py 30 15
```

Generate output and save to file:
```bash
python3 test.py 30 15 > dungeon.txt
```

Generate a larger dungeon:
```bash
python3 test.py 50 25
```

### Programmatic Usage

```python
from dungeon_generator import generate_dungeon, Dungeon

# Simple generation
dungeon = generate_dungeon(30, 15)
print(dungeon)

# Custom configuration
dungeon = Dungeon(
    width=50,
    height=25,
    min_room_size=(4, 4),
    max_room_size=(10, 10),
    feature_density=0.4
)
dungeon.generate()
```

## Character Legend

| Symbol | Meaning |
|--------|---------|
| `#` | Wall |
| `.` | Floor |
| `U` | Entrance (stairs up - your starting point) |
| `X` | Exit (stairs down - leads to next level) |
| `T` | Treasure (valuable item) |
| `^` | Trap (hazard - be careful!) |
| `E` | Enemy (combat encounter) |

## Generation Algorithm

The dungeon uses a **"Room and Corridor"** approach:

1. **Initialize Grid** - Create a 2D grid filled with wall tiles
2. **Generate Rooms** - Randomly place rectangular rooms that don't overlap
3. **Connect Rooms** - Use random walk pathfinding to connect adjacent rooms with corridors
4. **Place Features** - Randomly scatter treasures, traps, and enemies on floor tiles
5. **Place Entrance/Exit** - Place entrance at the first available floor tile near the first room; place 1-3 exits in other rooms

### Connectivity Guarantee

All rooms are guaranteed to be reachable from the entrance because:
- Rooms are connected sequentially (room 1 → room 2 → room 3, etc.)
- Corridors use guaranteed pathfinding (horizontal + vertical segments)
- This creates a connected graph where every room can be reached

## Configuration

### Command Line Arguments

```
python3 test.py [width] [height]
```

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `width` | int | 30 | Dungeon width in tiles |
| `height` | int | 15 | Dungeon height in tiles |

### Class Configuration

The `Dungeon` class accepts the following parameters:

```python
Dungeon(
    width: int,                 # Dungeon width
    height: int,                # Dungeon height
    room_count: int = 8,        # Target number of rooms
    min_room_size: tuple = (3, 3),  # Minimum room dimensions (w, h)
    max_room_size: tuple = (8, 8),  # Maximum room dimensions (w, h)
    corridor_min_size: int = 5, # Minimum corridor length
    feature_density: float = 0.3  # Feature placement density (0.0-1.0)
)
```

### Tips for Tuning

- **Smaller dungeons**: Reduce `width` and `height` to 20x10 or less
- **Larger dungeons**: Increase to 50x25 or more
- **More features**: Increase `feature_density` to 0.5 or higher
- **Smaller rooms**: Reduce `max_room_size` to (4, 4) or (5, 5)
- **More rooms**: Increase `room_count` parameter

## Limitations

- Corridors are simple (horizontal + vertical segments only)
- No diagonal movement between rooms
- Features don't account for combat balance
- No room for decorative elements (stairs, doors, etc.)

## Extending This Project

Potential extensions:

- Add **doors** at corridor intersections
- Implement **combat mechanics** for enemies
- Add **inventory system** for treasures
- Create **instance loading** for save states
- Add **multiple dungeon floors**
- Implement **BSP tree generation** for more complex layouts

## License

MIT License - feel free to use this for your personal projects!

## Contributing

Feel free to submit issues and pull requests! Improvements are welcome.
