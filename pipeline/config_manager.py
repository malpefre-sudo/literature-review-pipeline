"""
ConfigManager - Gestión de configuraciones de proyectos de revisión sistemática
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ConfigManager:
    """Gestiona la configuración persistente de proyectos de literatura."""

    def __init__(self, base_path: str = "./literature_reviews"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def list_projects(self) -> List[str]:
        """Lista todos los proyectos existentes."""
        if not self.base_path.exists():
            return []
        return [d.name for d in self.base_path.iterdir() if d.is_dir()]

    def project_exists(self, project_name: str) -> bool:
        """Verifica si un proyecto ya existe."""
        return (self.base_path / project_name).exists()

    def load_project_config(self, project_name: str) -> Optional[Dict]:
        """Carga la configuración de un proyecto."""
        config_path = self.base_path / project_name / "pipeline_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_project_config(self, project_name: str, config: Dict) -> None:
        """Guarda la configuración de un proyecto."""
        config_path = self.base_path / project_name / "pipeline_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def delete_project(self, project_name: str) -> bool:
        """Elimina un proyecto completo."""
        import shutil
        project_path = self.base_path / project_name
        if project_path.exists():
            shutil.rmtree(project_path)
            return True
        return False
