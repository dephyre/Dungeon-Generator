#!/usr/bin/env python3
"""
Procedural Dungeon Map Generator for Roguelike Games

This script generates text-based dungeon maps with rooms, corridors,
treasures, traps, enemies, and staircases.

Usage:
    python dungeon_generator.py [width] [height]

Defaults to 30x15 if no arguments provided.
"""

import random


class Room:
    """Represents a rectangular room in the dungeon."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def intersects(self, other: "Room") -> bool:
        """Check if this room intersects with another room."""
        return not (
            self.x + self.width <= other.x
            or other.x + other.width <= self.x
            or self.y + self.height <= other.y
            or other.y + other.height <= self.y
        )


class Dungeon:
    """Main dungeon class handling map generation."""

    WALL = "#"
    FLOOR = "."
    DOOR = "D"
    STAIRS_UP = "U"  # Entrance
    STAIRS_DOWN = "X"  # Exit (changed from 'E' to avoid conflict with enemy)
    TREASURE = "T"
    TRAP = "^"
    ENEMY = "E"

    def __init__(
        self,
        width: int,
        height: int,
        room_count: int = 8,
        min_room_size: tuple = (3, 3),
        max_room_size: tuple = (8, 8),
        corridor_min_size: int = 5,
        feature_density: float = 0.3,
    ):
        self.width = width
        self.height = height
        self.rooms = []
        self.corridors = []
        self.features = []  # (x, y, char)
        self.grid = None

        self.min_room_size = min_room_size
        self.max_room_size = max_room_size
        self.corridor_min_size = corridor_min_size
        self.feature_density = feature_density

    def generate(self) -> str:
        """Generate the dungeon map and return as string."""
        # Initialize grid with walls
        self.grid = [["#" for _ in range(self.width)] for _ in range(self.height)]
        self.rooms = []

        # Generate rooms
        self._generate_rooms()

        # Connect all rooms with corridors
        self._connect_rooms()

        # Place features (treasures, traps, enemies)
        self._place_features()

        # Place entrance and exits
        self._place_entrance_exits()

        # Convert grid to string and return
        return "\n".join("".join(row) for row in self.grid)

    def _generate_rooms(self) -> None:
        """Generate rooms that don't intersect with each other."""
        while len(self.rooms) < 8:
            # Random room dimensions
            room_width = random.randint(self.min_room_size[0], self.max_room_size[0])
            room_height = random.randint(self.min_room_size[1], self.max_room_size[1])

            # Ensure room fits within bounds with some margin
            max_x = self.width - room_width - 2
            max_y = self.height - room_height - 2

            if max_x <= 0 or max_y <= 0:
                continue

            # Random position
            x = random.randint(1, max_x)
            y = random.randint(1, max_y)

            new_room = Room(x, y, room_width, room_height)

            # Check if room intersects with existing rooms
            if any(room.intersects(new_room) for room in self.rooms):
                continue

            # Carve out room
            self._carve_room(new_room)
            self.rooms.append(new_room)

        # If we have more than 8 rooms, remove the last few
        if len(self.rooms) > 8:
            self.rooms = self.rooms[:8]

    def _carve_room(self, room: Room) -> None:
        """Carve out a room by placing floor tiles."""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                self.grid[y][x] = self.FLOOR

    def _connect_rooms(self) -> None:
        """Connect all rooms with corridors using random walk."""
        if not self.rooms:
            return

        # Sort rooms so first room connects to the second, etc.
        # This ensures connectivity
        for i in range(1, len(self.rooms)):
            self._create_corridor(self.rooms[i - 1], self.rooms[i])

    def _create_corridor(self, start: Room, end: Room) -> None:
        """Create a corridor connecting two rooms using random walk."""
        x1, y1 = start.x + start.width // 2, start.y + start.height // 2
        x2, y2 = end.x + end.width // 2, end.y + end.height // 2

        # Create corridor with some randomness
        if random.random() < 0.5:
            # Horizontal then vertical
            self._carve_horizontal(x1, x2, y1)
            self._carve_vertical(y1, y2, x2)
        else:
            # Vertical then horizontal
            self._carve_vertical(y1, y2, x1)
            self._carve_horizontal(x1, x2, y2)

    def _carve_horizontal(self, x1: int, x2: int, y: int) -> None:
        """Carve a horizontal corridor."""
        x = min(x1, x2)
        while x <= max(x1, x2):
            if self.grid[y][x] == self.WALL or self.grid[y][x] in [
                self.DOOR,
                self.STAIRS_UP,
                self.STAIRS_DOWN,
            ]:
                self.grid[y][x] = self.FLOOR
            x += 1

    def _carve_vertical(self, y1: int, y2: int, x: int) -> None:
        """Carve a vertical corridor."""
        y = min(y1, y2)
        while y <= max(y1, y2):
            if self.grid[y][x] == self.WALL or self.grid[y][x] in [
                self.DOOR,
                self.STAIRS_UP,
                self.STAIRS_DOWN,
            ]:
                self.grid[y][x] = self.FLOOR
            y += 1

    def _place_features(self) -> None:
        """Randomly place treasures, traps, and enemies on the floor."""
        # Calculate number of features based on dungeon size
        num_features = max(3, int(self.width * self.height * self.feature_density / 20))

        feature_types = [
            (self.TREASURE, "treasure"),
            (self.TRAP, "trap"),
            (self.ENEMY, "enemy"),
        ]

        # Shuffle to randomize placement
        random.shuffle(feature_types)

        for _ in range(num_features):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)

            # Only place on floor tiles, not in rooms
            if self.grid[y][x] == self.FLOOR and (x, y) not in self._room_tiles():
                feature = feature_types[0][0]
                self.grid[y][x] = feature
                self.features.append((x, y, feature))
                feature_types.pop(0)

    def _room_tiles(self) -> set:
        """Get all tiles occupied by rooms."""
        tiles = set()
        for room in self.rooms:
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    tiles.add((x, y))
        return tiles

    def _place_entrance_exits(self) -> None:
        """Place entrance and exits on floor tiles."""
        # Place entrance at the first available floor tile at the edge of the first room
        if self.rooms:
            entrance_found = False
            first_room = self.rooms[0]

            # Check the top edge (y = room.y - 1, from room.x to room.x + room.width)
            for x in range(first_room.x, first_room.x + first_room.width):
                if 0 <= first_room.y - 1 < self.height:
                    if (x, first_room.y - 1) not in self.features:
                        # FIX: Only place on FLOOR tiles, NOT WALL
                        if self.grid[first_room.y - 1][x] == self.FLOOR:
                            self.grid[first_room.y - 1][x] = self.STAIRS_UP
                            entrance_found = True
                            break

            if not entrance_found:
                # Check the left edge (x = room.x - 1, from room.y to room.y + room.height)
                for y in range(first_room.y, first_room.y + first_room.height):
                    if 0 <= first_room.x - 1 < self.width:
                        if (first_room.x - 1, y) not in self.features:
                            if self.grid[y][first_room.x - 1] == self.FLOOR:
                                self.grid[y][first_room.x - 1] = self.STAIRS_UP
                                entrance_found = True
                                break

            if not entrance_found:
                # Check the bottom edge
                for x in range(first_room.x, first_room.x + first_room.width):
                    if 0 <= first_room.y + first_room.height < self.height:
                        if (x, first_room.y + first_room.height) not in self.features:
                            if (
                                self.grid[first_room.y + first_room.height][x]
                                == self.FLOOR
                            ):
                                self.grid[first_room.y + first_room.height][x] = (
                                    self.STAIRS_UP
                                )
                                entrance_found = True
                                break

            if not entrance_found:
                # Check the right edge
                for y in range(first_room.y, first_room.y + first_room.height):
                    if 0 <= first_room.x + first_room.width < self.width:
                        if (first_room.x + first_room.width, y) not in self.features:
                            if (
                                self.grid[y][first_room.x + first_room.width]
                                == self.FLOOR
                            ):
                                self.grid[y][first_room.x + first_room.width] = (
                                    self.STAIRS_UP
                                )
                                entrance_found = True
                                break

        # Exits: place in 1-3 random rooms (not the first one)
        if len(self.rooms) > 1:
            num_exits = random.randint(1, min(3, len(self.rooms) - 1))
            exit_rooms = random.sample(self.rooms[1:], num_exits)

            for room in exit_rooms:
                # Place exit at center of room
                exit_x = room.x + room.width // 2
                exit_y = room.y + room.height // 2

                if 0 <= exit_y < self.height and 0 <= exit_x < self.width:
                    # Only place if not already occupied by a feature
                    if (exit_x, exit_y) not in self.features:
                        self.grid[exit_y][exit_x] = "X"

    def _place_entrance_exits(self) -> None:
        """Place entrance and exits on floor tiles."""
        # Place entrance at the first available floor tile at the edge of the first room
        if self.rooms:
            entrance_found = False
            first_room = self.rooms[0]

            # Check the top edge (y = room.y - 1, from room.x to room.x + room.width)
            for x in range(first_room.x, first_room.x + first_room.width):
                if 0 <= first_room.y - 1 < self.height:
                    if (x, first_room.y - 1) not in self.features:
                        # FIX: Only place on FLOOR tiles, NOT WALL
                        if self.grid[first_room.y - 1][x] == self.FLOOR:
                            self.grid[first_room.y - 1][x] = self.STAIRS_UP
                            entrance_found = True
                            break

            if not entrance_found:
                # Check the left edge (x = room.x - 1, from room.y to room.y + room.height)
                for y in range(first_room.y, first_room.y + first_room.height):
                    if 0 <= first_room.x - 1 < self.width:
                        if (first_room.x - 1, y) not in self.features:
                            if self.grid[y][first_room.x - 1] == self.FLOOR:
                                self.grid[y][first_room.x - 1] = self.STAIRS_UP
                                entrance_found = True
                                break

            if not entrance_found:
                # Check the bottom edge
                for x in range(first_room.x, first_room.x + first_room.width):
                    if 0 <= first_room.y + first_room.height < self.height:
                        if (x, first_room.y + first_room.height) not in self.features:
                            if (
                                self.grid[first_room.y + first_room.height][x]
                                == self.FLOOR
                            ):
                                self.grid[first_room.y + first_room.height][x] = (
                                    self.STAIRS_UP
                                )
                                entrance_found = True
                                break

            if not entrance_found:
                # Check the right edge
                for y in range(first_room.y, first_room.y + first_room.height):
                    if 0 <= first_room.x + first_room.width < self.width:
                        if (first_room.x + first_room.width, y) not in self.features:
                            if (
                                self.grid[y][first_room.x + first_room.width]
                                == self.FLOOR
                            ):
                                self.grid[y][first_room.x + first_room.width] = (
                                    self.STAIRS_UP
                                )
                                entrance_found = True
                                break

        # Exits: place in 1-3 random rooms (not the first one)
        if len(self.rooms) > 1:
            num_exits = random.randint(1, min(3, len(self.rooms) - 1))
            exit_rooms = random.sample(self.rooms[1:], num_exits)

            for room in exit_rooms:
                # Place exit at center of room
                exit_x = room.x + room.width // 2
                exit_y = room.y + room.height // 2

                if 0 <= exit_y < self.height and 0 <= exit_x < self.width:
                    # Only place if not already occupied by a feature
                    if (exit_x, exit_y) not in self.features:
                        self.grid[exit_y][exit_x] = "X"


def generate_dungeon(width: int = 30, height: int = 15) -> str:
    """
    Generate a dungeon map with the given dimensions.

    Args:
        width: Width of the dungeon in tiles
        height: Height of the dungeon in tiles

    Returns:
        String representation of the dungeon map
    """
    dungeon = Dungeon(width, height)
    return dungeon.generate()


def main():
    """Main entry point for the script."""
    import sys

    # Parse command line arguments
    width = 30
    height = 15

    if len(sys.argv) > 1:
        width = int(sys.argv[1])
    if len(sys.argv) > 2:
        height = int(sys.argv[2])

    # Validate dimensions
    if width < 10 or height < 10:
        print("Warning: Dungeon too small. Using minimum size 10x10.")
        width = max(width, 10)
        height = max(height, 10)

    if width > 100 or height > 50:
        print("Warning: Dungeon too large. Cap at 100x50.")
        width = min(width, 100)
        height = min(height, 50)

    # Generate and print the dungeon
    print(f"Generating {width}x{height} dungeon...")
    print()
    print(generate_dungeon(width, height))


if __name__ == "__main__":
    main()

