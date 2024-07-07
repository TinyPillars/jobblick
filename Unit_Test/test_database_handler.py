import pytest
from pydantic import ValidationError

# Mocking imports
from unittest.mock import patch, MagicMock

from database_logic.database_handler import InsertData, MySQLHandler, MongoDatabaseHandler

#Test InsertDara Validation
def test_insert_data_validation():
	# Test valid data
	valid_data = {
		"username": "testuser1",
		"email": "testuser1@test.com",
		"thread_text": "This is a valid thread text with more than 500 characters" + "a" * 500,
		"Category": "Jobb",
		"company_profile": "Valid-company",
    }
	data = InsertData(**valid_data)
	assert data.username == "testuser1"
	assert data.email == "testuser1@test.com"
	
    # Test Invalid thread text that is to short
	with pytest.raises(ValidationError):
		invalid_data = valid_data.copy()
		invalid_data["thread_text"] = "Too Short"
		InsertData(**invalid_data)
		
    # Test invalid company_profile (in this case, multiple words without hyphen '-')
	with pytest.raises(ValidationError):
		invalid_data = valid_data.copy()
		invalid_data["company:profile"] = "Invalid Company"
		InsertData(**invalid_data)
		


