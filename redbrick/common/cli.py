"""Interfaces for RedBrick CLI."""
from abc import ABC, abstractmethod
from typing import Optional
from argparse import Namespace

from redbrick.cli import CLIProject
from redbrick.utils.logging import print_warning


class CLIInputParams(ABC):
    """CLI Input params handler."""

    entity: Optional[str]
    error_message: str

    @abstractmethod
    def filtrator(self, entity: str) -> str:
        """Filter input entity."""

    @abstractmethod
    def validator(self, entity: str) -> bool:
        """Validate input entity."""

    @abstractmethod
    def get(self) -> str:
        """Get filtered entity value post validation."""

    def from_args(self) -> Optional[str]:
        """Get value from cli args."""
        if self.entity is None:
            return None

        if self.validator(self.entity):
            return self.filtrator(self.entity)

        print_warning(self.error_message + " : " + self.entity)
        return None


class CLIConfigInterface(ABC):
    """CLI config command interface."""

    args: Namespace
    project: CLIProject

    LIST = "list"
    SET = "set"
    ADD = "add"
    REMOVE = "remove"
    CLEAR = "clear"
    VERIFY = "verify"

    @abstractmethod
    def handler(self, args: Namespace) -> None:
        """Handle config command."""

    @abstractmethod
    def handle_config(self) -> None:
        """Handle empty sub command."""

    @abstractmethod
    def handle_list(self) -> None:
        """Handle list sub command."""

    @abstractmethod
    def handle_set(self) -> None:
        """Handle set sub command."""

    @abstractmethod
    def handle_add(self, set_default: bool = False) -> None:
        """Handle add sub command."""

    @abstractmethod
    def handle_remove(self) -> None:
        """Handle remove sub command."""

    @abstractmethod
    def handle_clear(self) -> None:
        """Handle clear sub command."""

    @abstractmethod
    def handle_verify(self, profile: Optional[str] = None) -> None:
        """Handle verify sub command."""


class CLIInitInterface(ABC):
    """CLI init interface."""

    args: Namespace
    project: CLIProject

    @abstractmethod
    def handler(self, args: Namespace) -> None:
        """Handle init command."""

    @abstractmethod
    def handle_init(self) -> None:
        """Handle empty sub command."""


class CLICloneInterface(ABC):
    """CLI clone interface."""

    args: Namespace
    project: CLIProject

    @abstractmethod
    def handler(self, args: Namespace) -> None:
        """Handle clone command."""

    @abstractmethod
    def handle_clone(self) -> None:
        """Handle empty sub command."""


class CLIInfoInterface(ABC):
    """CLI info interface."""

    args: Namespace
    project: CLIProject

    @abstractmethod
    def handler(self, args: Namespace) -> None:
        """Handle info command."""

    @abstractmethod
    def handle_info(self) -> None:
        """Handle empty sub command."""


class CLIExportInterface(ABC):
    """CLI export interface."""

    args: Namespace
    project: CLIProject

    TYPE_LATEST = "latest"
    TYPE_GROUNDTRUTH = "groundtruth"

    FORMAT_REDBRICK = "redbrick"
    FORMAT_COCO = "coco"

    @abstractmethod
    def handler(self, args: Namespace) -> None:
        """Handle export command."""

    @abstractmethod
    def handle_export(self) -> None:
        """Handle empty sub command."""


class CLIInterface(ABC):
    """Main CLI Interface."""

    config: CLIConfigInterface
    init: CLIInitInterface
    clone: CLICloneInterface
    info: CLIInfoInterface
    export: CLIExportInterface

    CONFIG = "config"
    INIT = "init"
    CLONE = "clone"
    INFO = "info"
    EXPORT = "export"

    @abstractmethod
    def handle_command(self, args: Namespace) -> None:
        """CLI command main handler."""
