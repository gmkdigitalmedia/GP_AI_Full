"""
File System MCP Server
Provides file operations like read, write, list, search
"""

import os
import glob
from pathlib import Path
from mcp_base import MCPServer

class FileSystemServer(MCPServer):
    def __init__(self, workspace_dir="./workspace"):
        super().__init__("filesystem", "File system operations server")
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)

    def _register_tools(self):
        """Register file system tools"""

        # Read file tool
        self.add_tool(
            "read_file",
            "Read contents of a file",
            {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of file to read"}
                },
                "required": ["filename"]
            },
            self._read_file
        )

        # Write file tool
        self.add_tool(
            "write_file",
            "Write content to a file",
            {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of file to write"},
                    "content": {"type": "string", "description": "Content to write to file"}
                },
                "required": ["filename", "content"]
            },
            self._write_file
        )

        # List files tool
        self.add_tool(
            "list_files",
            "List files in workspace directory",
            {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Optional glob pattern to filter files"}
                },
                "required": []
            },
            self._list_files
        )

        # Search in files tool
        self.add_tool(
            "search_files",
            "Search for text within files",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text to search for"},
                    "file_pattern": {"type": "string", "description": "File pattern to search in (default: *.txt)"}
                },
                "required": ["query"]
            },
            self._search_files
        )

        # Delete file tool
        self.add_tool(
            "delete_file",
            "Delete a file from workspace",
            {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of file to delete"}
                },
                "required": ["filename"]
            },
            self._delete_file
        )

    def _read_file(self, filename: str) -> str:
        """Read file contents"""
        file_path = self.workspace_dir / filename

        if not file_path.exists():
            return f"Error: File '{filename}' does not exist"

        if not file_path.is_file():
            return f"Error: '{filename}' is not a file"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"File '{filename}' contents:\n{content}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def _write_file(self, filename: str, content: str) -> str:
        """Write content to file"""
        file_path = self.workspace_dir / filename

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to '{filename}'"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def _list_files(self, pattern: str = "*") -> str:
        """List files in workspace"""
        try:
            files = list(self.workspace_dir.glob(pattern))
            if not files:
                return f"No files found matching pattern '{pattern}'"

            file_list = []
            for file_path in files:
                if file_path.is_file():
                    size = file_path.stat().st_size
                    file_list.append(f"{file_path.name} ({size} bytes)")
                elif file_path.is_dir():
                    file_list.append(f"{file_path.name}/ (directory)")

            return f"Files in workspace:\n" + "\n".join(file_list)
        except Exception as e:
            return f"Error listing files: {str(e)}"

    def _search_files(self, query: str, file_pattern: str = "*.txt") -> str:
        """Search for text in files"""
        try:
            results = []
            files = list(self.workspace_dir.glob(file_pattern))

            if not files:
                return f"No files found matching pattern '{file_pattern}'"

            for file_path in files:
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()

                        for line_num, line in enumerate(lines, 1):
                            if query.lower() in line.lower():
                                results.append(f"{file_path.name}:{line_num}: {line.strip()}")
                    except:
                        continue

            if not results:
                return f"No matches found for '{query}' in {file_pattern} files"

            return f"Search results for '{query}':\n" + "\n".join(results)
        except Exception as e:
            return f"Error searching files: {str(e)}"

    def _delete_file(self, filename: str) -> str:
        """Delete a file"""
        file_path = self.workspace_dir / filename

        if not file_path.exists():
            return f"Error: File '{filename}' does not exist"

        if not file_path.is_file():
            return f"Error: '{filename}' is not a file"

        try:
            file_path.unlink()
            return f"Successfully deleted file '{filename}'"
        except Exception as e:
            return f"Error deleting file: {str(e)}"