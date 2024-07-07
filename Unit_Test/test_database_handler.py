import pytest
from pydantic import ValidationError

# Mocking imports
from unittest.mock import patch, MagicMock

from database_logic.database_handler import InsertData, MySQLHandler, MongoDatabaseHandler

