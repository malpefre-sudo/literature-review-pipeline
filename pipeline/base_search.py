"""
BaseSearch - Clase base abstracta para todos los módulos de búsqueda
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseSearch(ABC):
    """Clase base para todos los buscadores de literatura."""

    def __init__(
        self,
        api_keys: Dict[str, str],
        output_path: Path,
        project_name: str = "review"
    ):
        self.api_keys = api_keys
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.project_name = project_name
        self.results = []
        self.metadata = {
            'source': self.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'query': None,
            'total_results': 0,
            'status': 'pending'
        }

    @abstractmethod
    def search(self, query: str, max_results: int = 100, **kwargs) -> List[Dict]:
        """Ejecuta la búsqueda. Debe implementarse en cada subclase."""
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Verifica que las credenciales necesarias estén presentes."""
        pass

    def save_results(self, filename: Optional[str] = None) -> Path:
        """Guarda los resultados en JSON."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.__class__.__name__.lower()}_{timestamp}.json"

        output_file = self.output_path / filename

        data = {
            'metadata': self.metadata,
            'results': self.results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Resultados guardados en: {output_file}")
        return output_file

    def rate_limit(self, seconds: float = 0.5) -> None:
        """Pausa entre requests para respetar rate limits."""
        time.sleep(seconds)
