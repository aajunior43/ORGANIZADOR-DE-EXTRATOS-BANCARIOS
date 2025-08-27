#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 Sistema de Backup e Recuperação
Organizador de Extratos Bancários

Sistema robusto para backup automático, versionamento e recuperação de dados.
"""

import os
import sys
import json
import shutil
import hashlib
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time

try:
    from logger_config import get_app_logger
    LOGGER_AVAILABLE = True
except ImportError:
    import logging
    def get_app_logger(name):
        return logging.getLogger(name)
    LOGGER_AVAILABLE = False

class BackupType(Enum):
    """Tipos de backup"""
    FULL = "full"           # Backup completo
    INCREMENTAL = "incremental"  # Apenas arquivos modificados
    DIFFERENTIAL = "differential"  # Modificados desde último full

@dataclass
class BackupInfo:
    """Informações sobre um backup"""
    backup_id: str
    timestamp: str
    backup_type: BackupType
    file_count: int
    total_size: int
    checksum: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['backup_type'] = self.backup_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupInfo':
        data['backup_type'] = BackupType(data['backup_type'])
        return cls(**data)

class BackupManager:
    """Gerenciador de backups"""
    
    def __init__(self, app_data_dir: Optional[Path] = None):
        try:
            self.logger = get_app_logger("backup")
        except Exception:
            import logging
            self.logger = logging.getLogger("backup")
        
        # Configuração de diretórios
        if app_data_dir is None:
            if sys.platform.startswith('win'):
                base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
            else:
                base_dir = os.path.expanduser('~/.config')
            app_data_dir = Path(base_dir) / 'OrganizadorExtratos'
        
        self.backup_dir = app_data_dir / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivo de índice de backups
        self.backup_index_file = self.backup_dir / 'backup_index.json'
        
        # Configurações
        self.max_backups = 10
        self.auto_backup_enabled = True
        self.backup_interval_hours = 24
        
        # Carrega índice existente
        self.backup_index = self._load_backup_index()
        
        # Thread para backup automático
        self.auto_backup_thread = None
        self.stop_auto_backup = threading.Event()
    
    def _load_backup_index(self) -> List[BackupInfo]:
        """Carrega índice de backups"""
        if self.backup_index_file.exists():
            try:
                with open(self.backup_index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [BackupInfo.from_dict(item) for item in data.get('backups', [])]
            except Exception as e:
                self.logger.error(f"Erro ao carregar índice de backups: {e}")
        
        return []
    
    def _save_backup_index(self):
        """Salva índice de backups"""
        try:
            data = {
                'backups': [backup.to_dict() for backup in self.backup_index],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.backup_index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar índice de backups: {e}")
    
    def create_backup(self, 
                     source_paths: List[Path], 
                     backup_type: BackupType = BackupType.FULL,
                     description: str = "") -> Optional[BackupInfo]:
        """
        Cria um backup
        
        Args:
            source_paths: Caminhos para fazer backup
            backup_type: Tipo de backup
            description: Descrição do backup
        
        Returns:
            BackupInfo se sucesso, None se erro
        """
        try:
            # Gera ID único para o backup
            backup_id = self._generate_backup_id()
            timestamp = datetime.now().isoformat()
            
            # Nome do arquivo de backup
            backup_filename = f"backup_{backup_id}_{backup_type.value}.zip"
            backup_path = self.backup_dir / backup_filename
            
            # Cria o arquivo ZIP
            file_count = 0
            total_size = 0
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for source_path in source_paths:
                    if source_path.is_file():
                        # Arquivo individual
                        zipf.write(source_path, source_path.name)
                        file_count += 1
                        total_size += source_path.stat().st_size
                    elif source_path.is_dir():
                        # Diretório recursivo
                        for file_path in source_path.rglob('*'):
                            if file_path.is_file():
                                # Calcula caminho relativo
                                rel_path = file_path.relative_to(source_path.parent)
                                zipf.write(file_path, str(rel_path))
                                file_count += 1
                                total_size += file_path.stat().st_size
            
            # Calcula checksum do backup
            checksum = self._calculate_file_checksum(backup_path)
            
            # Cria informações do backup
            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=timestamp,
                backup_type=backup_type,
                file_count=file_count,
                total_size=total_size,
                checksum=checksum,
                description=description or f"Backup {backup_type.value} automático"
            )
            
            # Adiciona ao índice
            self.backup_index.append(backup_info)
            self._save_backup_index()
            
            # Remove backups antigos se necessário
            self._cleanup_old_backups()
            
            self.logger.info(f"Backup criado: {backup_id} ({file_count} arquivos, {total_size} bytes)")
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            return None
    
    def restore_backup(self, backup_id: str, restore_path: Path) -> bool:
        """
        Restaura um backup
        
        Args:
            backup_id: ID do backup para restaurar
            restore_path: Caminho onde restaurar
        
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Encontra o backup
            backup_info = self._find_backup(backup_id)
            if not backup_info:
                self.logger.error(f"Backup não encontrado: {backup_id}")
                return False
            
            # Caminho do arquivo de backup
            backup_filename = f"backup_{backup_id}_{backup_info.backup_type.value}.zip"
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                self.logger.error(f"Arquivo de backup não encontrado: {backup_path}")
                return False
            
            # Verifica integridade
            if not self._verify_backup_integrity(backup_path, backup_info.checksum):
                self.logger.error(f"Backup corrompido: {backup_id}")
                return False
            
            # Cria diretório de restauração
            restore_path.mkdir(parents=True, exist_ok=True)
            
            # Extrai o backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_path)
            
            self.logger.info(f"Backup restaurado: {backup_id} -> {restore_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup: {e}")
            return False
    
    def list_backups(self) -> List[BackupInfo]:
        """Lista todos os backups disponíveis"""
        return sorted(self.backup_index, key=lambda x: x.timestamp, reverse=True)
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Remove um backup
        
        Args:
            backup_id: ID do backup para remover
        
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Encontra o backup
            backup_info = self._find_backup(backup_id)
            if not backup_info:
                self.logger.error(f"Backup não encontrado: {backup_id}")
                return False
            
            # Remove arquivo
            backup_filename = f"backup_{backup_id}_{backup_info.backup_type.value}.zip"
            backup_path = self.backup_dir / backup_filename
            
            if backup_path.exists():
                backup_path.unlink()
            
            # Remove do índice
            self.backup_index = [b for b in self.backup_index if b.backup_id != backup_id]
            self._save_backup_index()
            
            self.logger.info(f"Backup removido: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao remover backup: {e}")
            return False
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas dos backups"""
        if not self.backup_index:
            return {
                'total_backups': 0,
                'total_size': 0,
                'oldest_backup': None,
                'newest_backup': None,
                'by_type': {}
            }
        
        total_size = sum(b.total_size for b in self.backup_index)
        by_type = {}
        
        for backup in self.backup_index:
            backup_type = backup.backup_type.value
            if backup_type not in by_type:
                by_type[backup_type] = {'count': 0, 'size': 0}
            by_type[backup_type]['count'] += 1
            by_type[backup_type]['size'] += backup.total_size
        
        return {
            'total_backups': len(self.backup_index),
            'total_size': total_size,
            'oldest_backup': min(self.backup_index, key=lambda x: x.timestamp).timestamp,
            'newest_backup': max(self.backup_index, key=lambda x: x.timestamp).timestamp,
            'by_type': by_type
        }
    
    def start_auto_backup(self, source_paths: List[Path]):
        """Inicia backup automático"""
        if self.auto_backup_thread and self.auto_backup_thread.is_alive():
            return
        
        self.stop_auto_backup.clear()
        self.auto_backup_thread = threading.Thread(
            target=self._auto_backup_loop, 
            args=(source_paths,)
        )
        self.auto_backup_thread.daemon = True
        self.auto_backup_thread.start()
        
        self.logger.info("Backup automático iniciado")
    
    def stop_auto_backup(self):
        """Para backup automático"""
        self.stop_auto_backup.set()
        if self.auto_backup_thread:
            self.auto_backup_thread.join(timeout=2.0)
        
        self.logger.info("Backup automático parado")
    
    def _auto_backup_loop(self, source_paths: List[Path]):
        """Loop de backup automático"""
        while not self.stop_auto_backup.wait(self.backup_interval_hours * 3600):
            if self.auto_backup_enabled:
                try:
                    self.create_backup(
                        source_paths, 
                        BackupType.INCREMENTAL,
                        "Backup automático"
                    )
                except Exception as e:
                    self.logger.error(f"Erro no backup automático: {e}")
    
    def _generate_backup_id(self) -> str:
        """Gera ID único para backup"""
        from uuid import uuid4
        return str(uuid4())[:8]
    
    def _find_backup(self, backup_id: str) -> Optional[BackupInfo]:
        """Encontra backup por ID"""
        for backup in self.backup_index:
            if backup.backup_id == backup_id:
                return backup
        return None
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcula checksum MD5 de um arquivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _verify_backup_integrity(self, backup_path: Path, expected_checksum: str) -> bool:
        """Verifica integridade do backup"""
        actual_checksum = self._calculate_file_checksum(backup_path)
        return actual_checksum == expected_checksum
    
    def _cleanup_old_backups(self):
        """Remove backups antigos mantendo apenas os mais recentes"""
        if len(self.backup_index) <= self.max_backups:
            return
        
        # Ordena por timestamp (mais recente primeiro)
        sorted_backups = sorted(self.backup_index, key=lambda x: x.timestamp, reverse=True)
        
        # Remove os mais antigos
        backups_to_remove = sorted_backups[self.max_backups:]
        
        for backup in backups_to_remove:
            self.delete_backup(backup.backup_id)
        
        self.logger.info(f"Limpeza de backups: {len(backups_to_remove)} backups antigos removidos")

# Instância global do backup manager
backup_manager = BackupManager()

if __name__ == "__main__":
    # Teste do sistema de backup
    print("🧪 Testando sistema de backup...")
    
    manager = BackupManager()
    
    # Cria arquivos de teste
    test_dir = Path("test_backup")
    test_dir.mkdir(exist_ok=True)
    
    test_file1 = test_dir / "test1.txt"
    test_file2 = test_dir / "test2.txt"
    
    test_file1.write_text("Conteúdo do arquivo 1", encoding='utf-8')
    test_file2.write_text("Conteúdo do arquivo 2", encoding='utf-8')
    
    # Cria backup
    backup_info = manager.create_backup([test_dir], BackupType.FULL, "Teste de backup")
    
    if backup_info:
        print(f"✅ Backup criado: {backup_info.backup_id}")
        
        # Lista backups
        backups = manager.list_backups()
        print(f"📋 Total de backups: {len(backups)}")
        
        # Testa restauração
        restore_dir = Path("test_restore")
        if manager.restore_backup(backup_info.backup_id, restore_dir):
            print(f"✅ Backup restaurado em: {restore_dir}")
        
        # Mostra estatísticas
        stats = manager.get_backup_stats()
        print(f"📊 Estatísticas: {stats['total_backups']} backups, {stats['total_size']} bytes")
        
        # Remove backup de teste
        manager.delete_backup(backup_info.backup_id)
        print(f"🗑️ Backup de teste removido")
    
    # Limpa arquivos de teste
    shutil.rmtree(test_dir, ignore_errors=True)
    shutil.rmtree("test_restore", ignore_errors=True)
    
    print("✅ Teste concluído!")