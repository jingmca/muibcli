"""Command: man

Category: Utilities
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger
from mutil.dispatch import DArg

from icli.cmds.base import IOp, command


@command(names=["man"])
@dataclass
class IOpManual(IOp):
    """Display detailed manual for specific commands (like Unix man)."""

    cmd: list[str] = field(default_factory=list, init=False)

    def argmap(self):
        return [
            DArg(
                "*cmd",
                desc="Command name to get manual (leave empty to list all commands)",
            )
        ]

    def parse_help_md(self):
        """Parse COMMANDS_HELP.md and return a dictionary of command help."""
        # Find the COMMANDS_HELP.md file in project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        help_file = project_root / "COMMANDS_HELP.md"

        if not help_file.exists():
            logger.error(f"Help file not found: {help_file}")
            return {}

        with open(help_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the markdown file
        commands = {}

        # Split by command sections (## command_name)
        sections = re.split(r'\n---\n', content)

        for section in sections:
            section = section.strip()
            if not section or section.startswith('#') and 'ICLI 命令参考手册' in section:
                continue

            # Extract command name
            cmd_match = re.match(r'^## (\w+)', section)
            if not cmd_match:
                continue

            cmd_name = cmd_match.group(1)

            # Extract metadata
            category_match = re.search(r'\*\*分类\*\*:\s*(.+)', section)
            alias_match = re.search(r'\*\*别名\*\*:\s*(.+)', section)
            desc_match = re.search(r'\*\*描述\*\*:\s*(.+)', section)

            category = category_match.group(1).strip() if category_match else "其他"
            aliases = alias_match.group(1).strip() if alias_match else "无"
            description = desc_match.group(1).strip() if desc_match else ""

            # Extract usage examples (between ```bash and ```)
            usage_examples = []
            usage_blocks = re.findall(r'```bash\n(.*?)```', section, re.DOTALL)
            for block in usage_blocks:
                examples = [line.strip() for line in block.strip().split('\n') if line.strip() and not line.strip().startswith('#')]
                usage_examples.extend(examples)

            # Extract notes (lines starting with -)
            notes = []
            notes_section = re.search(r'\*\*注意事项\*\*:(.*?)(?=\n---|\Z)', section, re.DOTALL)
            if notes_section:
                notes_text = notes_section.group(1)
                notes = [line.strip('- ').strip() for line in notes_text.split('\n') if line.strip().startswith('-')]

            commands[cmd_name] = {
                'category': category,
                'aliases': aliases,
                'description': description,
                'usage': usage_examples if usage_examples else [],
                'notes': notes,
                'raw_section': section
            }

        return commands

    async def run(self):
        # Parse the help file
        commands = self.parse_help_md()

        if not commands:
            print("\n❌ 无法加载帮助文档")
            return False

        if not self.cmd or len(self.cmd) == 0:
            # List all commands by category
            categories = {}
            for cmd_name, cmd_info in sorted(commands.items()):
                cat = cmd_info.get('category', '其他')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(cmd_name)

            print("\n╔══════════════════════════════════════════════════════════════╗")
            print("║                    ICLI 命令完整列表                           ║")
            print("╚══════════════════════════════════════════════════════════════╝\n")

            for cat, cmds in sorted(categories.items()):
                print(f"【{cat}】")
                print(f"  {', '.join(sorted(cmds))}\n")

            print("💡 使用方法:")
            print("  man <命令名>     查看具体命令的详细帮助")
            print("  例如: man buy")
            print("\n  也可以使用: <命令>? 查看帮助")
            print("  例如: buy?\n")
            return True

        # Show specific command help
        cmd = self.cmd[0].lower() if self.cmd else ""

        # Check if command exists
        if cmd not in commands:
            # Try to find command by alias
            found = None
            for cmd_name, cmd_info in commands.items():
                aliases = cmd_info.get('aliases', '无')
                if aliases != '无':
                    alias_list = [a.strip() for a in aliases.split(',')]
                    if cmd in alias_list:
                        found = cmd_name
                        break

            if found:
                cmd = found
            else:
                # Try to find similar command
                similar = [c for c in commands.keys() if cmd in c or c in cmd]
                if similar:
                    print(f"\n❌ 命令 '{self.cmd[0]}' 未找到。\n")
                    print(f"🔍 你是否想查找以下命令？")
                    for s in similar[:5]:
                        print(f"  - {s}")
                    print(f"\n💡 使用 'man' 查看所有可用命令")
                else:
                    print(f"\n❌ 命令 '{self.cmd[0]}' 未找到。")
                    print(f"💡 使用 'man' 查看所有可用命令")
                return False

        info = commands[cmd]

        # Display command help
        print(f"\n╔══════════════════════════════════════════════════════════════╗")
        print(f"║  命令: {cmd:<54} ║")
        print(f"╚══════════════════════════════════════════════════════════════╝\n")

        print(f"📂 分类: {info.get('category', 'N/A')}")

        aliases = info.get('aliases', '无')
        if aliases and aliases != '无':
            print(f"🔗 别名: {aliases}")

        print(f"📝 描述: {info.get('description', 'N/A')}\n")

        usage = info.get('usage', [])
        if usage:
            print("📋 用法示例:")
            for example in usage:
                if example.strip():
                    print(f"  {example}")
            print()

        notes = info.get('notes', [])
        if notes:
            print("📌 注意事项:")
            for note in notes:
                if note.strip():
                    print(f"  • {note}")
            print()

        print("═══════════════════════════════════════════════════════════════\n")
        return True
