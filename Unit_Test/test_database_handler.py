import pytest
from pydantic import ValidationError

# Mocking imports
from unittest.mock import patch, MagicMock

from database_logic.database_handler import InsertData, MySQLHandler, MongoDatabaseHandler

#Test InsertDara Validation
def test_insert_data_validation():
    """
    Test the InsertData function for data validation.

    This function tests the following scenarios:
    1. Valid data insertion.
    2. Invalid thread text that is too short.
    3. Invalid company profile format (multiple words without hyphen '-').
    """
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
    
    # Test Invalid thread text that is too short
    with pytest.raises(ValidationError):
        invalid_data = valid_data.copy()
        invalid_data["thread_text"] = "Too Short"
        InsertData(**invalid_data)
        
    # Test invalid company_profile (in this case, multiple words without hyphen '-')
    with pytest.raises(ValidationError):
        invalid_data = valid_data.copy()
        invalid_data["company:profile"] = "Invalid Company"
        InsertData(**invalid_data)



# Test database_handler Methods
@patch('database_handler.MongoClient')
def test_mongo_database_handler(mock_mongo_client):
    mock_db = MagicMock()
    mock_mongo_client.return_value = mock_db

    handler = MongoDatabaseHandler()

    #Test createCompanyProfile
    mock_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_collection.insert_one.return_value.inserted_id = "12345"

    result = handler.createCompanyProfile(org_number="556435-9981")
    assert result == "12345"
    mock_collection.insert_one.assert_called_once()

    # Add more tests for other methods similarly...






