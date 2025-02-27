# Guidelines for Claude Code

## Commands
- Run the game: `python main.py`
- No explicit test framework found
- Virtual environment: `source myenv/bin/activate` (macOS/Linux)

## Code Style
- **Formatting**: Follow PEP 8 conventions
- **Imports**: Group standard library, third-party, and local imports
- **Naming**:
  - Variables/functions: `snake_case`
  - Constants: `UPPERCASE`
  - Classes: `PascalCase`
- **Organization**:
  - Initialize game settings at top
  - Group related functionality in functions
  - Organize game loop with clear sections: event handling, logic, rendering

## Best Practices
- Add docstrings to functions
- Maintain reasonable line lengths (<100 chars)
- Use meaningful variable names
- Handle errors gracefully with try/except blocks where appropriate
- Comment complex game logic