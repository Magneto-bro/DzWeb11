import unittest

from unittest.mock import MagicMock, patch

from src.contacts_api import crud,models,schemas

class TestContacts(unittest.TestCase):
    def setUp(self):
        self.db_mock = MagicMock()
        self.fake_user = MagicMock()
        self.fake_user.id = 1

       
        self.contact_data = schemas.ContactCreate(
            name="John",
            email="john@example.com",
            phone="1234567890",
            birthday=None,
            about="Test"
        )

        self.update_data = schemas.ContactCreate(
            name="Updated Name",
            email="updated@example.com",
            phone="9876543210",
            birthday=None,
            about="Updated about"
        )
    def test_create_contact(self,):
   
        result = crud.create_contact(self.contact_data,self.db_mock,self.fake_user)

        self.db_mock.add.assert_called_once()
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once_with(result)

        self.assertEqual(result.name,"John")
        self.assertEqual(result.email,"john@example.com")

    def test_get_contact(self):
        self.db_mock.query.return_value.filter.return_value.first.return_value = self.fake_user

        result = crud.get_contact(self.db_mock, 1)
        
        self.db_mock.query.assert_called_once_with(models.Contacts)
        self.db_mock.query.return_value.filter.assert_called()
        self.db_mock.query.return_value.filter.return_value.first.assert_called_once()
    
    def test_update_contact(self):
        self.db_mock.query.return_value.filter.return_value.first.return_value = self.fake_user

        result = crud.update_contact(self.db_mock,contact_id=1,contact=self.update_data)


        for key ,value in self.update_data.dict().items():
            self.assertEqual(getattr(self.fake_user,key),value)
        
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once_with(self.fake_user)

        self.assertEqual(result,self.fake_user)
    def test_delete_contact(self):
        self.db_mock.query.return_value.filter.return_value.first.return_value =self.fake_user

        result = crud.delete_contact(self.db_mock,contact_id=1)

        self.db_mock.query.assert_called_once_with(models.Contacts)
        self.db_mock.query.return_value.filter.assert_called()
        self.db_mock.query.return_value.filter.return_value.first.assert_called_once()
        self.assertEqual(result,self.fake_user)

if __name__ == "__main__":
    unittest.main()
    