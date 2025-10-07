import importlib
import importlib.util
import sys
import os
from typing import Dict, List, Any
from fastapi import FastAPI, APIRouter
import logging
from .config import settings

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """Registry for managing modular features"""

    def __init__(self):
        self.modules: Dict[str, Any] = {}
        self.enabled_modules: Dict[str, bool] = {}
        self.routers: List[APIRouter] = []
        self.background_tasks: List[Any] = []

    async def initialize(self):
        """Initialize all enabled modules"""
        # Load module configuration
        modules_config = settings.load_modules_config()
        modules = modules_config.get("modules", {})

        # Add modules directory to Python path
        modules_path = os.path.join(os.path.dirname(__file__), "..", "modules")
        modules_path = os.path.abspath(modules_path)
        if modules_path not in sys.path:
            sys.path.append(modules_path)
            logger.info(f"Added modules path to Python path: {modules_path}")

        # Add /app to sys.path to allow "modules.core_auth" style imports
        app_path = os.path.join(os.path.dirname(__file__), "..")
        app_path = os.path.abspath(app_path)
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
            logger.info(f"Added app path to Python path: {app_path}")

        # Initialize each enabled module
        for module_name, module_config in modules.items():
            if module_config.get("enabled", False):
                await self._load_module(module_name, module_config)

        logger.info(f"Initialized {len(self.modules)} modules")

    async def _load_module(self, module_name: str, config: dict):
        """Load a specific module"""
        try:
            # Import the module - handle dots in module names
            module_dir = module_name  # Keep original name for directory

            # Get the full path to the main.py file
            module_path = os.path.join(os.path.dirname(__file__), "..", "modules", module_dir, "main.py")
            module_path = os.path.abspath(module_path)

            # Load the module using importlib.util
            spec = importlib.util.spec_from_file_location(f"{module_name}.main", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Initialize the module if it has an init function
            logger.info(f"Module {module_name} has init_module: {hasattr(module, 'init_module')}")

            if hasattr(module, "init_module"):
                logger.info(f"Initializing module: {module_name}")
                module_instance = await module.init_module(config)
                self.modules[module_name] = module_instance

                # Register router if available
                if hasattr(module_instance, "router"):
                    self.routers.append(module_instance.router)
                    logger.info(f"Registered router for module: {module_name}")

                # Register background tasks if available
                if hasattr(module_instance, "background_tasks"):
                    self.background_tasks.extend(module_instance.background_tasks)
                    logger.info(f"Registered background tasks for module: {module_name}")
            else:
                logger.warning(f"Module {module_name} does not have init_module function")

            self.enabled_modules[module_name] = True
            logger.info(f"Loaded module: {module_name}")

        except Exception as e:
            logger.error(f"Failed to load module {module_name}: {str(e)}")
            self.enabled_modules[module_name] = False

    def register_routers(self, app: FastAPI):
        """Register all module routers with the FastAPI app"""
        for router in self.routers:
            app.include_router(router, prefix="/api/v1")
            logger.info(f"Registered router: {router.prefix}")

    def is_module_enabled(self, module_name: str) -> bool:
        """Check if a module is enabled"""
        return self.enabled_modules.get(module_name, False)

    def get_module(self, module_name: str) -> Any:
        """Get a loaded module instance"""
        return self.modules.get(module_name)

    async def cleanup(self):
        """Cleanup all modules"""
        for module_name, module_instance in self.modules.items():
            if hasattr(module_instance, "cleanup"):
                try:
                    await module_instance.cleanup()
                    logger.info(f"Cleaned up module: {module_name}")
                except Exception as e:
                    logger.error(f"Error cleaning up module {module_name}: {str(e)}")


# Global module registry instance
module_registry = ModuleRegistry()