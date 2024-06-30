import unittest
from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repository.qr import generate_qr_code, generate_qr_code_with_url
