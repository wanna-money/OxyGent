"""System monitoring tools for OxyGent agents."""

import asyncio
import json
import platform

import psutil

from oxygent.oxy import FunctionHub

system_tools = FunctionHub(name="system_tools")


@system_tools.tool(
    description="Get system information including OS, architecture, and Python version"
)
async def get_system_info() -> str:
    """Get system information."""
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version(),
        "node": platform.node(),
    }
    return json.dumps(info, ensure_ascii=False)


@system_tools.tool(
    description="Get current system resource usage including CPU, memory, and disk usage"
)
async def get_system_usage() -> str:
    """Get system resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        usage = {
            "cpu_percent": cpu_percent,
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "memory_percent": memory.percent,
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "disk_percent": round(disk.used / disk.total * 100, 2),
        }
        return json.dumps(usage, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def main():
    """
    Main function for testing system tools.
    """
    print("=== System Info Test ===")
    system_info_result = await get_system_info()
    print("System info:")
    print(system_info_result)

    # Convert JSON string to dict for clearer display
    try:
        system_info_dict = json.loads(system_info_result)
        print("\nFormatted system info:")
        for key, value in system_info_dict.items():
            print(f"  {key}: {value}")
    except json.JSONDecodeError:
        print("Failed to parse system info JSON")

    print("\n=== System Resource Usage Test ===")
    usage_result = await get_system_usage()
    print("Resource usage:")
    print(usage_result)

    # Convert JSON string to dict for clearer display
    try:
        usage_dict = json.loads(usage_result)
        print("\nFormatted resource usage:")
        if "error" in usage_dict:
            print(f"Error getting resource usage: {usage_dict['error']}")
        else:
            for key, value in usage_dict.items():
                print(f"  {key}: {value}")
    except json.JSONDecodeError:
        print("Failed to parse resource usage JSON")


if __name__ == "__main__":
    asyncio.run(main())
